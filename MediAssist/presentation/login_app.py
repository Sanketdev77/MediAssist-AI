import sys
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PROJECT PATH AND IMPORTS
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from authentication.auth import register_user, authenticate_user


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="MediAssist AI | Login",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f3f6fc;
        color: #172b4d;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1200px;
        padding: 2rem 1rem 1rem;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }

    .st-key-brand_panel {
        min-height: 570px;
        height: 100%;
        box-sizing: border-box;
        padding: 35px;
        border-radius: 10px 0 0 10px;
        color: white;
        background:
            linear-gradient(
                110deg,
                rgba(8, 35, 65, 0.95),
                rgba(12, 57, 91, 0.78),
                rgba(12, 57, 91, 0.55)
            ),
            url("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=85")
            center / cover no-repeat;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .st-key-brand_panel h1,
    .st-key-brand_panel h2,
    .st-key-brand_panel p {
        color: white;
    }

    .st-key-brand_panel h1 {
        font-size: 28px;
        font-weight: 750;
    }

    .st-key-brand_panel h2 {
        font-size: 28px;
        line-height: 1.3;
        margin-top: 48px;
    }

    .brand-subtitle {
        color: #e0eaf5;
        font-size: 12px;
    }

    .brand-feature {
        color: #f2f7fc;
        font-size: 13px;
        margin: 12px 0;
    }

    .st-key-auth_card {
        min-height: 570px;
        box-sizing: border-box;
        padding: 35px;
        border: 1px solid #dce5f0;
        border-left: none;
        border-radius: 0 10px 10px 0;
        background: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .st-key-auth_card h2 {
        font-size: 26px;
        color: #172b4d;
        margin-bottom: 0;
    }

    .st-key-auth_card input {
        min-height: 40px;
        border-radius: 6px;
        border: 1px solid #dce4ef;
    }

    .st-key-auth_card input:focus {
        border-color: #2478f5;
    }

    .st-key-auth_card label {
        font-size: 13px;
        color: #293d5b;
    }

    .st-key-auth_card button[kind="primary"] {
        width: 100%;
        min-height: 43px;
        border-radius: 6px;
        background: #1976f3;
        color: white;
        border: 1px solid #1976f3;
        font-weight: 600;
    }

    .st-key-auth_card button[kind="primary"]:hover {
        background: #095ecb;
        border-color: #095ecb;
        color: white;
    }

    .st-key-auth_card button[kind="secondary"] {
        color: #1769e8;
    }

    .auth-footer {
        margin-top: 22px;
        text-align: center;
        font-size: 11px;
        color: #7c8aa2;
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem 0.5rem;
        }

        .st-key-brand_panel {
            min-height: 270px;
            padding: 24px;
            border-radius: 10px 10px 0 0;
        }

        .st-key-brand_panel h2 {
            margin-top: 20px;
            font-size: 23px;
        }

        .st-key-auth_card {
            min-height: 440px;
            padding: 24px;
            border: 1px solid #dce5f0;
            border-radius: 0 0 10px 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "login"


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "login"
    st.rerun()


# --------------------------------------------------
# LEFT BRANDING PANEL
# --------------------------------------------------
def show_branding_panel():
    with st.container(key="brand_panel"):
        st.markdown("## ✚ MediAssist AI")

        st.markdown(
            '<div class="brand-subtitle">'
            'Enterprise Healthcare Agentic AI Copilot'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            "### Smarter Insights.<br>Better Healthcare.",
            unsafe_allow_html=True,
        )

        st.markdown(
            "Access patient data, clinical knowledge and enterprise "
            "systems through a unified AI assistant."
        )

        st.write("")

        st.markdown(
            '<div class="brand-feature">⌕ &nbsp; RAG-Powered Search</div>'
            '<div class="brand-feature">⚙ &nbsp; Multi-Agent AI</div>'
            '<div class="brand-feature">▧ &nbsp; Multimodal Analysis</div>'
            '<div class="brand-feature">↔ &nbsp; MCP + PostgreSQL</div>'
            '<div class="brand-feature">♢ &nbsp; Enterprise Ready</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# LOGIN FORM
# --------------------------------------------------
def show_login_form():
    st.markdown(
        "## Welcome to MediAssist AI – Enterprise Healthcare Agentic AI Copilot"
    )
    st.caption("Sign in to your MediAssist AI account")

    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
        )

        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
        )

        st.checkbox("Remember me", key="remember_me")

        login_clicked = st.form_submit_button(
            "Login",
            type="primary",
            use_container_width=True,
        )

    if login_clicked:
        username = username.strip()

        if not username or not password:
            st.error("Please enter both username and password.")

        else:
            try:
                is_authenticated = authenticate_user(username, password)

                if is_authenticated:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()

                else:
                    st.error("Invalid username or password.")

            except Exception:
                st.error(
                    "Unable to sign in right now. Please try again."
                )

    st.markdown("---")
    st.markdown("Don't have an account?")

    if st.button(
        "Create Your Account",
        type="primary",
        use_container_width=True,
        key="create_account_btn",
    ):
        st.session_state.page = "register"
        st.rerun()

    st.markdown(
        '<div class="auth-footer">Secure Healthcare AI Access</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# REGISTRATION FORM
# --------------------------------------------------
def show_registration_form():
    st.markdown("## Create Your Account")
    st.caption("Register to get started with MediAssist AI")

    with st.form("register_form"):
        new_username = st.text_input(
            "Username",
            placeholder="Choose a username",
        )

        new_password = st.text_input(
            "Password",
            placeholder="Create a password",
            type="password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            placeholder="Re-enter your password",
            type="password",
        )

        register_clicked = st.form_submit_button(
            "Register",
            type="primary",
            use_container_width=True,
        )

    if register_clicked:
        new_username = new_username.strip()

        if not new_username or not new_password or not confirm_password:
            st.error("Please fill in all fields.")

        elif len(new_username) < 3:
            st.error("Username must contain at least 3 characters.")

        elif len(new_password) < 8:
            st.error("Password must contain at least 8 characters.")

        elif new_password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                success, message = register_user(
                    new_username,
                    new_password,
                )

                if success:
                    st.success(message)
                    st.session_state.page = "login"
                    st.rerun()

                else:
                    st.error(message)

            except Exception:
                st.error(
                    "Unable to create your account right now. "
                    "Please try again."
                )

    st.markdown("---")
    st.markdown("Already have an account?")

    if st.button(
        "Back to Login",
        use_container_width=True,
        key="back_to_login_btn",
    ):
        st.session_state.page = "login"
        st.rerun()

    st.markdown(
        '<div class="auth-footer">'
        'Your account details are securely hashed'
        '</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# AUTHENTICATION PAGE
# --------------------------------------------------
def show_auth_page():
    left, right = st.columns([1.1, 1], gap=None)

    with left:
        show_branding_panel()

    with right:
        with st.container(key="auth_card"):
            if st.session_state.page == "login":
                show_login_form()
            else:
                show_registration_form()


# --------------------------------------------------
# MAIN APPLICATION FLOW
# --------------------------------------------------
# Import the dashboard only after the login app has initialized.
if st.session_state.get("logged_in", False):
    from presentation.main_dashboard import main as show_dashboard

    show_dashboard()
else:
    show_auth_page()