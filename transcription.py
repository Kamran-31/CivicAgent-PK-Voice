from pathlib import Path
from typing import Any, Dict

import re

from groq import Groq

from config import GROQ_API_KEY, MODEL_NAME


# ---------------------------------------------------------
# Language labels
# ---------------------------------------------------------

def _detect_language_label(language_code: str | None) -> str:
    """
    Convert Whisper language codes into user-friendly labels.
    """

    language_map = {
        "ur": "Urdu",
        "en": "English",
        "tl": "Tagalog",
    }

    if not language_code:
        return "Auto-detected"

    return language_map.get(
        language_code.lower(),
        language_code.upper(),
    )


# ---------------------------------------------------------
# Urdu text detection
# ---------------------------------------------------------

def _contains_urdu_script(text: str) -> bool:
    """
    Detect whether the transcription contains Urdu/Arabic-script
    characters commonly used in Urdu.
    """

    if not text:
        return False

    urdu_pattern = re.compile(
        r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]"
    )

    return bool(urdu_pattern.search(text))


def _urdu_character_count(text: str) -> int:
    """
    Count Urdu/Arabic-script characters in the text.
    """

    if not text:
        return 0

    return len(
        re.findall(
            r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]",
            text,
        )
    )


def _latin_character_count(text: str) -> int:
    """
    Count Latin alphabet characters.
    """

    if not text:
        return 0

    return len(
        re.findall(
            r"[A-Za-z]",
            text,
        )
    )


# ---------------------------------------------------------
# English text detection
# ---------------------------------------------------------

ENGLISH_WORDS = {
    "a",
    "about",
    "after",
    "again",
    "all",
    "am",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "before",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "get",
    "go",
    "good",
    "have",
    "he",
    "hello",
    "help",
    "her",
    "here",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "its",
    "just",
    "know",
    "like",
    "me",
    "my",
    "need",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "please",
    "problem",
    "report",
    "she",
    "so",
    "some",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
    "yes",
    "you",
    "your",
}


def _english_word_score(text: str) -> int:
    """
    Calculate a simple English vocabulary score.

    This is intentionally lightweight and does not require
    another API call.
    """

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    if not words:
        return 0

    return sum(
        1
        for word in words
        if word in ENGLISH_WORDS
    )


def _looks_like_english(text: str) -> bool:
    """
    Determine whether Latin-script transcription strongly
    resembles English.

    This is especially useful for short phrases where Whisper
    may incorrectly identify the spoken language.
    """

    if not text:
        return False

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    if not words:
        return False

    english_score = _english_word_score(text)

    # Very strong signal:
    # one or more recognizable English words in a short sentence.
    if len(words) <= 8 and english_score >= 2:
        return True

    # For longer text, require a reasonable percentage
    # of recognizable English words.
    if len(words) >= 5:

        english_ratio = english_score / len(words)

        if english_ratio >= 0.45:
            return True

    return False


# ---------------------------------------------------------
# Language classification
# ---------------------------------------------------------

def _classify_transcription_language(
    text: str,
    whisper_language_code: str | None,
) -> str:
    """
    Determine the final user-facing language label.

    Priority:

    1. Urdu script in transcription
    2. Clear English text
    3. Mixed Urdu + English
    4. Whisper language detection
    5. Auto-detected
    """

    if not text:
        return "Auto-detected"

    cleaned_text = " ".join(text.split())

    urdu_count = _urdu_character_count(
        cleaned_text
    )

    latin_count = _latin_character_count(
        cleaned_text
    )

    has_urdu = urdu_count > 0
    has_latin = latin_count > 0

    # -----------------------------------------------------
    # Mixed Urdu + English
    # -----------------------------------------------------

    if has_urdu and has_latin:

        # If both scripts are meaningfully present,
        # classify as mixed speech.
        if urdu_count >= 3 and latin_count >= 3:
            return "Urdu + English"

    # -----------------------------------------------------
    # Urdu
    # -----------------------------------------------------

    if has_urdu:

        return "Urdu"

    # -----------------------------------------------------
    # English
    # -----------------------------------------------------

    if has_latin and _looks_like_english(
        cleaned_text
    ):

        return "English"

    # -----------------------------------------------------
    # Whisper fallback
    # -----------------------------------------------------

    if whisper_language_code:

        whisper_code = whisper_language_code.lower()

        if whisper_code == "ur":
            return "Urdu"

        if whisper_code == "en":
            return "English"

        # Do NOT expose Tagalog for a CivicAgent PK
        # Urdu/English voice complaint when the text itself
        # does not support that classification.
        #
        # Instead, fall back to the transcription language
        # only when Whisper is confident enough to identify
        # a known language.
        language_label = _detect_language_label(
            whisper_code
        )

        return language_label

    return "Auto-detected"


