import pyttsx3
import threading


_engine = None
_lock = threading.Lock()


def init_engine(rate=160, volume=1.0):
    """
    Initialize TTS engine safely
    """

    global _engine

    if _engine is None:

        try:

            _engine = pyttsx3.init()

            _engine.setProperty("rate", rate)
            _engine.setProperty("volume", volume)

            voices = _engine.getProperty("voices")

            # choose first available voice
            if voices:
                _engine.setProperty("voice", voices[0].id)

        except Exception as e:

            print("Voice engine error:", e)
            _engine = None

    return _engine


def speak(text):
    """
    Speak given text
    """

    global _engine

    if not text:
        return

    engine = init_engine()

    if engine is None:
        print("[VOICE]", text)
        return

    try:

        with _lock:

            engine.say(text)
            engine.runAndWait()

    except Exception as e:

        print("Speech failed:", e)


def stop():
    """
    Stop current speech
    """

    global _engine

    if _engine:

        try:
            _engine.stop()
        except:
            pass


def speak_async(text):
    """
    Speak without blocking program
    """

    thread = threading.Thread(target=speak, args=(text,))
    thread.daemon = True
    thread.start()
