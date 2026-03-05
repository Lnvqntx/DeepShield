import numpy as np
import pyaudio
import torch
import time
import threading
import collections
import colorama
from colorama import Fore, Style
import wave
import sys
import os

colorama.init(autoreset=True)

class AudioCapture:
    """
    A class to capture audio from the microphone in real-time and maintain a rolling buffer of 2 seconds (32000 samples).
    """

    def __init__(self, sample_rate=16000, chunk_size=1024, buffer_length=32000):
        """
        Initialize the AudioCapture object.

        Parameters:
            sample_rate (int): Sample rate in Hz (default: 16000).
            chunk_size (int): Number of samples per chunk (default: 1024).
            buffer_length (int): Total number of samples to buffer (default: 32000 for 2 seconds).
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.buffer_length = buffer_length
        self.buffer = collections.deque(maxlen=buffer_length)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False

    def start(self):
        """
        Start the microphone stream.
        """
        try:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._callback
            )
            self.running = True
            self.stream.start_stream()
        except Exception as e:
            print(Fore.RED + "Error initializing microphone: " + str(e))
            sys.exit(1)

    def stop(self):
        """
        Stop the microphone stream and close the PyAudio instance.
        """
        if self.running:
            self.running = False
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def _callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for PyAudio to process incoming audio data.

        Parameters:
            in_data (bytes): Raw audio data.
            frame_count (int): Number of frames.
            time_info (dict): Timing information.
            status (int): Status of the stream.
        """
        if self.running:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            self.buffer.extend(audio_data)
        return (in_data, pyaudio.paContinue)

    def get_chunk(self):
        """
        Retrieve a chunk of audio data (32000 samples) from the buffer.

        Returns:
            numpy.ndarray: Audio chunk of shape (32000,) if available, else None.
        """
        if len(self.buffer) >= self.buffer_length:
            return np.array(self.buffer, dtype=np.float32)
        return None


class RealtimeDetector:
    """
    A class to perform real-time deepfake detection using a pre-trained model.
    """

    def __init__(self, checkpoint_path, language="hindi"):
        """
        Initialize the RealtimeDetector with a model checkpoint.

        Parameters:
            checkpoint_path (str): Path to the model checkpoint file.
            language (str): Language of the audio input (default: "hindi").
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(checkpoint_path, map_location=self.device)
        self.model.to(self.device)
        self.model.eval()
        self.language = language

    def predict_chunk(self, audio_array):
        """
        Predict whether the audio chunk is real or fake.

        Parameters:
            audio_array (numpy.ndarray): Audio chunk of shape (32000,).

        Returns:
            tuple: (label_string, confidence_float)
        """
        start_time = time.time()
        with torch.no_grad():
            tensor = torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).to(self.device)
            output = self.model(tensor).item()
        duration = time.time() - start_time
        assert duration < 0.5, f"Prediction took too long: {duration:.2f} seconds"
        label = "Real" if output > 0.5 else "Fake"
        confidence = output if label == "Real" else 1 - output
        return label, confidence


def run_realtime_detection(detector, capture):
    """
    Main loop for real-time detection.

    Parameters:
        detector (RealtimeDetector): The detection model.
        capture (AudioCapture): The audio capture object.
    """
    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + "Starting Real-Time Deepfake Detection")
    print(Fore.CYAN + "=" * 50 + "\n")

    start_time = time.time()
    chunk_counter = 0

    while True:
        chunk = capture.get_chunk()
        if chunk is not None:
            chunk_counter += 1
            label, confidence = detector.predict_chunk(chunk)
            elapsed_time = time.time() - start_time
            time_str = f"{int(elapsed_time // 60):02d}:{int(elapsed_time % 60):02d}"
            print(
                f"{Fore.YELLOW}[{time_str}] {Fore.GREEN if label == 'Real' else Fore.RED}{label} {Fore.YELLOW}({confidence:.2f}){Style.RESET_ALL}"
            )
            time.sleep(0.1)  # Small delay to avoid overwhelming the console


def simulate_from_file(detector, file_path):
    """
    Simulate detection from a .wav file.

    Parameters:
        detector (RealtimeDetector): The detection model.
        file_path (str): Path to the .wav file.
    """
    try:
        with wave.open(file_path, 'rb') as wav_file:
            if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 4:
                raise ValueError("File must be mono and 32-bit float PCM.")
            sample_rate = wav_file.getframerate()
            if sample_rate != 16000:
                raise ValueError("Sample rate must be 16000 Hz.")
            frames = wav_file.getnframes()
            audio_data = np.frombuffer(wav_file.readframes(frames), dtype=np.float32)
    except Exception as e:
        print(Fore.RED + "Error reading .wav file: " + str(e))
        return

    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + "Simulating Detection from File")
    print(Fore.CYAN + "=" * 50 + "\n")

    start_time = time.time()
    chunk_index = 0

    while chunk_index * 32000 < len(audio_data):
        chunk = audio_data[chunk_index * 32000 : (chunk_index + 1) * 32000]
        chunk_index += 1
        label, confidence = detector.predict_chunk(chunk)
        elapsed_time = time.time() - start_time
        time_str = f"{int(elapsed_time // 60):02d}:{int(elapsed_time % 60):02d}"
        print(
            f"{Fore.YELLOW}[{time_str}] {Fore.GREEN if label == 'Real' else Fore.RED}{label} {Fore.YELLOW}({confidence:.2f}){Style.RESET_ALL}"
        )
        time.sleep(1)  # 1 second delay between chunks


def main():
    if len(sys.argv) < 2:
        print(Fore.YELLOW + "Usage: python detect.py <model_path> [file_path]")
        sys.exit(1)

    model_path = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(model_path):
        print(Fore.RED + f"Model file not found: {model_path}")
        sys.exit(1)

    detector = RealtimeDetector(model_path)

    if file_path:
        simulate_from_file(detector, file_path)
    else:
        capture = AudioCapture()
        capture.start()
        run_realtime_detection(detector, capture)
        capture.stop()


if __name__ == "__main__":
    main()
