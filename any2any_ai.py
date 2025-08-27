#!/usr/bin/env python3
# any2any_ai.py — minimal offline "any↔any" backbone (Windows-friendly)
# Text→Audio (pyttsx3), Audio→Text (Vosk), simple Text→Text tools.

import argparse, os, sys, wave, json, shutil, tempfile, zipfile, subprocess, re
from pathlib import Path

# ---------- Utilities ----------
HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
VOSK_DIR = MODELS / "vosk-model-small-en-us-0.15"
VOSK_ZIP_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def fail(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)

def info(msg: str):
    print(f"[any2any] {msg}")

# ---------- Optional lazy imports ----------
def lazy_import_vosk():
    try:
        import vosk  # noqa
        return vosk
    except Exception:
        fail("Missing dependency: vosk. Install with:  pip install vosk")

def lazy_import_pyttsx3():
    try:
        import pyttsx3  # noqa
        return pyttsx3
    except Exception:
        fail("Missing dependency: pyttsx3. Install with:  pip install pyttsx3")

# ---------- Model bootstrap ----------
def ensure_vosk_model():
    if VOSK_DIR.exists():
        return
    info("Downloading Vosk small EN model (≈50MB)…")
    MODELS.mkdir(parents=True, exist_ok=True)
    zip_path = MODELS / "vosk-small-en.zip"
    try:
        import urllib.request
        urllib.request.urlretrieve(VOSK_ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(MODELS)
        # Vosk zips extract to a folder; keep original folder name
        info(f"Vosk model ready at {VOSK_DIR}")
    except Exception as e:
        fail(f"Could not download/extract Vosk model automatically.\n{e}\n"
             f"Manual fallback: download {VOSK_ZIP_URL} and unzip into {MODELS}")

# ---------- Audio helpers ----------
def ensure_wav_16k_mono(src_path: Path) -> Path:
    """
    Ensure audio is 16kHz mono WAV (required by Vosk).
    If not, and ffmpeg is available, convert. Otherwise, error out.
    """
    src_path = Path(src_path)
    try:
        with wave.open(str(src_path), "rb") as wf:
            ch, rate = wf.getnchannels(), wf.getframerate()
            if ch == 1 and rate == 16000:
                return src_path
    except wave.Error:
        # Not a WAV or unreadable — will need conversion
        pass

    if not have("ffmpeg"):
        fail("ffmpeg is required to convert audio to 16k mono WAV. "
             "Install it and ensure it's on PATH.")

    tmp = src_path.with_suffix(".16kmono.wav")
    cmd = [
        "ffmpeg", "-y", "-i", str(src_path),
        "-ac", "1", "-ar", "16000", "-f", "wav", str(tmp)
    ]
    info("Converting audio → 16kHz mono WAV via ffmpeg…")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tmp

# ---------- Core transforms ----------
def tts_text_to_wav(text: str, out_path: Path):
    pyttsx3 = lazy_import_pyttsx3()
    engine = pyttsx3.init()
    out_path = Path(out_path)
    if out_path.suffix.lower() != ".wav":
        out_path = out_path.with_suffix(".wav")
    info(f"Generating speech → {out_path.name}")
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()
    info("Done.")

def stt_audio_to_text(audio_path: Path) -> str:
    ensure_vosk_model()
    vosk = lazy_import_vosk()
    from vosk import Model, KaldiRecognizer
    wav_path = ensure_wav_16k_mono(audio_path)

    model = Model(str(VOSK_DIR))
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)

    with wave.open(str(wav_path), "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

    res = json.loads(rec.FinalResult())
    return res.get("text", "").strip()

# ---------- Tiny text→text tools ----------
def summarize_text(text: str, max_sentences: int = 3) -> str:
    # Naive frequency-based compression that needs no extra libs.
    # 1) split sentences, 2) score words by frequency (downweight stopwords),
    # 3) pick top-N sentences preserving order.
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sents) <= max_sentences:
        return text.strip()

    words = re.findall(r"[A-Za-z']+", text.lower())
    stop = set("""the a an and or but if then so of in on at to for from with as is are was were be been being by this that it
                 you i he she we they them us our your his her their not no do does did will would can could should""".split())
    freq = {}
    for w in words:
        if w in stop or len(w) <= 2:
            continue
        freq[w] = freq.get(w, 0) + 1

    def score(sent):
        tokens = re.findall(r"[A-Za-z']+", sent.lower())
        return sum(freq.get(t, 0) for t in tokens) / (len(tokens) + 1e-9)

    ranked = sorted(enumerate(sents), key=lambda x: score(x[1]), reverse=True)
    keep_idx = sorted(i for i, _ in ranked[:max_sentences])
    return " ".join(sents[i] for i in keep_idx)

def keywords(text: str, k: int = 10):
    words = re.findall(r"[A-Za-z']+", text.lower())
    stop = set("""the a an and or but if then so of in on at to for from with as is are was were be been being by this that it
                 you i he she we they them us our your his her their not no do does did will would can could should""".split())
    freq = {}
    for w in words:
        if w in stop or len(w) <= 2:
            continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:k]]

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="any2any_ai: minimal offline any↔any core")
    ap.add_argument("--from", dest="src_type", choices=["text", "audio"], required=True,
                    help="source modality")
    ap.add_argument("--to", dest="dst_type", choices=["text", "audio"], required=True,
                    help="destination modality")
    ap.add_argument("--input", "-i", help="input file path OR inline text if --from=text", required=True)
    ap.add_argument("--output", "-o", help="output file path (required for --to=audio)")
    ap.add_argument("--task", choices=["echo", "summarize", "keywords"], default="echo",
                    help="text→text task when --from=text --to=text")
    ap.add_argument("--max_sentences", type=int, default=3, help="summarize: number of sentences")
    args = ap.parse_args()

    src, dst = args.src_type, args.dst_type

    # text → audio
    if src == "text" and dst == "audio":
        if not args.output:
            fail("Provide --output for audio (e.g., out.wav)")
        tts_text_to_wav(args.input, Path(args.output))
        return

    # audio → text
    if src == "audio" and dst == "text":
        p = Path(args.input)
        if not p.exists():
            fail(f"Audio not found: {p}")
        text = stt_audio_to_text(p)
        print(text)
        return

    # text → text
    if src == "text" and dst == "text":
        if args.task == "echo":
            print(args.input)
        elif args.task == "summarize":
            print(summarize_text(args.input, max_sentences=args.max_sentences))
        elif args.task == "keywords":
            print(", ".join(keywords(args.input)))
        return

    fail("Route not implemented yet.")

if __name__ == "__main__":
    main()
