#!/usr/bin/env python3
# any2any_ai.py — offline "any↔any" with default speech-out
# - Text→Audio (pyttsx3), auto-plays WAV (Windows)
# - Audio→Text (Vosk) and Text→Text -> both spoken aloud by default

import argparse, os, sys, wave, json, shutil, zipfile, subprocess, re
from pathlib import Path

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

# -------- lazy imports --------
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

# -------- TTS helper --------
def speak(text: str):
    if not text:
        return
    pyttsx3 = lazy_import_pyttsx3()
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -------- model bootstrap --------
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
        info(f"Vosk model ready at {VOSK_DIR}")
    except Exception as e:
        fail(f"Could not download/extract Vosk model automatically.\n{e}\n"
             f"Manual: download {VOSK_ZIP_URL} and unzip into {MODELS}")

# -------- audio IO helpers --------
def ensure_wav_16k_mono(src_path: Path) -> Path:
    src_path = Path(src_path)
    try:
        with wave.open(str(src_path), "rb") as wf:
            ch, rate = wf.getnchannels(), wf.getframerate()
            if ch == 1 and rate == 16000:
                return src_path
    except wave.Error:
        pass
    if not have("ffmpeg"):
        fail("ffmpeg required to convert audio to 16k mono WAV. Install and add to PATH.")
    out = src_path.with_suffix(".16kmono.wav")
    cmd = ["ffmpeg","-y","-i",str(src_path),"-ac","1","-ar","16000","-f","wav",str(out)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out

def autoplay_wav(path: Path):
    path = Path(path)
    if os.name == "nt":
        import winsound
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
    else:
        # best-effort on mac/linux if available
        for cmd in (["afplay", str(path)], ["aplay", str(path)], ["paplay", str(path)],
                    ["ffplay","-nodisp","-autoexit",str(path)]):
            if have(cmd[0]):
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
