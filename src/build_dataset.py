import os
import shutil
import pathlib
import soundfile as sf
import gtts
from pydub import AudioSegment
from tqdm import tqdm
from tabulate import tabulate

# ── Scam sentences for gTTS fake generation ────────────────────────────────────
HINDI_SENTENCES = [
    "नमस्कार, मैं आपके बैंक से बात कर रहा हूँ। आपके खाते में एक अज्ञात ऋण है।",
    "मुझे तुरंत 5000 रुपये जमा करें, अन्यथा आपके खाते बंद कर दिए जाएंगे।",
    "आपके बच्चों की छात्रवृत्ति के लिए धन जमा करें।",
    "आपकी शादी के लिए एक विशेष ऑफर है, अभी संपर्क करें।",
    "आपके पिता की बीमारी के लिए आपको तत्काल धन जमा करना होगा।",
    "हम आपके बिजली कनेक्शन काटने वाले हैं, अभी भुगतान करें।",
    "आपका पार्सल रोका गया है, कृपया सत्यापन शुल्क जमा करें।",
    "आपने एक लकी ड्रा जीता है, इनाम पाने के लिए अभी कॉल करें।",
    "आपके बेटे को पुलिस ने पकड़ा है, जमानत के लिए पैसे भेजें।",
    "आपका आधार कार्ड ब्लॉक होने वाला है, तुरंत अपडेट करें।",
]

TELUGU_SENTENCES = [
    "మీకు బ్యాంకు నుంచి ఒక కాల్ వచ్చింది, మీ ఖాతాలో అసలు రుణం ఉంది.",
    "ఇప్పుడు 5000 రూపాయలు జమ చేయండి, లేకపోతే మీ ఖాతా బంద్ అవుతుంది.",
    "మీ పిల్లల విద్యార్థి వృత్తికి డబ్బు జమ చేయండి.",
    "మీ వివాహానికి ఒక అద్భుతమైన ఆఫర్ ఉంది, ఇప్పుడే సంప్రదించండి.",
    "మీ తండ్రి ఆరోగ్యం కోసం డబ్బు జమ చేయండి.",
    "మీ విద్యుత్ కనెక్షన్ కట్ అవ్వబోతోంది, ఇప్పుడే చెల్లించండి.",
    "మీ పార్సెల్ ఆగిపోయింది, ధృవీకరణ రుసుము చెల్లించండి.",
    "మీరు లక్కీ డ్రా గెలిచారు, బహుమతి పొందేందుకు కాల్ చేయండి.",
    "మీ కొడుకు పోలీసులకు దొరికాడు, బెయిల్ కోసం డబ్బు పంపండి.",
    "మీ ఆధార్ కార్డు బ్లాక్ అవ్వబోతోంది, వెంటనే అప్‌డేట్ చేయండి.",
]


# ── Step 1: Sort ASVspoof flac files into real/ and fake/ ──────────────────────
def build_asv_spoof():
    PROTOCOL = "data/asv_spoof/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt"
    FLAC_DIR = "data/asv_spoof/ASVspoof2019_LA_train/flac"
    REAL_OUT = "data/asv_spoof/real"
    FAKE_OUT = "data/asv_spoof/fake"

    os.makedirs(REAL_OUT, exist_ok=True)
    os.makedirs(FAKE_OUT, exist_ok=True)

    real_count = 0
    fake_count = 0
    missing = 0

    print("Reading ASVspoof protocol file...")
    with open(PROTOCOL, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            filename = parts[1] + ".flac"
            label = parts[4]
            src = os.path.join(FLAC_DIR, filename)
            if not os.path.exists(src):
                missing += 1
                continue
            if label == "genuine":
                dst = os.path.join(REAL_OUT, filename)
                real_count += 1
            else:
                dst = os.path.join(FAKE_OUT, filename)
                fake_count += 1
            shutil.copy2(src, dst)

    print(f"  ASVspoof real: {real_count} | fake: {fake_count} | missing: {missing}")


# ── Step 2: Generate gTTS fake samples ────────────────────────────────────────
def generate_fake_with_gtts(language, output_folder, sentences):
    os.makedirs(output_folder, exist_ok=True)

    for i, sentence in enumerate(tqdm(sentences, desc=f"gTTS {language}")):
        try:
            tts = gtts.gTTS(sentence, lang=language)
            mp3_path = os.path.join(output_folder, f"gtts_{language}_{i:03d}.mp3")
            wav_path = os.path.join(output_folder, f"gtts_{language}_{i:03d}.wav")
            tts.save(mp3_path)
            audio = AudioSegment.from_mp3(mp3_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(wav_path, format="wav")
            os.remove(mp3_path)
        except Exception as e:
            print(f"  WARNING: skipped sentence {i}: {e}")


# ── Summary ────────────────────────────────────────────────────────────────────
def print_dataset_summary():
    folders = [
        "data/asv_spoof/real",
        "data/asv_spoof/fake",
        "data/hindi_fake",
        "data/telugu_fake",
    ]
    counts = []
    for folder in folders:
        n = len(list(pathlib.Path(folder).glob("*"))) if pathlib.Path(folder).exists() else 0
        counts.append((folder, n, "✅" if n >= 5 else "⚠️  LOW"))

    print("\n=== Dataset Summary ===")
    print(tabulate(counts, headers=["Folder", "Files", "Status"], tablefmt="grid"))


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Step 1: Sorting ASVspoof flac files into real/ and fake/...")
    build_asv_spoof()

    print("\nStep 2: Generating Hindi fake samples with gTTS...")
    generate_fake_with_gtts("hi", "data/hindi_fake", HINDI_SENTENCES)

    print("\nStep 3: Generating Telugu fake samples with gTTS...")
    generate_fake_with_gtts("te", "data/telugu_fake", TELUGU_SENTENCES)

    print_dataset_summary()