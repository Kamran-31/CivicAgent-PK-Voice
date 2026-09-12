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

    /* Main application */
    .stApp {
        background: #f5f7fb;
    }

    /* Main content width */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero section */
    .hero {
        background: linear-gradient(
            135deg,
            #0f4c5c 0%,
            #176b87 55%,
            #1b8ca8 100%
        );
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 24px rgba(15, 76, 92, 0.18);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 750;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        line-height: 1.6;
    }

    /* Section headings */
    .section-title {
        color: #163a4a;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.8rem;
        margin-bottom: 0.7rem;
    }

    /* Input cards */
    .input-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 1.3rem;
        min-height: 190px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }

    .card-title {
        color: #163a4a;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .card-description {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    /* Result card */
    .result-card {
        background: white;
        border: 1px solid #d9e3ea;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1.2rem;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.06);
    }

    .result-label {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .transcription-text {
        background: #f8fafc;
        border-left: 4px solid #1b8ca8;
        border-radius: 8px;
        padding: 1.15rem;
        margin-top: 0.7rem;
        color: #1e293b;
        font-size: 1.05rem;
        line-height: 1.8;
        direction: auto;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid #e2e8f0;
    }

    /* Primary buttons */
    div.stButton > button {
        border-radius: 9px;
        font-weight: 650;
        min-height: 2.7rem;
    }

    /* Download button */
    div.stDownloadButton > button {
        border-radius: 9px;
        font-weight: 650;
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
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Record a new complaint or upload an existing voice note. "
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

audio_input = recorded_audio if recorded_audio is not None else uploaded_audio

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
        <div class="section-title">
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

    st.caption(f"Selected file: {filename}")


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
                result = transcribe_audio(audio_input)

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
                        '<div class="result-label">Language</div>',
                        unsafe_allow_html=True,
                    )
                    st.write(
                        result["language"] or "Auto-detected"
                    )

                with meta_col2:
                    st.markdown(
                        '<div class="result-label">Source</div>',
                        unsafe_allow_html=True,
                    )
                    st.write("Voice")

                st.markdown(
                    '<div class="result-label">Transcription</div>',
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

                st.markdown("</div>", unsafe_allow_html=True)

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
                    st.warning(result["error"])


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
