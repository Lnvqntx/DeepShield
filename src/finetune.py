import torch
import torch.nn as nn
import torch.optim as optim
import os
import sys
from torch.cuda.amp import GradScaler
sys.path.insert(0, os.path.dirname(__file__))
from classifier import DeepfakeClassifier
from data_loader import get_dataloaders
from train import train_one_epoch, evaluate, compute_eer
def run_finetuning():
    os.makedirs("models", exist_ok=True)
    device = torch.device("cpu")
    print("Using device: cpu")
    baseline_path = "models/best_classifier.pt"
    if not os.path.exists(baseline_path):
        raise FileNotFoundError("Run train.py first.")
    train_loader, val_loader = get_dataloaders(
        batch_size=32,
        cache_path="data/embeddings_cache.pt"
    )
    model = DeepfakeClassifier().to(device)
    model.load_state_dict(torch.load(baseline_path, map_location=device))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=5e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5)
    scaler = GradScaler()
    best_eer = float("inf")
    for epoch in range(5):
        loss, acc = train_one_epoch(model, train_loader, optimizer, criterion, device, scaler)
        metrics = evaluate(model, val_loader, criterion, device)
        eer = compute_eer(metrics["scores"], metrics["labels"])
        print(f"Epoch {epoch+1} | Loss {loss:.4f} | Val Acc {metrics['accuracy']*100:.1f}% | EER {eer*100:.2f}%")
        if eer < best_eer:
            best_eer = eer
            torch.save(model.state_dict(), "models/finetuned.pt")
            print(f"  Saved best (EER {best_eer*100:.2f}%)")
        scheduler.step()
    print(f"Done! Best EER: {best_eer*100:.2f}%")
    print("Model saved to models/finetuned.pt")
if __name__ == "__main__":
    run_finetuning()
