import numpy as np
import torch
import time
import collections
import colorama
import sounddevice as sd
import soundfile as sf
import sys
import os

from colorama import Fore, Style
colorama.init(autoreset=True)

sys.path.insert(0, os.path.dirname(__file__))
from classifier import DeepfakeClassifier
from extract_features import extract_wav2vec2

SAMPLE_RATE = 16000
BUFFER_SECONDS = 2
LABELS = ["REAL VOICE", "AI FAKE"]


class RealtimeDetector:
    def __init__(self, checkpoint_path):
        self.device = torch.device("cpu")
        self.model = DeepfakeClassifier()
        self.model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
        self.model.eval()
        print(f"Model loaded from {checkpoint_path}")

    def predict_chunk(self, audio_array):
        sf.write("temp_chunk.wav", audio_array, SAMPLE_RATE)
        embedding = extract_wav2vec2("temp_chunk.wav")
        tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred].item()
        return LABELS[pred], confidence


def run_realtime(detector):
    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + "  Real-Time Deepfake Voice Detection")
    print(Fore.CYAN + "  Press Ctrl+C to stop")
    print(Fore.CYAN + "=" * 50 + "\n")

    start_time = time.time()

    try:
        while True:
            print(Fore.YELLOW + f"Recording {BUFFER_SECONDS}s... speak now")
            audio = sd.rec(
                int(BUFFER_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32"
            )
            sd.wait()
            audio = audio.squeeze()

            label, confidence = detector.predict_chunk(audio)
            elapsed = time.time() - start_time
            time_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
            color = Fore.GREEN if label == "REAL VOICE" else Fore.RED
            bar = "█" * int(confidence * 20)
            print(f"{Fore.YELLOW}[{time_str}]  {color}{label:12s}  {Fore.WHITE}confidence: {confidence*100:.1f}% |{bar}|{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(Fore.CYAN + "\nStopped.")


def simulate_from_file(detector, file_path):
    import librosa
    print(Fore.CYAN + f"\nSimulating detection on: {os.path.basename(file_path)}\n")
    audio, _ = librosa.load(file_path, sr=16000, mono=True)

    window = SAMPLE_RATE * BUFFER_SECONDS
    step = SAMPLE_RATE
    start_time = time.time()
    idx = 0

    while idx + window <= len(audio):
        chunk = audio[idx: idx + window]
        label, confidence = detector.predict_chunk(chunk)
        elapsed = time.time() - start_time
        time_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
        color = Fore.GREEN if label == "REAL VOICE" else Fore.RED
        print(f"{Fore.YELLOW}[{time_str}]  {color}{label:12s}  {Fore.WHITE}confidence: {confidence*100:.1f}%{Style.RESET_ALL}")
        idx += step
        time.sleep(0.5)


def main():
    if len(sys.argv) < 2:
        print(Fore.YELLOW + "Usage:")
        print("  Live mic:   python realtime_detect.py models/best_classifier.pt")
        print("  From file:  python realtime_detect.py models/best_classifier.pt audio.wav")
        sys.exit(1)

    model_path = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(model_path):
        print(Fore.RED + f"Checkpoint not found: {model_path}")
        sys.exit(1)

    detector = RealtimeDetector(model_path)

    if file_path:
        simulate_from_file(detector, file_path)
    else:
        run_realtime(detector)


if __name__ == "__main__":
    main()