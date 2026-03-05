import os
import warnings
import numpy as np
import librosa
import torch
import torch.utils.data
import matplotlib.pyplot as plt

class AudioDataset(torch.utils.data.Dataset):
    def __init__(self, folder_path, label):
        self.folder_path = folder_path
        self.label = label
        self.files = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.flac')):
                    file_path = os.path.join(root, file)
                    try:
                        waveform, sr = librosa.load(file_path, sr=16000, mono=True)
                        if sr != 16000:
                            raise ValueError(f"Sample rate {sr} is not 16000 for file {file_path}")
                        if len(waveform) == 0:
                            raise ValueError(f"Empty waveform for file {file_path}")
                        self.files.append(file_path)
                    except Exception as e:
                        warnings.warn(f"Skipping file {file_path} due to error: {e}")

        if not self.files:
            warnings.warn(f"No valid files found in {folder_path}")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        file_path = self.files[idx]
        waveform, sr = librosa.load(file_path, sr=16000, mono=True)
        if sr != 16000:
            raise ValueError(f"Sample rate {sr} is not 16000 for file {file_path}")
        if len(waveform) < 64000:
            waveform = np.pad(waveform, (0, 64000 - len(waveform)), mode='constant')
        else:
            waveform = waveform[:64000]
        waveform_tensor = torch.tensor(waveform, dtype=torch.float32).unsqueeze(0)
        return waveform_tensor, torch.tensor(self.label, dtype=torch.long)

def get_dataloaders(data_config, batch_size=32):
    real_dataset = AudioDataset(data_config['real_folder'], 1)
    fake_dataset = AudioDataset(data_config['fake_folder'], 0)

    combined_dataset = torch.utils.data.ConcatDataset([real_dataset, fake_dataset])
    total_length = len(combined_dataset)
    train_size = int(0.7 * total_length)
    val_size = int(0.15 * total_length)
    test_size = total_length - train_size - val_size

    train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
        combined_dataset, [train_size, val_size, test_size]
    )

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader

def inspect_batch(dataloader):
    batch = next(iter(dataloader))
    waveforms, labels = batch
    print(f"Batch shape: {waveforms.shape}, Labels shape: {labels.shape}")
    print(f"Label distribution: {torch.bincount(labels)}")
    # Save a plot of the first waveform
    plt.figure(figsize=(12, 4))
    plt.plot(waveforms[0].numpy()[0])
    plt.title("First waveform in batch")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.savefig("results/sample_batch.png")
    plt.close()

if __name__ == "__main__":
    # Example data configuration
    data_config = {
        'real_folder': 'data/real',      # Replace with your real data path
        'fake_folder': 'data/fake'       # Replace with your fake data path
    }

    # Create dataloaders
    train_loader, val_loader, test_loader = get_dataloaders(data_config)

    # Inspect the training batch
    inspect_batch(train_loader)

    # Count and print number of real/fake files
    real_dataset = AudioDataset(data_config['real_folder'], 1)
    fake_dataset = AudioDataset(data_config['fake_folder'], 0)
    print(f"Real files: {len(real_dataset)}, Fake files: {len(fake_dataset)}")
