import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import sklearn.metrics
from sklearn.metrics import confusion_matrix
from tabulate import tabulate
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from classifier import DeepfakeClassifier
from data_loader import get_dataloaders
from train import compute_eer


def load_and_evaluate(checkpoint_path, batch_size=32):
    device = "cpu"
    model = DeepfakeClassifier()
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()

    _, val_loader = get_dataloaders(batch_size=batch_size, cache_path="data/embeddings_cache.pt")

    all_labels, all_scores, all_preds = [], [], []

    with torch.no_grad():
        for inputs, labels in val_loader:
            outputs = model(inputs)
            scores = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
            preds = [1 if s >= 0.5 else 0 for s in scores]
            all_labels.extend(labels.numpy())
            all_scores.extend(scores)
            all_preds.extend(preds)

    accuracy  = sklearn.metrics.accuracy_score(all_labels, all_preds)
    f1        = sklearn.metrics.f1_score(all_labels, all_preds, zero_division=0)
    precision = sklearn.metrics.precision_score(all_labels, all_preds, zero_division=0)
    recall    = sklearn.metrics.recall_score(all_labels, all_preds, zero_division=0)
    eer       = compute_eer(all_scores, all_labels)

    return {
        "accuracy": accuracy, "f1": f1, "eer": eer,
        "precision": precision, "recall": recall,
        "all_labels": all_labels, "all_preds": all_preds, "all_scores": all_scores,
    }


def plot_confusion_matrix(labels, preds, title, save_path):
    os.makedirs("results", exist_ok=True)
    cm = confusion_matrix(labels, preds)
    cm_df = pd.DataFrame(cm, index=["REAL", "FAKE"], columns=["REAL", "FAKE"])
    plt.figure(figsize=(6, 6))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print("Saved " + save_path)


def run_full_evaluation(checkpoint_path="models/best_classifier.pt"):
    os.makedirs("results", exist_ok=True)
    print("Evaluating " + checkpoint_path + "...")
    results = load_and_evaluate(checkpoint_path)

    table_data = [
        ["Accuracy",  str(round(results['accuracy']*100, 1)) + "%"],
        ["F1 Score",  str(round(results['f1'], 4))],
        ["Precision", str(round(results['precision'], 4))],
        ["Recall",    str(round(results['recall'], 4))],
        ["EER",       str(round(results['eer']*100, 2)) + "%"],
    ]
    print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

    plot_confusion_matrix(
        results["all_labels"], results["all_preds"],
        "Confusion Matrix",
        "results/confusion_matrix.png"
    )
    print("Done! Results saved to results/")


if __name__ == "__main__":
    run_full_evaluation()
