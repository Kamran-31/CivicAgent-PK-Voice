import re
from typing import Any, Dict

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
    }

    if not language_code:
        return "Unknown"

    return language_map.get(
        language_code.lower(),
        language_code.upper(),
    )


# ---------------------------------------------------------
# Urdu script detection
# ---------------------------------------------------------

def _urdu_character_count(text: str) -> int:
    """
    Count Urdu/Arabic-script characters.
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
# English detection
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


def _english_score(text: str) -> int:
    """
    Count recognizable English words.
    """

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    return sum(
        1
        for word in words
        if word in ENGLISH_WORDS
    )


def _looks_like_english(text: str) -> bool:
    """
    Determine whether text is likely English.
    """

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    if not words:
        return False

    score = _english_score(text)

    # Very short sentences.
    #
    # Example:
    # "Hello, how are you?"
    #
    # hello = English
    # how   = English
    # are   = English
    # you   = English
    if len(words) <= 8 and score >= 2:
        return True

    # Longer English text.
    if len(words) >= 5:

        ratio = score / len(words)

        if ratio >= 0.45:
            return True

    return False


# ---------------------------------------------------------
# Roman Urdu detection
# ---------------------------------------------------------

ROMAN_URDU_WORDS = {
    "mein",
    "main",
    "mujhe",
    "mujhay",
    "mera",
    "meri",
    "mere",
    "hum",
    "ham",
    "aap",
    "ap",
    "apka",
    "apki",
    "apke",
    "hai",
    "hain",
    "tha",
    "thi",
    "the",
    "ho",
    "hun",
    "houn",
    "kar",
    "karo",
    "karen",
    "karta",
    "karti",
    "karte",
    "raha",
    "rahi",
    "rahe",
    "raha",
    "nahi",
    "nahin",
    "nai",
    "ka",
    "ki",
    "ke",
    "ko",
    "se",
    "par",
    "pe",
    "yeh",
    "yah",
    "woh",
    "wo",
    "kya",
    "kyun",
    "kyon",
    "kab",
    "kahan",
    "kidhar",
    "kaise",
    "aisa",
    "aisi",
    "aisay",
    "bohat",
    "bahut",
    "acha",
    "achha",
    "achi",
    "achhi",
    "acha",
    "pani",
    "paani",
    "bijli",
    "masla",
    "shikayat",
    "gali",
    "sadak",
    "mohalla",
    "ghar",
    "school",
    "hospital",
    "awam",
    "log",
    "mera",
    "hamara",
    "hamari",
    "hamare",
    "madad",
    "chahiye",
    "chahta",
    "chahti",
    "kripya",
    "please",
}


def _roman_urdu_score(text: str) -> int:
    """
    Count common Roman Urdu words.
    """

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    return sum(
        1
        for word in words
        if word in ROMAN_URDU_WORDS
    )


def _looks_like_roman_urdu(text: str) -> bool:
    """
    Determine whether Latin-script text is likely Roman Urdu.

    Roman Urdu has no single official spelling system, so
    vocabulary-based detection is used instead of relying
    entirely on Whisper's language code.
    """

    words = re.findall(
        r"[A-Za-z]+",
        text.lower(),
    )

    if not words:
        return False

    score = _roman_urdu_score(text)

    # Strong signal for short phrases.
    if len(words) <= 8 and score >= 2:
        return True

    # Longer Roman Urdu.
    if len(words) >= 5:

        ratio = score / len(words)

        if ratio >= 0.30:
            return True

    return False


# ---------------------------------------------------------
# Final language classification
# ---------------------------------------------------------

def _classify_transcription_language(
    text: str,
    whisper_language_code: str | None,
) -> str:
    """
    Classify transcription into the four supported categories:

        English
        Urdu
        Roman Urdu
        Urdu + English

    Any other language is rejected.
    """

    if not text:
        return "Unknown"

    text = " ".join(
        text.split()
    )

    urdu_count = _urdu_character_count(text)
    latin_count = _latin_character_count(text)

    has_urdu_script = urdu_count > 0
    has_latin = latin_count > 0

    # -----------------------------------------------------
    # Urdu + English
    # -----------------------------------------------------

    if has_urdu_script and has_latin:

        if urdu_count >= 3 and latin_count >= 3:
            return "Urdu + English"

        if urdu_count > 0:
            return "Urdu"

    # -----------------------------------------------------
    # Urdu
    # -----------------------------------------------------

    if has_urdu_script:
        return "Urdu"

    # -----------------------------------------------------
    # Latin-script text
    # -----------------------------------------------------

    if has_latin:

        roman_urdu = _looks_like_roman_urdu(text)
        english = _looks_like_english(text)

        # If both appear possible, use Whisper as an
        # additional signal.
        if roman_urdu and english:

            if whisper_language_code:

                code = whisper_language_code.lower()

                if code == "en":
                    return "English"

            return "Roman Urdu"

        if roman_urdu:
            return "Roman Urdu"

        if english:
            return "English"

    # -----------------------------------------------------
    # Whisper fallback
    # -----------------------------------------------------

    if whisper_language_code:

        code = whisper_language_code.lower()

        if code == "ur":
            return "Urdu"

        if code == "en":
            return "English"

    # -----------------------------------------------------
    # Unsupported language
    # -----------------------------------------------------

    return "Unsupported"


# ---------------------------------------------------------
# Transcription
# ---------------------------------------------------------

def transcribe_audio(uploaded_file) -> Dict[str, Any]:
    """
    Transcribe an uploaded/recorded audio file using
    Groq's Whisper Large V3 model.

    Supported languages:

        English
        Urdu
        Roman Urdu
        Urdu + English

    Other languages are rejected.
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
    # API key
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
        # Audio
        # -------------------------------------------------

        file_bytes = uploaded_file.getvalue()

        file_tuple = (
            filename,
            file_bytes,
        )

        # -------------------------------------------------
        # Whisper
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
        # Text
        # -------------------------------------------------

        text = getattr(
            transcription,
            "text",
            "",
        ) or ""

        text = " ".join(
            text.split()
        )

        # -------------------------------------------------
        # Whisper language
        # -------------------------------------------------

        language_code = getattr(
            transcription,
            "language",
            None,
        )

        # -------------------------------------------------
        # Empty audio
        # -------------------------------------------------

        if not text:

            base_result["error"] = (
                "No speech could be detected in the audio."
            )

            return base_result

        # -------------------------------------------------
        # Language classification
        # -------------------------------------------------

        final_language = (
            _classify_transcription_language(
                text=text,
                whisper_language_code=language_code,
            )
        )

        # -------------------------------------------------
        # Reject unsupported languages
        # -------------------------------------------------

        if final_language == "Unsupported":

            base_result["error"] = (
                "Unsupported language detected. "
                "CivicAgent PK currently supports only "
                "English, Urdu, Roman Urdu, and Urdu + English."
            )

            base_result["text"] = text
            base_result["language_code"] = language_code

            return base_result

        # -------------------------------------------------
        # Success
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
