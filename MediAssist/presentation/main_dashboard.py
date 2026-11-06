import html

import streamlit as st
from presentation.document_panel import render_document_panel
from presentation.chatbot import render_chatbot
from presentation.image_upload_panel import render_image_upload_panel


# --------------------------------------------------
# STYLES (injected on EVERY rerun, see main())
# --------------------------------------------------
DASHBOARD_CSS = """
:root {
    --bg: #F4F7FB;
    --surface: #FFFFFF;
    --border: #E4EBF3;
    --text: #18334D;
    --muted: #7B8DA2;
    --primary: #087F8C;
    --primary-soft: #DDF5F0;
}

.stApp { background: var(--bg); color: var(--text); }

.block-container {
    max-width: 1600px;
    padding: 1.25rem 2rem 2.5rem;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* ================= NAVBAR ================= */
.st-key-navbar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 24px;
    box-shadow: 0 4px 20px rgba(20, 52, 80, 0.05);
}

.st-key-navbar [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 0.75rem;
}
.st-key-navbar [data-testid="stElementContainer"],
.st-key-navbar [data-testid="stMarkdownContainer"],
.st-key-navbar [data-testid="stMarkdownContainer"] p {
    margin: 0;
}

/* brand */
.med-brand { display: flex; align-items: center; gap: 14px; }

.med-logo {
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, #087F8C, #20B5A5);
    box-shadow: 0 4px 12px rgba(8, 127, 140, 0.30);
}

.med-brand-name {
    color: #14334F;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.med-brand-subtitle {
    color: var(--muted);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin-top: 2px;
}

/* ---------- USER PANEL (grid) ----------
   col 1: avatar (spans 2 rows)    col 2: label + name  /  logout button   */
.st-key-user_panel {
    display: grid !important;
    grid-template-columns: 44px max-content;
    grid-template-rows: auto auto;
    column-gap: 12px;
    row-gap: 6px;
    justify-content: end;      /* push whole block to the right edge */
    align-items: center;
    width: 100%;
}

/* avatar */
.st-key-user_panel > [data-testid="stElementContainer"]:nth-child(1) {
    grid-column: 1;
    grid-row: 1 / span 2;
    width: 44px;
}
.med-user-avatar {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--primary-soft);
    color: var(--primary);
    font-size: 18px;
    font-weight: 800;
}

/* label + name */
.st-key-user_panel > [data-testid="stElementContainer"]:nth-child(2) {
    grid-column: 2;
    grid-row: 1;
}
.med-user-label {
    color: var(--muted);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.6px;
    line-height: 1.2;
}
.med-user-name {
    color: #193750;
    font-size: 14px;
    font-weight: 700;
    line-height: 1.3;
    overflow-wrap: anywhere;
}

/* logout button: small, left-aligned with the username */
.st-key-user_panel > [data-testid="stElementContainer"]:nth-child(3) {
    grid-column: 2;
    grid-row: 2;
    width: auto !important;
    justify-self: start;
}
.st-key-dashboard_logout { width: auto !important; }
.st-key-dashboard_logout button {
    width: auto;
    min-height: 0;
    height: 26px;
    padding: 0 12px;
    gap: 6px;
    border-radius: 999px;
    border: 1px solid #D5DFEA;
    background: var(--surface);
    color: #3A566F;
    transition: all 0.15s ease;
}
.st-key-dashboard_logout button p {
    margin: 0;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
}
.st-key-dashboard_logout button [data-testid="stIconMaterial"] {
    font-size: 15px;
}
.st-key-dashboard_logout button:hover,
.st-key-dashboard_logout button:focus:not(:active) {
    border-color: #E5484D;
    color: #E5484D;
    background: #FFF5F5;
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(165deg, #102C45 0%, #123C55 58%, #105767 100%);
    border-right: 1px solid #25485F;
}
section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }
section[data-testid="stSidebar"] hr { border-color: rgba(219, 239, 248, 0.18); }

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] label p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #E3EDF6 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255, 255, 255, 0.07);
    border: 1.5px dashed rgba(227, 237, 246, 0.45);
    border-radius: 12px;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
    border-color: #20B5A5;
    background: rgba(255, 255, 255, 0.10);
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
    color: #E3EDF6 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: #FFFFFF;
    color: #123C55 !important;
    border: 1px solid #FFFFFF;
    border-radius: 9px;
    font-weight: 600;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button p,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p {
    color: #123C55 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
    background: #DDF5F0;
    border-color: #DDF5F0;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] svg {
    color: #E3EDF6 !important;
}

/* ================= MOBILE ================= */
@media (max-width: 700px) {
    .block-container { padding: 1rem 0.8rem 2rem; }
    .st-key-navbar { padding: 12px; border-radius: 12px; }
    .med-brand-name { font-size: 18px; }
    .med-brand-subtitle { font-size: 8px; letter-spacing: 0.8px; }
    .med-logo { width: 38px; height: 38px; }
    .st-key-user_panel { justify-content: start; }
}
"""


def inject_styles():
    """Must run on every rerun, otherwise Streamlit drops the CSS."""
    st.markdown("<style>" + DASHBOARD_CSS + "</style>", unsafe_allow_html=True)


# --------------------------------------------------
# MAIN DASHBOARD
# --------------------------------------------------
def main():
    inject_styles()

    # Preserve the existing authentication check.
    if not st.session_state.get("logged_in", False):
        st.warning("Please sign in to access MediAssist AI.")
        return

    raw_name = str(st.session_state.get("username") or "User")
    username = html.escape(raw_name)
    initial = html.escape(raw_name.strip()[:1].upper() or "U")

    # --------------------------------------------------
    # NAVBAR
    #   [logo] MediAssist AI .................. (S)  SIGNED IN AS
    #                                               Sanket@264
    #                                               [⇥ Logout]
    # --------------------------------------------------
    with st.container(key="navbar"):
        col_brand, col_user = st.columns([6, 2], vertical_alignment="center")

        with col_brand:
            st.markdown(
                '<div class="med-brand">'
                '<div class="med-logo">✚</div>'
                "<div>"
                '<div class="med-brand-name">MediAssist AI</div>'
                '<div class="med-brand-subtitle">ENTERPRISE HEALTHCARE COPILOT</div>'
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with col_user:
            # The order of these three children matters: the CSS grid
            # places them as avatar | label+name | logout button.
            with st.container(key="user_panel"):
                st.markdown(
                    f'<div class="med-user-avatar">{initial}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div>'
                    '<div class="med-user-label">SIGNED IN AS</div>'
                    f'<div class="med-user-name">{username}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Logout",
                    key="dashboard_logout",
                    icon=":material/logout:",
                    type="secondary",
                ):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.page = "login"
                    st.rerun()

    # --------------------------------------------------
    # SIDEBAR: DOCUMENTS + IMAGE/PDF UPLOADS
    # --------------------------------------------------
    with st.sidebar:
        render_document_panel()

        st.divider()
        render_image_upload_panel()
   
    # --------------------------------------------------
    # MAIN CONTENT AREA
    # Chatbot integration.
    # --------------------------------------------------
    render_chatbot()


if __name__ == "__main__":
    main()

    