from pathlib import Path
from typing import Any, Dict

from groq import Groq

from config import GROQ_API_KEY, MODEL_NAME


def _detect_language_label(language_code: str | None) -> str:
    """
    Convert Whisper language codes into user-friendly labels.
    """

    language_map = {
        "ur": "Urdu",
        "en": "English",
    }

    if not language_code:
        return "Auto-detected"

    return language_map.get(
        language_code.lower(),
        language_code.upper(),
    )


def transcribe_audio(uploaded_file) -> Dict[str, Any]:
    """
    Transcribe an uploaded/recorded audio file using
    Groq's Whisper Large V3 model.

    The input language is intentionally not supplied so that
    the system can handle Urdu, English, and mixed speech
    without requiring manual language selection.

    Returns a structured result dictionary.
    """

    filename = getattr(uploaded_file, "name", "recording.wav")

    base_result = {
        "success": False,
        "text": None,
        "language": None,
        "language_code": None,
        "source": "voice",
        "filename": filename,
        "error": None,
    }

    if not GROQ_API_KEY:
        base_result["error"] = (
            "Groq API key is not configured. "
            "Please add GROQ_API_KEY to Streamlit Secrets."
        )
        return base_result

    try:
        client = Groq(api_key=GROQ_API_KEY)

        file_bytes = uploaded_file.getvalue()

        file_tuple = (
            filename,
            file_bytes,
        )

        transcription = client.audio.transcriptions.create(
            file=file_tuple,
            model=MODEL_NAME,
            response_format="verbose_json",
            temperature=0.0,
        )

        text = getattr(transcription, "text", "") or ""
        language_code = getattr(transcription, "language", None)

        text = " ".join(text.split())

        if not text:
            base_result["error"] = (
                "No speech could be detected in the audio."
            )
            return base_result

        base_result.update(
            {
                "success": True,
                "text": text,
                "language": _detect_language_label(language_code),
                "language_code": language_code,
            }
        )

        return base_result

    except Exception as exc:
        error_message = str(exc).strip()

        if not error_message:
            error_message = "An unexpected transcription error occurred."

        base_result["error"] = error_message

        return base_result