import os

import httpx
import streamlit as st

from ui.components.styles import inject_css


API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AI Debate Judge",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

DEFAULTS = {
    "user_id": None,
    "email": None,
    "selected_debate": None,
    "pending_delete_id": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.user_id:
        headers["X-User-ID"] = str(st.session_state.user_id)

    with httpx.Client(timeout=390) as client:
        response = client.request(
            method,
            API + path,
            headers=headers,
            **kwargs,
        )

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(detail)

    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def page_heading(eyebrow, title, subtitle):
    st.markdown(
        f"""
        <div class="adj-eyebrow">{eyebrow}</div>
        <h1 class="adj-page-title">{title}</h1>
        <p class="adj-page-subtitle">{subtitle}</p>
        """,
        unsafe_allow_html=True,
    )


def auth_screen():
    page_heading(
        "LOCAL-FIRST DEBATE ANALYSIS",
        "AI Debate Judge",
        "Structured adjudication for two-sided English debates, "
        "powered by your locally running Ollama model.",
    )

    st.write("")
    left, right = st.columns(2, gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Welcome back")
            st.caption("Sign in to access your debate workspace.")

            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                try:
                    data = api(
                        "POST",
                        "/auth/login",
                        json={"email": email, "password": password},
                    )
                    st.session_state.user_id = data["user_id"]
                    st.session_state.email = data["email"]
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with right:
        with st.container(border=True):
            st.subheader("Create your account")
            st.caption("Create an account to keep your debate history.")

            with st.form("register_form"):
                email = st.text_input("Email", key="register_email")
                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                )
                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                )

            if submitted:
                try:
                    data = api(
                        "POST",
                        "/auth/register",
                        json={"email": email, "password": password},
                    )
                    st.session_state.user_id = data["user_id"]
                    st.session_state.email = data["email"]
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="adj-brand">
                <span class="adj-brand-mark">⚖</span>
                <span>AI Debate Judge</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "＋  New debate",
            type="primary",
            use_container_width=True,
            key="new_debate",
        ):
            st.session_state.selected_debate = None
            st.session_state.pending_delete_id = None
            st.rerun()

        st.markdown(
            '<div class="adj-section-label">Your workspace</div>',
            unsafe_allow_html=True,
        )
        st.caption("DEBATE HISTORY")

        try:
            debates = api("GET", "/debates") or []
        except Exception as exc:
            st.error(f"Could not load history: {exc}")
            debates = []

        if not debates:
            st.caption("Your saved debates will appear here.")
        else:
            for debate in debates:
                debate_id = debate["id"]
                title = debate.get("title") or "Untitled debate"
                selected = st.session_state.selected_debate == debate_id

                open_col, menu_col = st.columns([0.82, 0.18], gap="small")
                with open_col:
                    button_label = ("●  " if selected else "") + title
                    if st.button(
                        button_label,
                        key=f"open_debate_{debate_id}",
                        use_container_width=True,
                        type="primary" if selected else "secondary",
                        help=title,
                    ):
                        st.session_state.selected_debate = debate_id
                        st.session_state.pending_delete_id = None
                        st.rerun()

                with menu_col:
                    if st.button(
                        "⋯",
                        key=f"menu_debate_{debate_id}",
                        use_container_width=True,
                        help="Debate actions",
                    ):
                        st.session_state.pending_delete_id = (
                            None
                            if st.session_state.pending_delete_id == debate_id
                            else debate_id
                        )
                        st.rerun()

                if st.session_state.pending_delete_id == debate_id:
                    with st.container(border=True):
                        st.caption("DEBATE ACTIONS")
                        st.write("Delete this debate permanently?")
                        delete_col, cancel_col = st.columns(2)
                        with delete_col:
                            if st.button(
                                "Delete",
                                key=f"confirm_delete_{debate_id}",
                                type="primary",
                                use_container_width=True,
                            ):
                                try:
                                    api("DELETE", f"/debates/{debate_id}")
                                    if st.session_state.selected_debate == debate_id:
                                        st.session_state.selected_debate = None
                                    st.session_state.pending_delete_id = None
                                    st.toast("Debate deleted.")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"Could not delete debate: {exc}")
                        with cancel_col:
                            if st.button(
                                "Cancel",
                                key=f"cancel_delete_{debate_id}",
                                use_container_width=True,
                            ):
                                st.session_state.pending_delete_id = None
                                st.rerun()

        st.divider()
        st.caption("SIGNED IN")
        st.markdown(f"**{st.session_state.email or 'User'}**")

        if st.button("Sign out", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.email = None
            st.session_state.selected_debate = None
            st.session_state.pending_delete_id = None
            st.rerun()


def upload_page():
    page_heading(
        "NEW EVALUATION",
        "Judge a debate.",
        "Upload one transcript. The system extracts arguments, maps clashes "
        "and rebuttals, then produces an explicit adjudication with a "
        "traceable scorecard.",
    )

    st.write("")
    with st.container(border=True):
        st.subheader("Upload your transcript")
        st.caption(
            "Choose a TXT, DOCX or PDF file containing both sides of the debate."
        )

        uploaded = st.file_uploader(
            "Choose a transcript",
            type=["txt", "docx", "pdf"],
            help="TXT up to 10 MB · DOCX up to 10 MB · PDF up to 25 MB",
        )

        st.markdown(
            '<p class="adj-file-note">Supported: TXT (10 MB), DOCX (10 MB), '
            'PDF (25 MB) · English · two sides</p>',
            unsafe_allow_html=True,
        )

        if uploaded:
            st.success(f"File ready: {uploaded.name} · {uploaded.size:,} bytes")
            default_title = uploaded.name.rsplit(".", 1)[0][:120]
            title = st.text_input(
                "Debate title",
                value=default_title,
                max_chars=300,
            )

            if st.button(
                "Analyze debate  →",
                type="primary",
                use_container_width=True,
                disabled=not title.strip(),
            ):
                with st.spinner(
                    "The local judge is analyzing the debate. "
                    "This may take several minutes..."
                ):
                    try:
                        content = uploaded.getvalue()
                        from app.services.file_ingestion import extract_text

                        transcript = extract_text(uploaded.name, content)
                        result = api(
                            "POST",
                            "/debates",
                            json={
                                "title": title.strip(),
                                "transcript": transcript,
                            },
                        )
                        st.session_state.selected_debate = result["id"]
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))


