import torch
import librosa
import numpy as np
import sys
import os
from transformers import AutoModel, AutoFeatureExtractor

MODEL_NAME = "facebook/wav2vec2-large-xlsr-53"
DEVICE = torch.device("cpu")

_model = None
_feature_extractor = None

def _load_model():
    global _model, _feature_extractor
    if _model is None:
        print("Loading wav2vec2-large-xlsr-53...")
        _feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
        for param in _model.parameters():
            param.requires_grad = False
        _model.eval()
        print("Model loaded and frozen.")
    return _model, _feature_extractor

def extract_wav2vec2(audio_path):
    model, feature_extractor = _load_model()
    audio, _ = librosa.load(audio_path, sr=16000, mono=True)
    inputs = feature_extractor(audio, sampling_rate=16000, return_tensors="pt")
    input_values = inputs.input_values.to(DEVICE)
    with torch.no_grad():
        outputs = model(input_values=input_values)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    assert embedding.shape == (1024,), f"Unexpected shape: {embedding.shape}"
    return embedding
