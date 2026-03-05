import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
from sklearn.metrics import f1_score, precision_score, recall_score
from tqdm import tqdm
import numpy as np
import json
import os
from pathlib import Path

from classifier import DeepfakeDetector
from data_loader import get_dataloaders


def train_one_epoch(model, loader, optimizer, criterion, device, scaler):
    """Trains the model for one epoch with gradient accumulation and mixed precision."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    progress_bar = tqdm(loader, desc="Training", leave=False)

    optimizer.zero_grad()

    for batch_idx, (inputs, labels) in enumerate(progress_bar):
        inputs, labels = inputs.to(device), labels.to(device)

        with autocast():
            outputs = model(inputs)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()

        if (batch_idx + 1) % 4 == 0:
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()

        total_loss += loss.item() * inputs.size(0)
        predicted = torch.argmax(outputs, dim=1)
        correct += (predicted == labels).sum().item()
        total += labels.size(0)

        progress_bar.set_postfix(loss=loss.item(), accuracy=(correct / total) * 100)

    avg_loss = total_loss / total
    accuracy = correct / total

    return avg_loss, accuracy


def evaluate(model, loader, criterion, device):
    """Evaluates the model on validation/test data."""
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    all_scores = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in loader:

            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)

            loss = criterion(outputs, labels)

            total_loss += loss.item() * inputs.size(0)

            predicted = torch.argmax(outputs, dim=1)

            correct += (predicted == labels).sum().item()
            total += labels.size(0)

            scores = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()

            all_scores.extend(scores)
            all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / total
    accuracy = correct / total

    preds = [1 if s >= 0.5 else 0 for s in all_scores]

    f1 = f1_score(all_labels, preds)
    precision = precision_score(all_labels, preds)
    recall = recall_score(all_labels, preds)

    return {
        "loss": avg_loss,
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "scores": all_scores,
        "labels": all_labels
    }


def compute_eer(scores, labels):
    """
    Computes Equal Error Rate (EER).

    EER is the point where False Acceptance Rate (FAR)
    equals False Rejection Rate (FRR). In deepfake detection
    lower EER means better spoof detection performance.
    """

    scores = np.array(scores)
    labels = np.array(labels)

    thresholds = np.linspace(0, 1, 101)

    eer = 1.0

    for t in thresholds:

        predicted = scores >= t

        far = np.sum((predicted == 1) & (labels == 0)) / np.sum(labels == 0)
        frr = np.sum((predicted == 0) & (labels == 1)) / np.sum(labels == 1)

        if abs(far - frr) < abs(eer - 0.5):
            eer = (far + frr) / 2

    return eer


def run_training():
    """Main training loop."""

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = DeepfakeDetector().to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        weight_decay=0.01
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=10
    )

    data_config = {
        "data_dir": "data/",
        "batch_size": 16,
        "sample_rate": 16000,
        "max_length": 32000,
        "train_split": 0.8
}
    data_config = {
        "data_dir": "data/",
        "batch_size": 16,
        "sample_rate": 16000,
        "max_length": 32000,
        "train_split": 0.8
    }
    
    train_loader, val_loader, test_loader = get_dataloaders(data_config)

    real_count = 0
    fake_count = 0

    for _, labels in train_loader:

        real_count += (labels == 0).sum().item()
        fake_count += (labels == 1).sum().item()

    class_weights = torch.tensor(
        [
            real_count / (real_count + fake_count),
            fake_count / (real_count + fake_count)
        ],
        device=device
    )

    criterion = nn.CrossEntropyLoss(weight=class_weights)

    scaler = GradScaler()

    best_eer = float("inf")

    history = []

    try:

        for epoch in range(10):

            train_loss, train_acc = train_one_epoch(
                model,
                train_loader,
                optimizer,
                criterion,
                device,
                scaler
            )

            val_metrics = evaluate(
                model,
                val_loader,
                criterion,
                device
            )

            val_loss = val_metrics["loss"]
            val_acc = val_metrics["accuracy"]

            eer = compute_eer(
                val_metrics["scores"],
                val_metrics["labels"]
            )

            history.append({
                "epoch": epoch + 1,
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "eer": eer
            })

            if eer < best_eer:

                best_eer = eer

                torch.save(
                    model.state_dict(),
                    "best_model.pth"
                )

                print(f"Epoch {epoch+1}: EER improved to {best_eer:.4f}")

            print(
                f"Epoch {epoch+1}: "
                f"Train Loss={train_loss:.4f}, "
                f"Val Loss={val_loss:.4f}, "
                f"EER={eer:.4f}"
            )

            scheduler.step()

        model.load_state_dict(torch.load("best_model.pth"))

        final_metrics = evaluate(
            model,
            test_loader,
            criterion,
            device
        )

        final_eer = compute_eer(
            final_metrics["scores"],
            final_metrics["labels"]
        )

        print(f"\nFinal Test EER: {final_eer:.4f}")
        print(f"Final Test Accuracy: {final_metrics['accuracy']:.4f}")

        with open("training_history.json", "w") as f:
            json.dump(history, f)

    except RuntimeError as e:

        if "CUDA out of memory" in str(e):
            print("CUDA OOM: Reduce batch size or sequence length.")
        else:
            print(f"Training failed: {e}")


if __name__ == "__main__":
    run_training()