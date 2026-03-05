import os
import pathlib
import soundfile as sf
import gtts
from pydub import AudioSegment
from datasets import load_dataset, Dataset
from tqdm import tqdm

# Constants for sentences
HINDI_SENTENCES = [
    "नमस्कार, मैं आपके बैंक से बात कर रहा हूँ। आपके खाते में एक अज्ञात ऋण है।",
    "मुझे तुरंत 5000 रुपये जमा करें, अन्यथा आपके खाता बंद कर दिया जाएगा।",
    "आपके बच्चों के छात्रवृत्ति के लिए धन जमा करें, अब तक के लिए आपके खाते से निकाल लिया गया है।",
    "आपकी शादी के लिए एक अत्याधुनिक आभूषण खरीदें, आपके पति के नाम पर भेजा जाएगा।",
    "आपके पिता की बीमारी के लिए आपको तत्काल धन जमा करना होगा।"
]

TELUGU_SENTENCES = [
    "మీకు బ్యాంకు నుంచి ఒక కాల్ వచ్చింది, మీ ఖాతాలో అసలు రుణం ఉంది.",
    "ఇప్పుడు 5000 రూపాయలు జమ్ము చేయండి, లేకపోతే మీ ఖాతా బంద్ అవుతుంది.",
    "మీ పిల్లల విద్యార్థి వృత్తికి డబ్బు జమ్ము చేయండి, ఇప్పటికే మీ ఖాతా నుంచి తీసివేయబడింది.",
    "మీ వివాహానికి ఒక అద్భుతమైన గాల్స్ కొనుగోలు చేయండి, మీ భర్త పేరు పై పంపబడుతుంది.",
    "మీ తండ్రి ఆరోగ్యం కోసం డబ్బు జమ్ము చేయండి, ఇప్పుడు త్వరలో జరుగుతుంది."
]

def load_indic_huggingface():
    """
    Load the Indic TTS Deepfake dataset from HuggingFace, filter by Hindi and Telugu,
    and save real/fake audio files in the appropriate directories.
    """
    try:
        # Attempt to load the first dataset
        dataset = load_dataset("SherryT997/IndicTTS-Deepfake-Challenge-Data")
    except:
        # If first dataset not found, try the second
        try:
            dataset = load_dataset("ai4bharat/indic-tts-deepfake")
        except:
            print("Error: Could not load the dataset from HuggingFace. Please check the dataset name and availability.")
            return

    # Ensure directories exist
    for lang in ["hi", "te"]:
        for real_fake in ["real", "fake"]:
            folder = f"data/{lang}_{real_fake}"
            os.makedirs(folder, exist_ok=True)

    # Process Hindi
    hindi_data = dataset.filter(lambda x: x["language"] == "hi")
    for split in ["train", "test"]:
        if split in hindi_data:
            for item in tqdm(hindi_data[split], desc="Processing Hindi"):
                audio = item["audio"]
                is_real = item["is_real"]
                lang = "hi"
                folder = f"data/{lang}_{('real' if is_real else 'fake')}"
                filename = f"{item['id']}.wav"
                sf.write(os.path.join(folder, filename), audio["array"], audio["sampling_rate"])
    
    # Process Telugu
    telugu_data = dataset.filter(lambda x: x["language"] == "te")
    for split in ["train", "test"]:
        if split in telugu_data:
            for item in tqdm(telugu_data[split], desc="Processing Telugu"):
                audio = item["audio"]
                is_real = item["is_real"]
                lang = "te"
                folder = f"data/{lang}_{('real' if is_real else 'fake')}"
                filename = f"{item['id']}.wav"
                sf.write(os.path.join(folder, filename), audio["array"], audio["sampling_rate"])

    # Count files saved
    for lang in ["hi", "te"]:
        for real_fake in ["real", "fake"]:
            folder = f"data/{lang}_{real_fake}"
            files = len(list(pathlib.Path(folder).glob("*.wav")))
            print(f"Saved {files} files in {folder}")

def generate_fake_with_gtts(language, output_folder, num_samples=5):
    """
    Generate fake audio samples using gTTS for the specified language and save them as .wav files.
    """
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Select sentences based on language
    if language == "hi":
        sentences = HINDI_SENTENCES
    elif language == "te":
        sentences = TELUGU_SENTENCES
    else:
        raise ValueError("Unsupported language. Use 'hi' for Hindi or 'te' for Telugu.")

    # Generate and save fake samples
    for sentence in tqdm(sentences, desc=f"Generating fake {language} audio"):
        try:
            tts = gtts.gTTS(sentence, lang=language)
            tts.save("temp.mp3")
            audio = AudioSegment.from_mp3("temp.mp3")
            audio.export(os.path.join(output_folder, f"{sentence[:10]}.wav"), format="wav")
            os.remove("temp.mp3")
        except Exception as e:
            print(f"Error generating audio for sentence: {sentence}. Error: {e}")

def print_dataset_summary():
    """
    Count the number of .wav files in each data subfolder and print a summary table.
    """
    from tabulate import tabulate

    # Define folders to check
    folders = [
        "data/hindi_real", "data/hindi_fake",
        "data/telugu_real", "data/telugu_fake"
    ]

    # Count files in each folder
    counts = []
    for folder in folders:
        file_count = len(list(pathlib.Path(folder).glob("*.wav")))
        counts.append((folder, file_count))

    # Print summary table
    print("\n=== Dataset Summary ===")
    print(tabulate(counts, headers=["Folder", "File Count"], tablefmt="grid"))

    # Check if any folder has fewer than 5 files
    for folder, count in counts:
        if count < 5:
            print(f"WARNING: Folder '{folder}' has only {count} files (less than 5).")

if __name__ == "__main__":
    load_indic_huggingface()
    generate_fake_with_gtts("hi", "data/hindi_fake")
    generate_fake_with_gtts("te", "data/telugu_fake")
    print_dataset_summary()