def _clash_display_rows(decision: dict, analysis: dict) -> list[dict]:
    """Join Stage 2 clash findings to Stage 1 clashes by clash_id."""
    stage1_clashes = analysis.get("clashes", [])
    stage2_clashes = decision.get("clash_results", [])

    if not isinstance(stage1_clashes, list):
        stage1_clashes = []
    if not isinstance(stage2_clashes, list):
        stage2_clashes = []

    stage2_by_id = {}
    for item in stage2_clashes:
        if not isinstance(item, dict):
            continue
        clash_id = str(item.get("clash_id", "")).strip()
        if clash_id:
            stage2_by_id[clash_id] = item

    rows = []
    seen_ids = set()

    for clash in stage1_clashes:
        if not isinstance(clash, dict):
            continue
        clash_id = str(clash.get("clash_id", "")).strip()
        if not clash_id:
            continue

        result = stage2_by_id.get(clash_id, {})
        finding = (
            result.get("finding")
            or result.get("resolution")
            or result.get("explanation")
            or result.get("analysis")
            or ""
        )
        rows.append(
            {
                "clash_id": clash_id,
                "issue": str(clash.get("issue", "")).strip(),
                "description": str(clash.get("description", "")).strip(),
                "finding": str(finding).strip(),
                "decisive": bool(result.get("decisive", False)),
            }
        )
        seen_ids.add(clash_id)

    for clash_id, result in stage2_by_id.items():
        if clash_id in seen_ids:
            continue
        finding = (
            result.get("finding")
            or result.get("resolution")
            or result.get("explanation")
            or result.get("analysis")
            or ""
        )
        rows.append(
            {
                "clash_id": clash_id,
                "issue": str(result.get("issue", "")).strip(),
                "description": "",
                "finding": str(finding).strip(),
                "decisive": bool(result.get("decisive", False)),
            }
        )

    return rows


