import torch
import librosa
import numpy as np
from transformers import AutoModel, AutoFeatureExtractor
import sys

# Load pre-trained model and feature extractor
model_name = "facebook/wav2vec2-xlsr-53"
model = AutoModel.from_pretrained(model_name)
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)

# Freeze all parameters
for param in model.parameters():
    param.requires_grad = False

# Set model to evaluation mode
model.eval()

def extract_wav2vec2(audio_path):
    # 1. Load audio file
    audio, sr = librosa.load(audio_path, sr=16000)
    
    # 2. Convert to mono (if stereo)
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=0)
    
    # 3. Preprocess with feature extractor
    inputs = feature_extractor(audio, sampling_rate=16000, return_tensors="pt")
    input_values = inputs.input_values
    
    # 4. Pass through model
    with torch.no_grad():
        outputs = model(input_values)
    
    # 5. Extract encoder outputs (hidden states)
    encoder_outputs = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, 1024)
    
    # 6. Take mean over time dimension to get 1024-dimensional embedding
    embedding = torch.mean(encoder_outputs, dim=1).squeeze().numpy()  # Shape: (1024,)
    
    return embedding

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_features.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    try:
        embedding = extract_wav2vec2(audio_path)
        print(f"Embedding shape: {embedding.shape}")
    except Exception as e:
        print(f"Error: {e}")
