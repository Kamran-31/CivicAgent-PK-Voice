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
        background: #e9eef3;
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
            #0d4352 0%,
            #155f76 55%,
            #197d96 100%
        );

        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;

        box-shadow:
            0 8px 22px rgba(15, 76, 92, 0.20);
    }

    .hero-title {
        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
    }

    .hero-subtitle {
        display: none;
    }

    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-title {
        color: #173f50;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.28rem;
        font-weight: 750;

        letter-spacing: -0.015em;

        margin-top: 0.55rem;
        margin-bottom: 0.45rem;
    }

    /* =====================================================
       INPUT CARDS
       ===================================================== */

    .input-card {
        background: #ffffff;

        border: 1px solid #d6e0e7;
        border-radius: 14px;

        padding: 1rem 1.15rem;

        min-height: 0;

        box-shadow:
            0 3px 10px rgba(15, 23, 42, 0.055);

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease;
    }

    .input-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 7px 18px rgba(15, 23, 42, 0.09);
    }

    .card-title {
        color: #173f50;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.04rem;
        font-weight: 750;

        margin-bottom: 0.25rem;
    }

    .card-description {
        color: #64748b;

        font-size: 0.86rem;

        line-height: 1.45;

        margin-bottom: 0;
    }

    /* =====================================================
       STREAMLIT INPUT LABELS
       ===================================================== */

    label {
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* =====================================================
       AUDIO PREVIEW
       ===================================================== */

    .audio-preview-title {
        color: #173f50;

        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;

        font-size: 1.05rem;
        font-weight: 700;

        margin-top: 1.1rem;
        margin-bottom: 0.35rem;
    }

    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {
        background: #ffffff;

        border: 1px solid #d5e1e8;
        border-radius: 15px;

        padding: 1.25rem;

        margin-top: 1rem;

        box-shadow:
            0 5px 17px rgba(15, 23, 42, 0.07);
    }

    .result-label {
        color: #64748b;

        font-size: 0.76rem;
        font-weight: 700;

        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    .transcription-text {
        background: #f4f8fa;

        border-left: 4px solid #19829b;

        border-radius: 8px;

        padding: 1rem;

        margin-top: 0.55rem;

        color: #1e293b;

        font-size: 1.02rem;

        line-height: 1.85;

        direction: auto;

        box-shadow:
            inset 0 0 0 1px rgba(15, 76, 92, 0.04);
    }

    /* =====================================================
       BUTTONS
       ===================================================== */

    div.stButton > button {
        border-radius: 9px;

        font-family:
            "Segoe UI",
            sans-serif;

        font-weight: 700;

        min-height: 2.65rem;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 5px 12px rgba(15, 76, 92, 0.15);
    }

    div.stDownloadButton > button {
        border-radius: 9px;

        font-weight: 700;

        min-height: 2.55rem;
    }

    /* =====================================================
       STATUS MESSAGES
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #718096;

        font-size: 0.78rem;

        margin-top: 2.2rem;
        padding-top: 1rem;

        border-top: 1px solid #cfd9e1;

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
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Submit complaint section
# ---------------------------------------------------------

st.markdown(
    """
    <div class="section-title">
        Submit a Voice Complaint
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
                Record a citizen complaint directly through your
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
        <div class="audio-preview-title">
            Audio Preview
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
                    """
                    <div class="result-card">
                    """,
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

                    st.write(
                        result["language"]
                        or "Auto-detected"
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

                    st.write("Voice")

                st.markdown(
                    """
                    <div class="result-label">
                        Transcription
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="transcription-text">
                        {result["text"]}
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
