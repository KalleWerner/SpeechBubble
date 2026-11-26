import json
import queue
import socket
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

# --- Configuration ---
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000  # the Vosk model expects 16 kHz audio
BLOCK_SIZE = 4000  # 4000 samples @ 16 kHz = 0.25s per chunk
DEVICE_INDEX = None  # None = system default mic; set an int to pick a specific mic

KEYWORDS = [
    "red",
    "blue",
    "green",
    "yellow",
    "cube",
    "square",
    "sphere",
    "circle",
    "pyramid",
    "triangle",
    "donut",
    "cylinder",
    "reset",
    "clear",
    "[unk]",
]

# Set to True later when Unity's UdpVoiceReceiver is running
ENABLE_UDP = False
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# --- Initialization ---
SetLogLevel(-1)

audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    """Runs on a separate high-priority audio thread whenever a chunk is recorded."""
    if status:
        print(f"[Audio Warning] {status}", file=sys.stderr)
    audio_queue.put(bytes(indata))


def handle_recognized_word(word, sock):
    """Handles a confirmed keyword (prints locally and optionally sends to Unity)."""
    print(f"\n>>> FILTER COMMAND: '{word}'")
    if ENABLE_UDP and sock is not None:
        sock.sendto(word.encode("utf-8"), (UDP_IP, UDP_PORT))


def main():
    # 1. Detect the microphone's native sample rate (e.g., 44100 or 48000 Hz)
    device_info = sd.query_devices(DEVICE_INDEX, "input")
    samplerate = int(device_info["default_samplerate"])
    blocksize = int(samplerate * 0.25)  # Keep 0.25s chunks regardless of sample rate

    # 2. Load acoustic model and let Vosk resample internally from `samplerate`
    print(
        f"Loading model from '{MODEL_PATH}' (Mic: {device_info['name']} @ {samplerate} Hz)..."
    )
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, samplerate, json.dumps(KEYWORDS))

    # 3. Prepare UDP socket if enabled
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) if ENABLE_UDP else None

    print("Ready! Speak one of:", ", ".join(w for w in KEYWORDS if w != "[unk]"))
    print("Press Ctrl+C to stop.\n")

    # 4. Open microphone stream using the detected native sample rate
    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=blocksize,
            device=DEVICE_INDEX,
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            while True:
                data = audio_queue.get()

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()

                    if text and text != "[unk]":
                        handle_recognized_word(text, sock)
                else:
                    partial = (
                        json.loads(recognizer.PartialResult())
                        .get("partial", "")
                        .strip()
                    )
                    if partial and partial != "[unk]":
                        print(f"\rListening... ({partial})      ", end="", flush=True)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if sock is not None:
            sock.close()


if __name__ == "__main__":
    main()
