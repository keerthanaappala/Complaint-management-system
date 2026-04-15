import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from ai_model import categorize, get_priority, chatbot_response
from auth import *
from database import *  # includes get_complaint_by_id now

st.set_page_config(page_title="MRECW Complaint Portal", layout="wide")

create_users()
create_table()

SIREN_PATH = os.path.join(os.path.dirname(__file__), "siren.wav")


def get_notification_summary():
    counts = get_complaint_counts()
    total = sum(counts.values())
    return {
        "total": total,
        "pending": counts.get("Pending", 0),
        "in_progress": counts.get("In Progress", 0),
        "resolved": counts.get("Resolved", 0),
    }


def generate_ticket(name, sid):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_name = name.strip().upper().replace(" ", "")[:4] if name else "USER"
    sanitized_sid = sid.strip().upper().replace(" ", "")[-4:] if sid else "0000"
    return f"MRECW-{sanitized_name}-{sanitized_sid}-{timestamp}"


st.markdown(
    """
    <style>
        html, body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 25%, #A78BFA 50%, #F472B6 75%, #EC4899 100%);
            color: #1f2937;
        }
        .stApp, .reportview-container, .main, .block-container, .appview-container, .main > div, section.main, .streamlit-container {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 25%, #A78BFA 50%, #F472B6 75%, #EC4899 100%) !important;
            backdrop-filter: blur(18px);
            border-radius: 30px;
            box-shadow: 0 22px 65px rgba(15, 23, 42, 0.08);
            margin: 0 !important;
            padding: 0 !important;
        }
        .block-container {
            padding: 0rem 1.5rem 2.0rem !important;
            margin: 0 !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border-radius: 20px !important;
        }
        body > div:first-child, section.main, .streamlit-container, .block-container, .page-hero, .hero-title {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
    #    .login-wrapper {
    #         width: 50%;
    #         margin: 0 auto;
    #         # padding: 0rem 1rem 2.25rem;
    #         display: flex;
    #         flex-direction: column;
    #         align-items: center;
    #         min-height: auto;   /* FIXED: was calc(100vh - 100px) */
    #     }
        .page-hero {
            width: 100%;
            max-width: 920px;
            text-align: center;
            margin: 0 auto 0.75rem;
            padding: 0 1rem;
        }
        .stButton>button {
            border-radius: 16px;
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #A78BFA 100%);
            color: white;
            font-weight: 700;
            border: 1px solid rgba(14, 165, 233, 0.35);
            padding: 0.9rem 1.3rem;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #0284C7 0%, #0891B2 50%, #9333EA 100%);
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.4);
        }
        .stTextInput>div>div>input, .stTextInput>div>div>textarea, .stSelectbox>div>div>div>div,
        .stNumberInput>div>div>input, .stFileUploader>div>div {
            border-radius: 16px;
            border: 2px solid rgba(14, 165, 233, 0.25);
            background: rgba(255,255,255,0.98);
            color: #1f2937;
        }
        .stTextInput>div>div>input::placeholder, .stTextInput>div>div>textarea::placeholder {
            color: rgba(15, 23, 42, 0.45);
        }
        .login-card {
            padding: 2rem 2rem 2.4rem;
            border-radius: 30px;
            background: #ffffff;
            box-shadow: 0 24px 60px rgba(14, 165, 233, 0.2);
            border: 2px solid rgba(14, 165, 233, 0.2);
            backdrop-filter: blur(10px);
            margin-bottom: 1.5rem;
            max-width: 980px;
            margin-left: auto;
            margin-right: auto;
        }
        .login-card h2 {
            background: linear-gradient(135deg, #0EA5E9, #A78BFA, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            font-size: 2.2rem;
        }
        .login-card p {
            color: #64748b;
            margin-top: 0.25rem;
            margin-bottom: 1.5rem;
            line-height: 1.7;
        }
        .login-card .stTextInput>div>div>input,
        .login-card .stTextInput>div>div>textarea,
        .login-card .stSelectbox>div>div>div>div,
        .login-card .stNumberInput>div>div>input,
        .login-card .stFileUploader>div>div {
            border-radius: 16px;
            border: 2px solid rgba(14, 165, 233, 0.14);
            background: rgba(248, 250, 252, 0.98);
        }
        .login-card .stTextInput>div>label,
        .login-card .stSelectbox>div>label,
        .login-card .stRadio>div>label {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        .login-card .stRadio > div { margin-bottom: 1rem; }
        .sidebar-menu {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            padding-top: 0.5rem;
        }
        .stRadio label, section[data-testid="stSidebar"] label {
            color: #0EA5E9 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] label { font-size: 1rem !important; }
        section[data-testid="stSidebar"] [role="radio"] { accent-color: #06B6D4 !important; }
        [role="radio"] { accent-color: #06B6D4 !important; }
        .sos-button button {
            background: linear-gradient(135deg, #DC2626 0%, #EF4444 50%, #991B1B 100%);
            border-radius: 18px;
            color: white;
            font-weight: 700;
            border: 3px solid #7F1D1D;
            padding: 1.2rem 2rem;
            font-size: 1.1rem;
        }
        .sos-button button:hover {
            background: linear-gradient(135deg, #991B1B 0%, #EF4444 50%, #DC2626 100%);
            box-shadow: 0 16px 40px rgba(220, 38, 38, 0.6);
            transform: scale(1.05);
        }
        .logo-container {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #E0F2FE 0%, #F3E8FF 50%, #FCE7F3 100%);
            border-radius: 28px;
            margin-bottom: 1.5rem;
            box-shadow: 0 20px 40px rgba(14, 165, 233, 0.1);
            border: 2px solid rgba(14, 165, 233, 0.1);
        }
        .logo-container img { display: block; margin: 0 auto; }
        # .login-wrapper {
        #     width: 100%;
        #     margin: 0 auto;
        #     padding: 0rem 1rem 2.25rem;
        #     display: flex;
        #     flex-direction: column;
        #     align-items: center;
        #     min-height: calc(100vh - 100px);
        # }
        .page-hero {
            width: 100%;
            max-width: 920px;
            text-align: center;
            margin: 0 auto 0.75rem;
            padding: 0 1rem;
        }
        .hero-title h1 {
            margin: 0;
            font-size: clamp(2.4rem, 4vw, 3.4rem);
            line-height: 1.02;
            letter-spacing: 1px;
            font-weight: 900;
            color: #c81d24;
        }
        .hero-title p {
            margin: 0.6rem auto 0;
            font-size: 1.05rem;
            color: #4b5563;
            max-width: 760px;
        }
        .welcome-card {
            position: relative;
            margin: 0 auto;
            max-width: 760px;
            padding: 2.2rem 2rem 2.6rem;
            border-radius: 34px;
            background: #ffffff;
            border: 1px solid rgba(167, 139, 250, 0.25);
            box-shadow: 0 24px 60px rgba(99, 102, 241, 0.12);
            overflow: hidden;
        }
        .welcome-card::before,
        .welcome-card::after {
            content: "";
            position: absolute;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle at top, rgba(139, 92, 246, 0.20), transparent 70%);
            z-index: 0;
            animation: float 6s ease-in-out infinite;
        }
        .welcome-card::before {
            top: -25px;
            left: -25px;
        }
        .welcome-card::after {
            bottom: -25px;
            right: -25px;
            width: 100px;
            height: 100px;
            animation-delay: 2s;
        }
        .welcome-card h2 {
            position: relative;
            z-index: 1;
            margin: 0;
            font-size: clamp(2rem, 3vw, 2.8rem);
            font-weight: 900;
            line-height: 1.02;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .welcome-card p {
            position: relative;
            z-index: 1;
            margin: 0.85rem auto 0;
            max-width: 620px;
            color: #4b5563;
            font-size: 1rem;
            line-height: 1.7;
        }
        .confetti-dot {
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(236, 72, 153, 0.95);
            opacity: 0.85;
            animation: float 5s ease-in-out infinite;
        }
        .confetti-dot:nth-child(1) { top: 18%; left: 8%; animation-delay: 0s; }
        .confetti-dot:nth-child(2) { top: 12%; right: 12%; background: rgba(56, 189, 248, 0.92); animation-delay: 1s; }
        .confetti-dot:nth-child(3) { bottom: 18%; left: 16%; background: rgba(168, 85, 247, 0.88); animation-delay: 0.5s; }
        .confetti-dot:nth-child(4) { bottom: 12%; right: 14%; background: rgba(251, 191, 36, 0.88); animation-delay: 1.5s; }
        .login-card {
            max-width: 780px;
            width: 100%;
            margin: 1.25rem auto 0;
        }
        .college-header {
            text-align: center;
            padding: 22px 24px;
            margin: 0 auto 10px;
            border-bottom: 3px solid #DC2626;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            background: rgba(255, 255, 255, 0.96);
            border-radius: 24px;
            box-shadow: 0 18px 38px rgba(15, 23, 42, 0.08);
            overflow: hidden;
            max-width: 920px;
        }
        .college-header-logo {
            width: 92px;
            height: auto;
            display: inline-block;
            margin-left: 12px;
        }
        .college-header-text {
            text-align: center;
        }
        # .login-card .stRadio>div { margin-bottom: 1rem; }
        .college-header h1 {
            color: #DC2626;
            font-size: 2.8rem;
            font-weight: 900;
            margin: 0;
            letter-spacing: 1.2px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.12);
            display: inline-block;
        }
        .college-subtitle {
            margin: 4px 0 0;
            font-size: 1rem;
            color: #475569;
            font-weight: 600;
            letter-spacing: 0.6px;
        }
        .welcome-banner {
            position: relative;
            overflow: hidden;
            padding: 1.8rem 1.8rem 1.6rem;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.95), rgba(167, 139, 250, 0.92), rgba(244, 114, 182, 0.92));
            box-shadow: 0 20px 60px rgba(14, 165, 233, 0.18);
            margin-bottom: 1.5rem;
            color: white;
            animation: float 6s ease-in-out infinite;
        }
        .welcome-banner::before,
        .welcome-banner::after {
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.16);
            top: -60px;
            right: -60px;
            pointer-events: none;
        }
        .welcome-banner::after {
            width: 120px;
            height: 120px;
            top: auto;
            bottom: -40px;
            right: 20px;
            background: rgba(255, 255, 255, 0.1);
        }
        .welcome-banner h2 {
            margin: 0 0 0.4rem;
            font-size: 2.4rem;
            letter-spacing: 0.8px;
            background: linear-gradient(135deg, #FDE68A, #F472B6, #8B5CF6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .welcome-banner p {
            margin: 0;
            font-size: 1rem;
            line-height: 1.65;
            opacity: 0.95;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
        section[data-testid="stSidebar"] .stButton>button {
            background: linear-gradient(135deg, #F472B6 0%, #EC4899 50%, #0EA5E9 100%) !important;
            border-radius: 18px !important;
            padding: 0.9rem 1rem !important;
            margin: 0.5rem 0 !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            width: 100% !important;
            min-height: 3.2rem !important;
            text-align: left !important;
            box-shadow: 0 10px 24px rgba(236, 72, 153, 0.2) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        }
        section[data-testid="stSidebar"] .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 16px 32px rgba(236, 72, 153, 0.35) !important;
        }
        section[data-testid="stSidebar"] .stButton>button:focus {
            outline: 3px solid rgba(255, 255, 255, 0.45) !important;
        }
        .dashboard-title { 
            background: linear-gradient(135deg, #0EA5E9, #A78BFA, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.8rem; 
            font-weight: 800; 
            text-align: center; 
            margin-bottom: 1.8rem; 
        }
        .dashboard-card {
            padding: 1.75rem;
            border-radius: 26px;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid rgba(14, 165, 233, 0.12);
            box-shadow: 0 18px 45px rgba(14, 165, 233, 0.1);
            margin-bottom: 1.25rem;
        }
        .dashboard-card h3 { 
            margin-top: 0; 
            background: linear-gradient(135deg, #0EA5E9, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        [data-testid="stDataFrame"] {
            background: rgba(240, 249, 255, 0.98) !important;
            border-radius: 20px !important;
            color: #0f172a !important;
            border: 2px solid rgba(14, 165, 233, 0.15) !important;
        }
        .css-1cpxqw2 { color: #0EA5E9 !important; font-weight: 700 !important; }
        .css-1v0mbdj { background-color: rgba(14, 165, 233, 0.06) !important; }
        .css-1lcbmhc, .css-1v4u2gq, .css-1q8f2ux { background-color: rgba(14, 165, 233, 0.05) !important; }
        h1, h2, h3, h4, h5, h6, p, div { color: #111827; }
        .stMarkdown, .stText { color: #111827; }
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98) !important;
            border-right: 2px solid rgba(14, 165, 233, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "role" not in st.session_state:
    st.session_state.role=None

# ---------------- LOGIN PAGE ----------------
if st.session_state.role is None:

    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='page-hero'>
            <div class='hero-title'>
                <h1>Malla Reddy Engineering College for Women (MRECW)</h1>
                <p>Smart Campus Care Portal</p>
            </div>
            <div class='welcome-card'>
                <div class='confetti-dot'></div>
                <div class='confetti-dot'></div>
                <div class='confetti-dot'></div>
                <div class='confetti-dot'></div>
                <h2>Welcome to MRECW Portal</h2>
                <p>Enjoy a modern campus care experience designed for students, staff, and campus teams.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    option = st.radio("Login/Register", ["Login", "Register"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = st.selectbox("Role", [
        "Student",
        "Hostel Admin",
        "College Admin",
        "Canteen Admin",
        "Security Admin",
        "Women Safety Admin",
        "Other Admin"
    ])

    if option == "Register":
        if st.button("Register"):
            if not username.strip() or not password.strip():
                st.error("Username and password are required to register.")
            else:
                ok, msg = register(username, password, role)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    else:
        if st.button("Login"):
            if not username.strip() or not password.strip():
                st.error("Please enter both username and password.")
            else:
                user = login(username, password)
                if user:
                    st.session_state.username = user[0]
                    st.session_state.role = user[1]
                    st.rerun()
                else:
                    st.error("Invalid Login")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AFTER LOGIN ----------------
else:

    role = st.session_state.role

    st.sidebar.title(role)

    st.markdown(
        """
        <div class='college-header'>
            <div class='college-header-text'>
                <h1>MALLA REDDY ENGINEERING COLLEGE FOR WOMEN</h1>
                <p class="college-subtitle">Smart Campus Care Portal</p>
            </div>
            <img src="logo.png" class="college-header-logo" />
        </div>
        <div class='welcome-banner'>
            <h2>Welcome to MRECW Portal</h2>
            <p>Experience the colorful campus complaint portal designed for MRECW students and staff.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 class='dashboard-title'>🎓 Smart Campus Care</h1>", unsafe_allow_html=True)

    if role != "Student":
        summary = get_notification_summary()
        st.sidebar.markdown("### Admin Notifications")
        st.sidebar.markdown(f"- **Total complaints:** {summary['total']}")
        st.sidebar.markdown(f"- **Pending:** {summary['pending']}")
        st.sidebar.markdown(f"- **In Progress:** {summary['in_progress']}")
        st.sidebar.markdown(f"- **Resolved:** {summary['resolved']}")
        if st.sidebar.button("Refresh Notifications"):
            st.rerun()
        st.sidebar.markdown("---")

    if "menu" not in st.session_state:
        st.session_state.menu = "Dashboard"

    menu_options = [
        "Dashboard",
        "Submit Complaint",
        "AI Chatbot",
        "Hostel Admin",
        "College Admin",
        "Canteen Admin",
        "Security Admin",
        "Women Safety Admin",
        "Other Admin",
        "Logout"
    ]

    st.sidebar.markdown("<div class='sidebar-menu'>", unsafe_allow_html=True)
    for option in menu_options:
        if st.sidebar.button(option, key=f"menu_{option}"):
            st.session_state.menu = option
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    menu = st.session_state.menu

# ---------------- STUDENT ----------------

    if role=="Student":

        if menu=="Dashboard":

            # Emergency SOS Section
            st.markdown("<div class='sos-button'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: #DC2626; text-align: center; margin: 0;'>🚨 EMERGENCY SOS</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #666; text-align: center; margin-top: 0.5rem;'>Select emergency type and activate SOS</p>", unsafe_allow_html=True)
            
            if st.button("🚨 ACTIVATE EMERGENCY SOS", use_container_width=True, key="activate_sos"):
                student_name = st.session_state.username or "Unknown Student"
                ticket = generate_ticket(student_name, st.session_state.username or "0000")
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sos_description = "Emergency SOS triggered by student. Immediate attention required."

                add_complaint((
                    ticket,
                    student_name,
                    st.session_state.username or "Unknown",
                    None,
                    "Unknown",
                    "N/A",
                    "Emergency SOS",
                    "Other",
                    "Emergency SOS",
                    sos_description,
                    None,
                    "High",
                    "Pending",
                    "",
                    "",
                    now,
                ))

                if os.path.exists(SIREN_PATH):
                    with open(SIREN_PATH, 'rb') as audio_file:
                        audio_bytes = audio_file.read()
                    st.markdown(
                        f"""
                        <audio autoplay>
                            <source src="data:audio/wav;base64,{__import__('base64').b64encode(audio_bytes).decode()}" type="audio/wav">
                        </audio>
                        """,
                        unsafe_allow_html=True
                    )
                    st.info("🔊 Siren sound activated immediately.")
                else:
                    st.warning("Siren sound file not found. Please add siren.wav to the app folder.")

                st.success("Emergency SOS submitted successfully. Security has been notified in the portal.")
            
            st.markdown("<h3 style='color: #333; margin-top: 1.5rem; margin-bottom: 1rem;'>Select Emergency Type:</h3>", unsafe_allow_html=True)
            
            emergency_types = ["🏥 Medical", "🔒 Security", "🔥 Fire", "👩 Women Safety", "⚙️ Other"]
            emerg_cols = st.columns(len(emergency_types), gap="small")
            
            for idx, emerg_type in enumerate(emergency_types):
                with emerg_cols[idx]:
                    if st.button(emerg_type, use_container_width=True, key=f"emergency_{idx}"):
                        student_name = st.session_state.username or "Unknown Student"
                        ticket = generate_ticket(student_name, st.session_state.username or "0000")
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        sos_description = f"Emergency SOS - Type: {emerg_type}. Immediate attention required."

                        if "Medical" in emerg_type:
                            category = "Other"
                        elif "Security" in emerg_type:
                            category = "Security"
                        elif "Fire" in emerg_type:
                            category = "Other"
                        elif "Women Safety" in emerg_type:
                            category = "Women Safety"
                        else:
                            category = "Other"

                        issue = f"Emergency - {emerg_type}"
                        complaint_for = "Emergency SOS"

                        add_complaint((
                            ticket,
                            student_name,
                            st.session_state.username or "Unknown",
                            None,
                            "Unknown",
                            "N/A",
                            complaint_for,
                            category,
                            issue,
                            sos_description,
                            None,
                            "High",
                            "Pending",
                            "",
                            "",
                            now,
                        ))

                        if os.path.exists(SIREN_PATH):
                            with open(SIREN_PATH, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                            st.markdown(
                                f"""
                                <audio autoplay>
                                    <source src="data:audio/wav;base64,{__import__('base64').b64encode(audio_bytes).decode()}" type="audio/wav">
                                </audio>
                                """,
                                unsafe_allow_html=True
                            )
                            st.info(f"🔊 Siren sound activated for {emerg_type}")
                        
                        st.success(f"{emerg_type} emergency submitted successfully. {category} has been notified!")
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Display All Admins in Blue
            st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>👥 Available Admins</h3></div>", unsafe_allow_html=True)
            admins = get_all_admins()
            if admins:
                admin_html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>"
                for admin_username, admin_role in admins:
                    role_emoji = "🏛️" if "College" in admin_role else "🏨" if "Hostel" in admin_role else "🍽️" if "Canteen" in admin_role else "🔒" if "Security" in admin_role else "👩" if "Women" in admin_role else "⚙️"
                    admin_html += f"""
                    <div style='background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%); 
                                padding: 20px; border-radius: 12px; border: 2px solid #ff6b35;
                                box-shadow: 0 8px 16px rgba(255, 107, 53, 0.4); cursor: pointer;
                                transition: transform 0.2s;'>
                        <div style='font-weight: 700; color: #ffffff; margin-bottom: 8px; font-size: 1.1rem;'>{role_emoji} {admin_role}</div>
                        <div style='color: #ffe0b2; font-size: 0.9rem;'>👤 {admin_username}</div>
                    </div>
                    """
                admin_html += "</div>"
                st.markdown(admin_html, unsafe_allow_html=True)
            else:
                st.info("No admins available yet.")

            data=get_student_complaints(st.session_state.username)

            df=pd.DataFrame(data,columns=[
                "id","ticket","student_name","student_id","student_email","department","section",
                "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
            ])

            df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                          "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]

            st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📋 Your Complaints</h3></div>", unsafe_allow_html=True)
            st.dataframe(df)

            if not df.empty:
                project_data = get_all_complaints()
                project_df = None
                if project_data:
                    project_df = pd.DataFrame(project_data, columns=[
                        "id", "ticket", "student_name", "student_id", "student_email", "department", "section",
                        "complaint_for", "category", "issue", "description", "image", "priority", "status", "feedback", "rating", "date_created"
                    ])
                    project_df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                                          "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]

                st.markdown("<div class='dashboard-card'><h3 style='color: #00D9FF;'>📊 PROJECT-WIDE COMPLAINT ANALYSIS BY CATEGORY</h3></div>", unsafe_allow_html=True)
                
                requested_categories = [
                    'Hostel', 'College', 'Canteen', 'Transport',
                    'Security', 'Women Safety', 'Academic', 'Other'
                ]
                display_labels = [
                    'Hostel', 'College', 'Canteen', 'Transport',
                    'Security', 'Women Safety', 'Academic', 'Others'
                ]
                category_color_map = {
                    'Hostel': '#1DD1A1',
                    'College': '#6C5CE7',
                    'Canteen': '#FFA502',
                    'Transport': '#00D9FF',
                    'Security': '#FF6B6B',
                    'Women Safety': '#FDCB6E',
                    'Academic': '#A29BFE',
                    'Other': '#DFE6E9'
                }
                
                if project_df is not None and not project_df.empty:
                    category_counts = project_df['Category'].apply(
                        lambda c: c if c in requested_categories else 'Other'
                    ).value_counts().reindex(requested_categories, fill_value=0)

                    labels = display_labels
                    values = category_counts.values
                    colors = [category_color_map[cat] for cat in requested_categories]
                    
                    fig, ax = plt.subplots(figsize=(18, 4))
                    bars = ax.bar(range(len(values)), values,
                                  color=colors, edgecolor='white', linewidth=2.5, width=0.7)
                    
                    ax.set_xticks(range(len(labels)))
                    ax.set_xticklabels(labels, fontsize=12, fontweight='bold', color='white', rotation=0)
                    
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.2,
                                f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=13, color='white')
                    
                    ax.set_ylabel("")
                    ax.set_ylim(0, max(values.max(), 1) * 1.25)
                    ax.set_axisbelow(True)
                    ax.grid(axis='y', alpha=0.18, linestyle='--', color='white', linewidth=1)
                    ax.set_yticks([])
                    
                    fig.patch.set_facecolor('#1a1a2e')
                    ax.set_facecolor('#16213e')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['left'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    
                    fig.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No complaints to display.")
            else:
                st.info("No complaints found. Submit a complaint to see analytics.")
        elif menu=="Submit Complaint":

            st.markdown("**Please fill in the complaint form below. Required fields are marked with an asterisk.**")
            st.write("")

            name = st.text_input("Name *")
            sid = st.text_input("Student ID *")
            dept = st.text_input("Department *")
            section = st.text_input("Section")
            complaint_for = st.text_input("Complaint For", "Student Services")

            issue = st.text_input("Issue *")
            desc = st.text_area("Description *")

            suggested_category = categorize(f"{issue} {desc}")
            suggested_priority = get_priority(f"{issue} {desc}")

            category = st.selectbox("Category", [
                "Auto Categorize",
                "Hostel",
                "College",
                "Canteen",
                "Transport",
                "Security",
                "Women Safety",
                "Academic",
                "Other"
            ])
            if category == "Auto Categorize":
                category = suggested_category
                st.info(f"Suggested category: {category}")
                st.markdown(f"**Detected category:** {category}")

            priority = st.selectbox("Priority", ["Auto Estimate", "Low", "Medium", "High"])
            if priority == "Auto Estimate":
                priority = suggested_priority
                st.info(f"Suggested priority: {priority}")

            image = st.file_uploader("Upload Image")

            if st.button("Submit"):
                required_fields = {
                    "Name": name,
                    "Student ID": sid,
                    "Department": dept,
                    "Issue": issue,
                    "Description": desc,
                }
                missing = [label for label, value in required_fields.items() if not str(value).strip()]

                if missing:
                    st.error("Please fill in the following required fields: " + ", ".join(missing))
                else:
                    img = image.read() if image else None
                    ticket = generate_ticket(name, sid)
                    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    email = ""

                    add_complaint((
                        ticket,
                        name,
                        sid,
                        email,
                        dept,
                        section,
                        complaint_for,
                        category,
                        issue,
                        desc,
                        img,
                        priority,
                        "Pending",
                        "",
                        "",
                        date_created,
                    ))

                    st.success("Complaint submitted successfully.")
                    st.info("Your complaint has been recorded and will be reviewed by admins shortly.")
                    st.markdown(f"<div class='dashboard-card'><strong>Detected Category:</strong> {category}</div>", unsafe_allow_html=True)

        elif menu == "AI Chatbot":
            st.header("🤖 AI Chatbot Assistant")
            st.markdown(
                "💬 Ask me anything about the Smart Campus Care system, complaints, or campus services. I'll respond instantly!"
            )

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            if "chatbot_input" not in st.session_state:
                st.session_state.chatbot_input = ""

            st.markdown(
                """
                <style>
                    .chat-window {
                        border-radius: 18px;
                        padding: 20px;
                        background: rgba(240, 249, 255, 0.6);
                        border: 2px solid rgba(14, 165, 233, 0.2);
                        margin-bottom: 20px;
                    }
                    .chat-row {
                        margin-bottom: 16px;
                        display: flex;
                        animation: fadeIn 0.3s ease-in;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .chat-bubble-user {
                        background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%);
                        color: white;
                        padding: 14px 18px;
                        border-radius: 18px;
                        margin-left: auto;
                        max-width: 70%;
                        word-wrap: break-word;
                        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
                        font-size: 14px;
                        line-height: 1.5;
                    }
                    .chat-bubble-assistant {
                        background: white;
                        color: #111827;
                        padding: 14px 18px;
                        border-radius: 18px;
                        margin-right: auto;
                        max-width: 70%;
                        word-wrap: break-word;
                        border: 2px solid rgba(14, 165, 233, 0.15);
                        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.1);
                        font-size: 14px;
                        line-height: 1.5;
                    }
                    .chat-empty {
                        text-align: center;
                        color: #94a3b8;
                        padding: 40px 20px;
                        font-style: italic;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
            if not st.session_state.chat_history:
                st.markdown(
                    "<div class='chat-empty'>👋 No messages yet. Start by asking me about the portal, complaints, emergency support, or anything about the system!</div>",
                    unsafe_allow_html=True,
                )
            else:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        st.markdown(
                            f"<div class='chat-row'>"
                            f"<div class='chat-bubble-user'>{message['content']}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div class='chat-row'>"
                            f"<div class='chat-bubble-assistant'>{message['content']}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
            st.markdown("</div>", unsafe_allow_html=True)

            if "chatbot_warning" not in st.session_state:
                st.session_state.chatbot_warning = ""

            def send_chat_message():
                user_message = st.session_state.chatbot_input.strip()
                if not user_message:
                    st.session_state.chatbot_warning = "Please enter a message before sending."
                    return

                st.session_state.chat_history.append({"role": "user", "content": user_message})
                st.session_state.chatbot_input = ""

                try:
                    response = chatbot_response(user_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I'm here to help! Please try again with your question."})

            col1, col2 = st.columns([5, 1], gap="small")
            with col1:
                st.text_area(
                    "Your message",
                    placeholder="Ask anything about the system...",
                    key="chatbot_input",
                    height=80,
                )
            with col2:
                st.button("Send", use_container_width=True, type="primary", on_click=send_chat_message)

            if st.session_state.chatbot_warning:
                st.warning(st.session_state.chatbot_warning)
                st.session_state.chatbot_warning = ""

            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()

    if role != "Student" and menu == "Dashboard":
        summary = get_notification_summary()
        st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📣 Admin Dashboard</h3></div>", unsafe_allow_html=True)
        st.markdown(f"**Total complaints:** {summary['total']}  \n**Pending:** {summary['pending']}  \n**In Progress:** {summary['in_progress']}  \n**Resolved:** {summary['resolved']}")

        all_data = get_all_complaints()
        if all_data:
            admin_df = pd.DataFrame(all_data, columns=[
                "id","ticket","student_name","student_id","student_email","department","section",
                "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
            ])
            admin_df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                              "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]
            st.dataframe(admin_df)
        else:
            st.info("No complaints have been submitted yet.")

        if all_data:
            st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📊 Overall Complaint Analytics By Category</h3></div>", unsafe_allow_html=True)

            admin_df['Date Created'] = pd.to_datetime(admin_df['Date Created'], errors='coerce')
            requested_categories = [
                'Hostel', 'College', 'Canteen', 'Transport',
                'Security', 'Women Safety', 'Academic', 'Other'
            ]
            display_labels = [
                'Hostel', 'College', 'Canteen', 'Transport',
                'Security', 'Women Safety', 'Academic', 'Others'
            ]
            category_color_map = {
                'Hostel': '#1DD1A1',
                'College': '#6C5CE7',
                'Canteen': '#FFA502',
                'Transport': '#00D9FF',
                'Security': '#FF6B6B',
                'Women Safety': '#FDCB6E',
                'Academic': '#A29BFE',
                'Other': '#DFE6E9'
            }
            
            category_counts = admin_df['Category'].apply(
                lambda c: c if c in requested_categories else 'Other'
            ).value_counts().reindex(requested_categories, fill_value=0)

            labels = display_labels
            values = category_counts.values
            colors = [category_color_map[cat] for cat in requested_categories]
            
            fig, ax = plt.subplots(figsize=(18, 4))
            bars = ax.bar(range(len(values)), values,
                          color=colors, edgecolor='white', linewidth=2.5, width=0.7)
            
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=12, fontweight='bold', color='white', rotation=0)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.2,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=13, color='white')
            
            ax.set_ylabel("")
            ax.set_ylim(0, max(values.max(), 1) * 1.25)
            ax.set_axisbelow(True)
            ax.grid(axis='y', alpha=0.18, linestyle='--', color='white', linewidth=1)
            ax.set_yticks([])
            
            fig.patch.set_facecolor('#1a1a2e')
            ax.set_facecolor('#16213e')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            fig.tight_layout()
            st.pyplot(fig)
    admin_map={
        "Hostel Admin":"Hostel",
        "College Admin":"College",
        "Canteen Admin":"Canteen",
        "Security Admin":"Security",
        "Women Safety Admin":"Women Safety",
        "Other Admin":"Other"
    }

    if menu in admin_map:

        category=admin_map[menu]

        data=get_category_complaints(category)

        df=pd.DataFrame(data,columns=[
            "id","ticket","student_name","student_id","student_email","department","section",
            "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
        ])

        df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                      "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]

        st.header(f"{category} Complaints Dashboard")

        st.dataframe(df)

        cid=st.number_input("Complaint ID",step=1)

        status=st.selectbox("Status",[
            "Pending","In Progress","Resolved"
        ])

        if st.button("Update Status"):

            update_status(cid,status)

            complaint = get_complaint_by_id(cid)
            if complaint and complaint[4]:  # student_email is index 4
                st.success(f"Status updated to '{status}'.")
                st.info("The student will be notified through the portal.")
            else:
                st.success(f"Status updated to '{status}'.")

# ---------------- LOGOUT ----------------

    if menu=="Logout":

        st.session_state.role=None

        st.rerun()