# ---------------------------------------------------------
# Transcription
# ---------------------------------------------------------

def transcribe_audio(uploaded_file) -> Dict[str, Any]:
    """
    Transcribe an uploaded/recorded audio file using
    Groq's Whisper Large V3 model.

    The input language is intentionally not supplied so that
    the system can handle Urdu, English, and mixed speech
    without requiring manual language selection.

    Language detection uses both:

    - Whisper's detected language
    - Transcribed text analysis

    Text analysis is prioritized for short recordings because
    Whisper can occasionally misclassify very short English
    phrases.
    """

    filename = getattr(
        uploaded_file,
        "name",
        "recording.wav",
    )

    base_result = {
        "success": False,
        "text": None,
        "language": None,
        "language_code": None,
        "source": "voice",
        "filename": filename,
        "error": None,
    }

    # -----------------------------------------------------
    # API key validation
    # -----------------------------------------------------

    if not GROQ_API_KEY:

        base_result["error"] = (
            "Groq API key is not configured. "
            "Please add GROQ_API_KEY to Streamlit Secrets."
        )

        return base_result

    try:

        # -------------------------------------------------
        # Groq client
        # -------------------------------------------------

        client = Groq(
            api_key=GROQ_API_KEY
        )

        # -------------------------------------------------
        # Read uploaded/recorded audio
        # -------------------------------------------------

        file_bytes = uploaded_file.getvalue()

        file_tuple = (
            filename,
            file_bytes,
        )

        # -------------------------------------------------
        # Whisper transcription
        # -------------------------------------------------

        transcription = (
            client.audio.transcriptions.create(
                file=file_tuple,
                model=MODEL_NAME,
                response_format="verbose_json",
                temperature=0.0,
            )
        )

        # -------------------------------------------------
        # Extract transcription text
        # -------------------------------------------------

        text = getattr(
            transcription,
            "text",
            "",
        ) or ""

        # -------------------------------------------------
        # Extract Whisper language
        # -------------------------------------------------

        language_code = getattr(
            transcription,
            "language",
            None,
        )

        # -------------------------------------------------
        # Clean transcription
        # -------------------------------------------------

        text = " ".join(
            text.split()
        )

        # -------------------------------------------------
        # Empty transcription
        # -------------------------------------------------

        if not text:

            base_result["error"] = (
                "No speech could be detected in the audio."
            )

            return base_result

        # -------------------------------------------------
        # Final language classification
        # -------------------------------------------------

        final_language = (
            _classify_transcription_language(
                text=text,
                whisper_language_code=language_code,
            )
        )

        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        base_result.update(
            {
                "success": True,
                "text": text,
                "language": final_language,
                "language_code": language_code,
            }
        )

        return base_result

    # -----------------------------------------------------
    # Error handling
    # -----------------------------------------------------

    except Exception as exc:

        error_message = str(
            exc
        ).strip()

        if not error_message:

            error_message = (
                "An unexpected transcription error occurred."
            )

        base_result["error"] = error_message

        return base_result
