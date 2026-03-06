import torch
import torch.nn as nn


class DeepfakeClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1024, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        return self.layers(x)

    def predict(self, logits):
        probs = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(probs, dim=1)
        confidence = probs.max(dim=1).values
        labels = ["REAL VOICE", "AI FAKE"]
        return labels[predicted_class.item()], confidence.item()

    def save_checkpoint(self, path):
        torch.save(self.state_dict(), path)

    def load_checkpoint(self, path):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_state_dict(torch.load(path, map_location=device))