def result_page(debate_id: int):
    try:
        debate = api("GET", f"/debates/{debate_id}")
    except Exception as exc:
        st.error(f"Could not load this debate: {exc}")
        if st.button("Return to new debate"):
            st.session_state.selected_debate = None
            st.rerun()
        return

    result = debate.get("result") or {}
    if "error" in result:
        st.error(result["error"])
        return

    decision = result.get("decision", {})
    analysis = result.get("analysis", {})
    scores = decision.get("scores", {})
    winner = decision.get("winner", "UNRESOLVED")
    status = decision.get("decision_status", "unknown")
    confidence = decision.get("confidence", "unknown")

    page_heading(
        "DEBATE REPORT",
        "Decision",
        decision.get("deciding_issue", "No deciding issue recorded."),
    )

    st.write("")
    st.caption(debate.get("title", "Untitled debate"))

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="adj-card">
                <div class="adj-card-label">ADJUDICATED WINNER</div>
                <div class="adj-winner">{winner}</div>
                <div class="adj-muted">
                    Status: {status} &nbsp;·&nbsp; Confidence: {confidence}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        score_a = scores.get("A", {}).get("total", "—")
        score_b = scores.get("B", {}).get("total", "—")
        metric_a, metric_b = st.columns(2)
        with metric_a:
            st.metric("Side A", score_a)
        with metric_b:
            st.metric("Side B", score_b)

    st.write("")
    st.subheader("Scorecard")
    score_rows = []
    for dimension in [
        "reasoning",
        "clash",
        "weighing",
        "clarity",
        "strategy",
        "persuasion",
    ]:
        score_rows.append(
            {
                "Dimension": dimension.title(),
                "Side A": scores.get("A", {}).get(dimension, "—"),
                "Side B": scores.get("B", {}).get(dimension, "—"),
            }
        )
    st.dataframe(
        score_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.write("")
    st.subheader("Deciding issue")
    st.info(decision.get("deciding_issue", "Not available."))

    clashes_col, explanation_col = st.columns(2, gap="large")

    with clashes_col:
        st.subheader("Key clashes")
        clash_rows = _clash_display_rows(decision, analysis)

        if not clash_rows:
            st.caption("No clashes were extracted from this debate.")

        for clash in clash_rows:
            heading = clash["clash_id"]
            if clash["issue"]:
                heading += f" · {clash['issue']}"
            if clash["decisive"]:
                heading += " · Decisive"

            with st.container(border=True):
                st.markdown(f"**{heading}**")
                if clash["finding"]:
                    st.write(clash["finding"])
                elif clash["description"]:
                    st.write(clash["description"])
                    st.caption(
                        "Stage 2 did not return a separate finding for this clash."
                    )
                else:
                    st.caption(
                        "No Stage 2 finding or Stage 1 description is available."
                    )

    with explanation_col:
        st.subheader("Judge's explanation")
        explanation_points = decision.get("explanation_points", [])
        if explanation_points:
            for point in explanation_points:
                st.markdown(f"- {point}")
        else:
            st.caption("No explanation points were returned.")

    with st.expander("View full argument analysis"):
        st.json(analysis)

    with st.expander("View full transcript"):
        st.text(debate.get("transcript", ""))


if not st.session_state.user_id:
    auth_screen()
else:
    sidebar()
    if st.session_state.selected_debate:
        result_page(st.session_state.selected_debate)
    else:
        upload_page()
