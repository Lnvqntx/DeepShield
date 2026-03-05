import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import librosa
import librosa.display
import sklearn.metrics
import tabulate
from tabulate import tabulate
from sklearn.metrics import confusion_matrix

def load_and_evaluate(checkpoint_path, data_config, batch_size=16):
    """
    Load a trained model from checkpoint and evaluate on test set.

    Args:
        checkpoint_path (str): Path to model checkpoint
        data_config (dict): Configuration for data loading
        batch_size (int): Batch size for evaluation

    Returns:
        dict: Evaluation metrics including accuracy, F1, EER, precision, recall,
              along with all labels, predictions, and scores
    """
    # Load model
    model = DeepfakeDetector().to("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()

    # Load test data
    _, _, test_loader = get_dataloaders(data_config)

    # Evaluate
    all_labels = []
    all_scores = []
    all_preds = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to("cuda" if torch.cuda.is_available() else "cpu"), labels.to("cpu")
            outputs = model(inputs)
            scores = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
            preds = [1 if s >= 0.5 else 0 for s in scores]
            all_labels.extend(labels.numpy())
            all_scores.extend(scores)
            all_preds.extend(preds)

    # Calculate metrics
    accuracy = sklearn.metrics.accuracy_score(all_labels, all_preds)
    f1 = sklearn.metrics.f1_score(all_labels, all_preds)
    precision = sklearn.metrics.precision_score(all_labels, all_preds)
    recall = sklearn.metrics.recall_score(all_labels, all_preds)
    eer = compute_eer(all_scores, all_labels)

    return {
        "accuracy": accuracy,
        "f1": f1,
        "eer": eer,
        "precision": precision,
        "recall": recall,
        "all_labels": all_labels,
        "all_preds": all_preds,
        "all_scores": all_scores
    }

def plot_confusion_matrix(labels, preds, title, save_path):
    """
    Plot confusion matrix with counts and percentages.

    Args:
        labels (list): True labels
        preds (list): Predicted labels
        title (str): Title of the plot
        save_path (str): Path to save the plot
    """
    cm = confusion_matrix(labels, preds)
    cm_df = pd.DataFrame(cm, index=["AI FAKE", "REAL VOICE"], columns=["AI FAKE", "REAL VOICE"])

    # Calculate percentages
    total_samples = len(labels)
    cm_percent = cm_df.apply(lambda x: x / total_samples * 100).round(1)

    # Create combined annotations
    annotations = [[f"{cm_df.iloc[i, j]} ({cm_percent.iloc[i, j]:.1f}%)" for j in range(2)] for i in range(2)]

    plt.figure(figsize=(6, 6))
    sns.heatmap(cm_df, annot=annotations, fmt="", cmap="Blues", cbar=False,
                xticklabels=["AI FAKE", "REAL VOICE"], yticklabels=["AI FAKE", "REAL VOICE"])

    # Formatting
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

def plot_accuracy_comparison(results_dict, save_path):
    """
    Plot grouped bar chart comparing model accuracies.

    Args:
        results_dict (dict): Dictionary of model names and accuracies
        save_path (str): Path to save the plot
    """
    # Extract data
    models = list(results_dict.keys())
    accuracies = list(results_dict.values())

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = np.arange(len(models))

    # Create bars
    bars = ax.bar(index, accuracies, width=bar_width, color=["green" if acc >= 0.75 else "red" for acc in accuracies])

    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f"{yval*100:.1f}%", ha="center", va="bottom")

    # Formatting
    ax.set_title("Accuracy: Existing Approach vs Our Fine-Tuned Model")
    ax.set_ylabel("Accuracy")
    ax.set_xticks(index)
    ax.set_xticklabels(models, rotation=0)
    ax.axhline(0.75, color="gray", linestyle="--", label="Minimum Acceptable")
    ax.legend()
    ax.set_ylim(0, 1.1)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.set_yticklabels([f"{i*100:.0f}%" for i in np.arange(0, 1.1, 0.1)])
    ax.grid(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

def plot_spectrogram_comparison(real_audio_path, fake_audio_path, save_path):
    """
    Plot side-by-side mel spectrograms of real and fake audio.

    Args:
        real_audio_path (str): Path to real audio file
        fake_audio_path (str): Path to fake audio file
        save_path (str): Path to save the plot
    """
    # Load audio files
    real_audio, sr = librosa.load(real_audio_path, sr=None)
    fake_audio, sr = librosa.load(fake_audio_path, sr=None)

    # Compute mel spectrograms
    real_mel = librosa.feature.melspectrogram(y=real_audio, sr=sr, n_mels=128, fmax=8000)
    fake_mel = librosa.feature.melspectrogram(y=fake_audio, sr=sr, n_mels=128, fmax=8000)

    # Convert to dB scale
    real_db = librosa.power_to_db(real_mel, ref=np.max)
    fake_db = librosa.power_to_db(fake_mel, ref=np.max)

    # Plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    img1 = librosa.display.specshow(real_db, x_axis="time", y_axis="mel", ax=ax[0], cmap="viridis")
    img2 = librosa.display.specshow(fake_db, x_axis="time", y_axis="mel", ax=ax[1], cmap="viridis")

    # Formatting
    ax[0].set_title("Real Audio")
    ax[1].set_title("Fake Audio")
    ax[0].set_xlabel("Time (s)")
    ax[1].set_xlabel("Time (s)")
    ax[0].set_ylabel("Frequency (Hz)")
    ax[1].set_ylabel("Frequency (Hz)")

    # Colorbar
    fig.colorbar(img1, ax=ax[0], orientation="vertical")
    fig.colorbar(img2, ax=ax[1], orientation="vertical")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

def run_full_evaluation():
    """
    Run full evaluation and generate all plots and tables.
    """
    # Configuration
    checkpoints = [
        ("models/real_model.pth", "Real Model"),
        ("models/fake_model.pth", "Fake Model"),
        ("models/combined_model.pth", "Combined Model")
    ]

    # Evaluate models
    results = []
    for path, name in checkpoints:
        result = load_and_evaluate(path, data_config)
        result["model"] = name
        results.append(result)

    # Generate plots
    plot_confusion_matrix(
        results[0]["all_labels"],
        results[0]["all_preds"],
        f"Confusion Matrix - {results[0]['model']}",
        "results/confusion_matrix.png"
    )

    plot_accuracy_comparison({
        "Real Model": results[0]["accuracy"],
        "Fake Model": results[1]["accuracy"],
        "Combined Model": results[2]["accuracy"]
    }, "results/accuracy_comparison.png")

    plot_spectrogram_comparison(
        "data/real_audio.wav",
        "data/fake_audio.wav",
        "results/spectrogram_comparison.png"
    )

    # Generate table
    table_data = [
        [r["model"], f"{r['accuracy']*100:.1f}%", f"{r['f1']*100:.1f}%", f"{r['eer']*100:.1f}%",
         f"{r['precision']*100:.1f}%", f"{r['recall']*100:.1f}%"]
        for r in results
    ]

    headers = ["Model", "Accuracy", "F1 Score", "EER", "Precision", "Recall"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Example usage
if __name__ == "__main__":
    run_full_evaluation()
