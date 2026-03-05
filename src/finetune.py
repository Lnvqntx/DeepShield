import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import os
import yaml
from src.classifier import DeepfakeDetector
from src.data_loader import get_dataloaders
from src.train import train_one_epoch, evaluate, compute_eer
from src.evaluate import plot_accuracy_comparison

def unfreeze_top_n_layers(model, n=4):
    """
    Unfreeze the top n transformer layers of wav2vec2.
    Keeps feature extractor and lower layers frozen.
    
    Args:
        model: wav2vec2 model with classifier head
        n: number of top transformer layers to unfreeze
        
    Returns:
        count of trainable parameters
    """
    trainable_params = 0
    layer_table = []
    
    # Freeze feature extractor
    for param in model.wav2vec2.feature_extractor.parameters():
        param.requires_grad = False
    
    # Freeze encoder layers except top n
    encoder = model.wav2vec2.encoder
    if hasattr(encoder, "layers"):
        total_layers = len(encoder.layers)
        for i, layer in enumerate(encoder.layers):
            if i >= total_layers - n:
                for param in layer.parameters():
                    param.requires_grad = True
                trainable_params += sum(p.numel() for p in layer.parameters())
                layer_table.append((f"layer_{i}", True, sum(p.numel() for p in layer.parameters())))
            else:
                for param in layer.parameters():
                    param.requires_grad = False
                layer_table.append((f"layer_{i}", False, sum(p.numel() for p in layer.parameters())))
    
    # Freeze classifier head if not already trainable
    for param in model.classifier.parameters():
        param.requires_grad = True  # Classifier is always trainable
    
    # Print table
    print("=== Layer Freeze Status ===")
    print(f"{'Layer':<10} | {'Trainable':<10} | {'Params':<10}")
    for layer_name, trainable, count in layer_table:
        print(f"{layer_name:<10} | {str(trainable):<10} | {count:<10}")
    
    return trainable_params

def run_finetuning():
    """
    Execute three-phase fine-tuning for multilingual model.
    """
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Phase 1: Freeze all layers except classifier
    print("\n=== PHASE 1: Full Freeze ===")
    model = DeepfakeDetector()
    model.load_state_dict(torch.load("models/baseline/best.pt"))
    model.freeze_all_layers()
    
    # Combine Hindi and Telugu data
    train_loader, val_loader = get_dataloaders(config["data"], batch_size=16, lang="all")
    
    # Setup optimizer
    optimizer = optim.Adam(model.classifier.parameters(), lr=1e-3)
    
    # Training loop
    for epoch in range(3):
        train_one_epoch(model, train_loader, optimizer, epoch, "Phase 1")
        acc, eer = evaluate(model, val_loader)
        print(f"Epoch {epoch+1} | Val Acc: {acc:.2%} | EER: {eer:.2%}")
    
    # Phase 2: Unfreeze top 4 layers
    print("\n=== PHASE 2: Unfreeze Top 4 Layers ===")
    model.load_state_dict(torch.load("models/baseline/best.pt"))
    trainable_params = unfreeze_top_n_layers(model, n=4)
    
    # Setup optimizer with lower learning rate
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4)
    
    # Training loop
    best_val_acc = 0
    for epoch in range(4, 8):
        train_one_epoch(model, train_loader, optimizer, epoch, "Phase 2")
        acc, eer = evaluate(model, val_loader)
        print(f"Epoch {epoch+1} | Val Acc: {acc:.2%} | EER: {eer:.2%}")
        
        # Save best checkpoint
        if acc > best_val_acc:
            best_val_acc = acc
            os.makedirs("models/indian_finetuned", exist_ok=True)
            torch.save(model.state_dict(), "models/indian_finetuned/best.pt")
    
    # Phase 3: Conditional full unfreeze
    print("\n=== PHASE 3: Conditional Full Unfreeze ===")
    if best_val_acc < 0.8:
        try:
            model.load_state_dict(torch.load("models/indian_finetuned/best.pt"))
            model.unfreeze_all_layers()
            
            # Enable gradient checkpointing
            model.wav2vec2.encoder.apply(torch.utils.checkpoint.checkpoint)
            
            # Setup optimizer with smaller batch size
            optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=5e-5)
            
            # Training loop
            for epoch in range(3):
                train_one_epoch(model, train_loader, optimizer, epoch, "Phase 3")
                acc, eer = evaluate(model, val_loader)
                print(f"Epoch {epoch+1} | Val Acc: {acc:.2%} | EER: {eer:.2%}")
                
        except RuntimeError as e:
            print("CUDA OOM detected. Suggestion: Reduce batch size or use mixed precision training.")
            exit(1)

def compare_models():
    """
    Compare baseline and finetuned models on test sets.
    """
    # Load test data
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Load models
    model_baseline = DeepfakeDetector()
    model_baseline.load_state_dict(torch.load("models/baseline/best.pt"))
    
    model_finetuned = DeepfakeDetector()
    model_finetuned.load_state_dict(torch.load("models/indian_finetuned/best.pt"))
    
    # Prepare test loaders
    test_loaders = {
        "hindi": get_dataloaders(config["data"], batch_size=16, lang="hi"),
        "telugu": get_dataloaders(config["data"], batch_size=16, lang="te")
    }
    
    # Evaluate models
    results = {}
    for name, (test_loader, _) in test_loaders.items():
        acc_baseline, _ = evaluate(model_baseline, test_loader)
        acc_finetuned, _ = evaluate(model_finetuned, test_loader)
        results[name] = {
            "Baseline Acc": acc_baseline,
            "Our Model Acc": acc_finetuned,
            "Improvement": acc_finetuned - acc_baseline
        }
    
    # Print comparison table
    print("\n=== Model Comparison ===")
    print(f"{'Dataset':<10} | {'Baseline Acc':<12} | {'Our Model Acc':<12} | {'Improvement':<10}")
    for name, data in results.items():
        print(f"{name:<10} | {data['Baseline Acc']:.2%} | {data['Our Model Acc']:.2%} | {data['Improvement']:.2%} ✅")
    
    # Generate comparison plot
    plot_accuracy_comparison(results, "models/indian_finetuned/accuracy_comparison.png")

if __name__ == "__main__":
    try:
        run_finetuning()
        compare_models()
    except RuntimeError as e:
        print("Training failed with error:", e)
        print("Suggestion: Reduce batch size or use mixed precision training.")
