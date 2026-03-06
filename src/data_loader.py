import os
import torch
import random
from torch.utils.data import Dataset, DataLoader
from extract_features import extract_wav2vec2
from tqdm import tqdm

SUPPORTED = (".wav", ".flac")
MAX_PER_CLASS = 100


class AudioDataset(Dataset):
    def __init__(self, real_dirs, fake_dirs, cache_path=None):
        self.samples = []

        if cache_path and os.path.exists(cache_path):
            print(f"Loading cached embeddings from {cache_path}...")
            self.samples = torch.load(cache_path)
            print(f"Loaded {len(self.samples)} samples from cache.")
            return

        print("Extracting features...")

        real_count = 0
        for folder in real_dirs:
            if real_count >= MAX_PER_CLASS:
                break
            files = [f for f in os.listdir(folder) if f.endswith(SUPPORTED)]
            for fname in tqdm(files, desc=f"Real: {folder}"):
                if real_count >= MAX_PER_CLASS:
                    break
                path = os.path.join(folder, fname)
                try:
                    emb = extract_wav2vec2(path)
                    self.samples.append((torch.tensor(emb, dtype=torch.float32), 0))
                    real_count += 1
                except Exception as e:
                    print(f"  Skipped {fname}: {e}")

        fake_count = 0
        for folder in fake_dirs:
            if fake_count >= MAX_PER_CLASS:
                break
            files = [f for f in os.listdir(folder) if f.endswith(SUPPORTED)]
            for fname in tqdm(files, desc=f"Fake: {folder}"):
                if fake_count >= MAX_PER_CLASS:
                    break
                path = os.path.join(folder, fname)
                try:
                    emb = extract_wav2vec2(path)
                    self.samples.append((torch.tensor(emb, dtype=torch.float32), 1))
                    fake_count += 1
                except Exception as e:
                    print(f"  Skipped {fname}: {e}")

        print(f"Extracted — Real: {real_count} | Fake: {fake_count}")

        if cache_path:
            torch.save(self.samples, cache_path)
            print(f"Saved cache to {cache_path}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        emb, label = self.samples[idx]
        if isinstance(label, torch.Tensor):
            label = label.item()
        return emb, torch.tensor(label, dtype=torch.long)


def get_dataloaders(batch_size=32, val_split=0.2, cache_path=None):
    real_dirs = ["data/asv_spoof/real"]
    fake_dirs = ["data/asv_spoof/fake", "data/hindi_fake", "data/telugu_fake"]

    dataset = AudioDataset(real_dirs, fake_dirs, cache_path=cache_path)

    random.seed(42)
    random.shuffle(dataset.samples)

    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_set,   batch_size=batch_size, shuffle=False)

    print(f"Train: {train_size} | Val: {val_size}")
    return train_loader, val_loader


if __name__ == "__main__":
    train_loader, val_loader = get_dataloaders(batch_size=32, cache_path="data/embeddings_cache.pt")
    batch = next(iter(train_loader))
    print(f"Batch shape: {batch[0].shape}")
    print(f"Labels: {batch[1]}")