import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        /* AI Debate Judge — restrained, theme-aware application styling. */

        :root {
            --adj-radius: 16px;
            --adj-radius-sm: 11px;
        }

        .stApp {
            background: var(--background-color);
            color: var(--text-color);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }

        /* Let Streamlit own the sidebar's active theme background. */
        [data-testid="stSidebar"] {
            border-right: 1px solid var(--border-color, rgba(128,128,128,.18));
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem;
        }

        .adj-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 0 1.5rem 0;
            color: var(--text-color);
            font-size: 1.05rem;
            font-weight: 750;
            letter-spacing: -.025em;
        }

        .adj-brand-mark {
            display: inline-flex;
            width: 34px;
            height: 34px;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: var(--primary-color);
            color: white;
            font-size: 17px;
        }

        .adj-section-label {
            margin: 1.35rem 0 .55rem;
            color: var(--text-color);
            opacity: .58;
            font-size: .70rem;
            font-weight: 700;
            letter-spacing: .11em;
            text-transform: uppercase;
        }

        .adj-eyebrow {
            color: var(--primary-color);
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .13em;
            text-transform: uppercase;
            margin-bottom: .65rem;
        }

        .adj-page-title {
            color: var(--text-color);
            font-size: clamp(2rem, 4vw, 3.15rem);
            font-weight: 780;
            line-height: 1.05;
            letter-spacing: -.055em;
            margin: 0;
        }

        .adj-page-subtitle {
            max-width: 720px;
            margin-top: .85rem;
            color: var(--text-color);
            opacity: .68;
            font-size: 1.02rem;
            line-height: 1.65;
        }

        .adj-card {
            background: var(--secondary-background-color);
            color: var(--text-color);
            border: 1px solid var(--border-color, rgba(128,128,128,.20));
            border-radius: var(--adj-radius);
            padding: 1.25rem 1.35rem;
        }

        .adj-card-label {
            color: var(--text-color);
            opacity: .58;
            font-size: .70rem;
            font-weight: 750;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .5rem;
        }

        .adj-winner {
            font-size: clamp(1.65rem, 3vw, 2.25rem);
            font-weight: 800;
            letter-spacing: -.045em;
            line-height: 1.1;
            color: var(--text-color);
            margin: .2rem 0 .65rem;
            overflow-wrap: anywhere;
        }

        .adj-muted {
            color: var(--text-color);
            opacity: .65;
            font-size: .86rem;
            line-height: 1.5;
        }

        .adj-file-note {
            color: var(--text-color);
            opacity: .62;
            font-size: .82rem;
            line-height: 1.5;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            min-height: 2.65rem;
            font-weight: 600;
            transition: border-color .15s ease, filter .15s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.06);
            border-color: var(--primary-color);
        }

        [data-testid="stFileUploader"] {
            border: 1px dashed var(--border-color, rgba(128,128,128,.4));
            border-radius: 13px;
            padding: .9rem;
            background: var(--background-color);
        }

        [data-testid="stFileUploaderDropzone"] {
            border: 0;
            background: transparent;
        }

        [data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid var(--border-color, rgba(128,128,128,.2));
            border-radius: 13px;
            padding: .9rem 1rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color, rgba(128,128,128,.2));
            border-radius: 12px;
            overflow: hidden;
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--border-color, rgba(128,128,128,.2));
            border-radius: 12px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }

        @media (max-width: 760px) {
            .block-container {
                padding: 1.4rem 1rem 3rem;
            }
            .adj-page-title {
                font-size: 2.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
