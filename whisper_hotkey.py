#!/usr/bin/env python3
"""
Whisper Hotkey - Voice-to-clipboard for macOS

Record audio with a hotkey, transcribe with OpenAI Whisper,
and automatically copy the text to your clipboard.

Usage:
    python3 whisper_hotkey.py [--model tiny|base|small|medium|large-v3]

Requirements:
    - pyaudio (for audio recording)
    - faster-whisper (for transcription)
    - Hammerspoon (for global hotkey)
"""

import argparse
import io
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import wave

SOCKET_PATH = "/tmp/whisper_hotkey.sock"
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit


def check_dependencies():
    """Verify required packages are installed."""
    missing = []
    try:
        import pyaudio  # noqa: F401
    except ImportError:
        missing.append("pyaudio")
    try:
        from faster_whisper import WhisperModel  # noqa: F401
    except ImportError:
        missing.append("faster-whisper")
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print("Run: pip install " + " ".join(missing), file=sys.stderr)
        sys.exit(1)


def copy_to_clipboard(text: str):
    """Copy text to macOS clipboard using pbcopy."""
    proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    proc.communicate(text.encode("utf-8"))


def play_sound(name: str):
    """Play a short system sound (non-blocking)."""
    sounds = {
        "start": "/System/Library/Sounds/Pop.aiff",
        "stop": "/System/Library/Sounds/Bottle.aiff",
        "done": "/System/Library/Sounds/Glass.aiff",
        "error": "/System/Library/Sounds/Basso.aiff",
    }
    path = sounds.get(name)
    if path and os.path.exists(path):
        subprocess.Popen(["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Recorder:
    """Handles audio recording in a background thread."""

    def __init__(self):
        self.frames: list[bytes] = []
        self.recording = False
        self._stream = None
        self._audio = None
        self._thread = None

    def start(self):
        import pyaudio

        self.frames = []
        self.recording = True
        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=1024,
        )
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def _record_loop(self):
        while self.recording:
            try:
                data = self._stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break

    def stop(self) -> bytes | None:
        """Stop recording, return WAV bytes or None if no audio captured."""
        self.recording = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._audio:
            self._audio.terminate()

        if not self.frames:
            return None

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(self.frames))
        return buf.getvalue()


class WhisperTranscriber:
    """Lazy-loads and caches the faster-whisper model."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    def load(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            print(f"Loading Whisper '{self.model_name}' model...")
            self._model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="float32"
            )
            print("Model loaded.")

    def transcribe(self, wav_bytes: bytes) -> str:
        self.load()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_bytes)
            tmp_path = f.name
        try:
            segments, _ = self._model.transcribe(tmp_path, beam_size=5)
            text = " ".join(segment.text for segment in segments)
            return text.strip()
        finally:
            os.unlink(tmp_path)


def run_server(model_name: str):
    """Main event loop — listens on a Unix socket for toggle commands."""
    check_dependencies()

    transcriber = WhisperTranscriber(model_name)
    recorder = Recorder()

    # Pre-load model so first transcription is fast
    print("Pre-loading model...")
    transcriber.load()

    # Clean up stale socket
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)
    os.chmod(SOCKET_PATH, 0o777)

    def shutdown(signum, frame):
        print("\nShutting down...")
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Whisper Hotkey ready. Listening on {SOCKET_PATH}")
    print(f"Press your hotkey (Ctrl+Shift+Space) to toggle recording.")

    while True:
        try:
            conn, _ = server.accept()
            data = conn.recv(256).decode("utf-8").strip()

            if data == "toggle":
                if not recorder.recording:
                    # Start recording
                    recorder.start()
                    play_sound("start")
                    conn.sendall(b"recording_started")
                    print("Recording started...")
                else:
                    # Stop recording and transcribe
                    play_sound("stop")
                    print("Recording stopped. Transcribing...")
                    conn.sendall(b"recording_stopped")
                    wav_data = recorder.stop()
                    recorder = Recorder()  # Reset for next use

                    if wav_data:
                        text = transcriber.transcribe(wav_data)
                        if text:
                            copy_to_clipboard(text)
                            play_sound("done")
                            print(f"Transcribed & copied: {text}")
                        else:
                            play_sound("error")
                            print("No speech detected.")
                    else:
                        play_sound("error")
                        print("No audio captured.")

            elif data == "status":
                status = "recording" if recorder.recording else "idle"
                conn.sendall(status.encode("utf-8"))

            elif data == "quit":
                conn.sendall(b"bye")
                conn.close()
                shutdown(None, None)

            conn.close()
        except OSError:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Whisper Hotkey — Voice-to-clipboard on macOS"
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: base)",
    )
    args = parser.parse_args()
    run_server(args.model)


if __name__ == "__main__":
    main()
