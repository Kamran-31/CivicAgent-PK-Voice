import html

import streamlit as st

from audio_utils import validate_audio_file
from transcription import transcribe_audio


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CivicAgent PK | Voice-to-Text",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# Custom styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: #f5f7fb;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2.5rem;
    }

    /* =====================================================
       TYPOGRAPHY
       ===================================================== */

    html,
    body,
    [class*="css"] {
        font-family:
            "Inter",
            "Segoe UI",
            Roboto,
            Helvetica,
            Arial,
            sans-serif;
    }

    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        background: linear-gradient(
            135deg,
            #0f4c5c 0%,
            #176b87 55%,
            #1b8ca8 100%
        );

        padding: 2rem 2.3rem;

        border-radius: 18px;

        color: white;

        margin-bottom: 1.6rem;

        box-shadow:
            0 10px 28px rgba(15, 76, 92, 0.20);
    }

    .hero-title {
        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 2.2rem;

        font-weight: 800;

        letter-spacing: -0.025em;

        margin: 0;
    }

    .hero-subtitle {
        font-size: 0.98rem;

        opacity: 0.92;

        line-height: 1.5;

        margin-top: 0.3rem;
    }

    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-title {
        color: #163a4a;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.28rem;

        font-weight: 750;

        letter-spacing: -0.015em;

        margin-top: 0.4rem;

        margin-bottom: 0.4rem;
    }

    .section-caption {
        color: #64748b;

        font-size: 0.9rem;

        line-height: 1.5;

        margin-bottom: 0.9rem;
    }

    /* =====================================================
       INPUT CARDS
       ===================================================== */

    .input-card {
        background: #ffffff;

        border: 1px solid #d9e3ea;

        border-radius: 15px;

        padding: 1.15rem 1.2rem;

        min-height: 112px;

        box-shadow:
            0 4px 14px rgba(15, 23, 42, 0.055);

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    .input-card:hover {
        transform: translateY(-2px);

        border-color: #b9d2dc;

        box-shadow:
            0 8px 20px rgba(15, 23, 42, 0.09);
    }

    .card-title {
        color: #163a4a;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.05rem;

        font-weight: 750;

        margin-bottom: 0.3rem;
    }

    .card-description {
        color: #64748b;

        font-size: 0.87rem;

        line-height: 1.5;

        margin: 0;
    }

    /* =====================================================
       STREAMLIT LABELS
       ===================================================== */

    label {
        color: #334155 !important;

        font-weight: 600 !important;
    }

    /* =====================================================
       AUDIO PREVIEW
       ===================================================== */

    .preview-header {
        display: flex;

        align-items: center;

        gap: 0.45rem;

        color: #163a4a;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.08rem;

        font-weight: 750;

        margin-top: 1.1rem;

        margin-bottom: 0.45rem;
    }

    /* =====================================================
       TRANSCRIBE BUTTON
       ===================================================== */

    div.stButton > button {
        border-radius: 10px;

        font-family:
            "Segoe UI",
            sans-serif;

        font-size: 0.95rem;

        font-weight: 700;

        min-height: 2.8rem;

        border: none;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 6px 14px rgba(15, 76, 92, 0.18);
    }

    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {
        background: #ffffff;

        border: 1px solid #d6e2e9;

        border-radius: 16px;

        padding: 1.35rem;

        margin-top: 0.9rem;

        box-shadow:
            0 6px 20px rgba(15, 23, 42, 0.07);
    }

    .result-header {
        color: #163a4a;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.08rem;

        font-weight: 750;

        margin-bottom: 1rem;
    }

    .result-label {
        color: #64748b;

        font-size: 0.75rem;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 0.07em;

        margin-bottom: 0.25rem;
    }

    .result-value {
        color: #1e293b;

        font-size: 0.95rem;

        font-weight: 600;
    }

    .transcription-label {
        color: #64748b;

        font-size: 0.75rem;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 0.07em;

        margin-top: 1rem;

        margin-bottom: 0.45rem;
    }

    .transcription-text {
        background: #f5f8fa;

        border: 1px solid #e1e9ee;

        border-left: 4px solid #1b8ca8;

        border-radius: 9px;

        padding: 1rem 1.05rem;

        color: #1e293b;

        font-size: 1.03rem;

        line-height: 1.85;

        direction: auto;

        word-wrap: break-word;

        overflow-wrap: anywhere;
    }

    /* =====================================================
       DOWNLOAD BUTTON
       ===================================================== */

    div.stDownloadButton > button {
        border-radius: 9px;

        font-weight: 700;

        min-height: 2.55rem;

        margin-top: 0.25rem;
    }

    /* =====================================================
       STATUS MESSAGES
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* =====================================================
       FILE CAPTION
       ===================================================== */

    div[data-testid="stCaptionContainer"] {
        color: #718096;
    }

    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #7b8794;

        font-size: 0.78rem;

        margin-top: 2.1rem;

        padding-top: 1rem;

        border-top: 1px solid #d5dee5;

        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Hero
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            🎙️ CivicAgent PK
        </div>
        <div class="hero-subtitle">
            Voice-to-Text Complaint Module<br>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Introduction
# ---------------------------------------------------------

st.markdown(
    """
    <div class="section-title">
        Submit a Voice Complaint
    </div>

    <div class="section-caption">
        Record a new complaint or upload an existing voice note.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Input methods
# ---------------------------------------------------------

col1, col2 = st.columns(2, gap="large")


with col1:

    st.markdown(
        """
        <div class="input-card">
            <div class="card-title">
                🎙️ Record Complaint
            </div>
            <div class="card-description">
                Record a complaint directly through your
                device microphone.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recorded_audio = st.audio_input(
        "Record your complaint",
        sample_rate=16000,
        help="Speak clearly and describe the public issue.",
    )


with col2:

    st.markdown(
        """
        <div class="input-card">
            <div class="card-title">
                📁 Upload Voice Note
            </div>
            <div class="card-description">
                Upload an existing audio recording in MP3, WAV,
                M4A, or WEBM format.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_audio = st.file_uploader(
        "Choose an audio file",
        type=["mp3", "wav", "m4a", "webm"],
        help="Maximum supported file size: 25 MB.",
    )


# ---------------------------------------------------------
# Select input
# ---------------------------------------------------------

audio_input = (
    recorded_audio
    if recorded_audio is not None
    else uploaded_audio
)


if recorded_audio is not None and uploaded_audio is not None:

    st.info(
        "Both recording and upload were provided. "
        "The recorded audio will be used."
    )


# ---------------------------------------------------------
# Audio preview
# ---------------------------------------------------------

if audio_input is not None:

    st.markdown(
        """
        <div class="preview-header">
            🔊 Audio Preview
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.audio(audio_input)

    filename = getattr(
        audio_input,
        "name",
        "recording.wav",
    )

    st.caption(
        f"Selected file: {filename}"
    )


# ---------------------------------------------------------
# Transcription button
# ---------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

transcribe_clicked = st.button(
    "✨ Transcribe Complaint",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# Transcription process
# ---------------------------------------------------------

if transcribe_clicked:

    if audio_input is None:

        st.warning(
            "Please record a complaint or upload an audio file first."
        )

    else:

        is_valid, validation_error = validate_audio_file(
            audio_input
        )

        if not is_valid:

            st.error(validation_error)

        else:

            with st.spinner(
                "Transcribing audio with Whisper Large V3..."
            ):

                result = transcribe_audio(
                    audio_input
                )

            if result["success"]:

                st.success(
                    "Transcription completed successfully."
                )

               st.markdown(
                    '<div class="result-card">'
                        '<div class="result-header">'
                        '📄 Complaint Transcription'
                    '</div>',
                    unsafe_allow_html=True,
                )

                meta_col1, meta_col2 = st.columns(2)

                with meta_col1:

                    st.markdown(
                        """
                        <div class="result-label">
                            Language
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"""
                        <div class="result-value">
                            {html.escape(
                                result["language"]
                                or "Auto-detected"
                            )}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with meta_col2:

                    st.markdown(
                        """
                        <div class="result-label">
                            Source
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        """
                        <div class="result-value">
                            Voice
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    """
                    <div class="transcription-label">
                        Transcription
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                safe_text = html.escape(
                    result["text"]
                )

                st.markdown(
                    f"""
                    <div class="transcription-text">
                        {safe_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

                st.download_button(
                    label="⬇️ Download Transcription",
                    data=result["text"],
                    file_name="complaint_transcription.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            else:

                st.error(
                    "Transcription could not be completed."
                )

                if result["error"]:

                    st.warning(
                        result["error"]
                    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        CivicAgent PK · Autonomous Public Grievance & Legal Workflow Engine
        <br>
        Voice-to-Text powered by Groq Whisper Large V3
    </div>
    """,
    unsafe_allow_html=True,
)
