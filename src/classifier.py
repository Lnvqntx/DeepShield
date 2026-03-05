import torch
import torch.nn as nn
from transformers import AutoModel, AutoFeatureExtractor

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
            nn.Linear(128, 2)  # 2 classes: "REAL VOICE" or "AI FAKE"
        )

    def forward(self, x):
        return self.layers(x)

class DeepfakeDetector(nn.Module):
    def __init__(self,model_name = "facebook/wav2vec2-large-xlsr-53"):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.wav2vec2_model = AutoModel.from_pretrained(model_name).to(self.device)
        for param in self.wav2vec2_model.parameters():
            param.requires_grad = False  # Freeze pre-trained weights
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.classifier = DeepfakeClassifier()

    def forward(self, waveform):
        # Normalize waveform
        mean = waveform.mean(dim=(2,), keepdim=True)
        std = waveform.std(dim=(2,), keepdim=True) + 1e-7
        normalized_waveform = (waveform - mean) / std

        # Convert to numpy for feature extraction
        normalized_waveform_cpu = normalized_waveform.cpu().numpy()

        # Extract features
        input_values = self.feature_extractor(normalized_waveform_cpu, return_tensors="pt")
        input_values = {k: v.to(self.device) for k, v in input_values.items()}

        # Get hidden states from Wav2Vec2
        with torch.no_grad():
            outputs = self.wav2vec2_model(input_values=input_values)
            last_hidden_state = outputs.last_hidden_state  # [batch, seq_len, 1024]

        # Mean pooling over time dimension
        pooled = last_hidden_state.mean(dim=1)  # [batch, 1024]

        # Classify
        logits = self.classifier(pooled)
        return logits

    def predict(self, logits):
        probs = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(probs, dim=1)
        confidence = probs.max(dim=1).values
        labels = ["REAL VOICE", "AI FAKE"]
        return labels[predicted_class.item()], confidence.item()

    def save_checkpoint(self, path):
        torch.save(self.state_dict(), path)

    def load_checkpoint(self, path, strict=True):
        self.load_state_dict(torch.load(path, map_location=self.device), strict=strict)
