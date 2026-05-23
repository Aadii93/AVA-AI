import streamlit as st
from groq import Groq
from PIL import Image
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AVA AI",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# GROQ API
# =====================================================

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(
    api_key=GROQ_API_KEY
)

# =====================================================
# FIREBASE WEB CONFIG
# =====================================================

firebase_config = {

    "apiKey": st.secrets["FIREBASE_API_KEY"],

    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],

    "projectId": st.secrets["FIREBASE_PROJECT_ID"],

    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],

    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],

    "appId": st.secrets["FIREBASE_APP_ID"],

    "databaseURL": ""

}

firebase = pyrebase.initialize_app(firebase_config)

auth = firebase.auth()

# =====================================================
# FIRESTORE DATABASE
# =====================================================

if not firebase_admin._apps:

    cred = credentials.Certificate({

        "type": "service_account",

        "project_id":
        st.secrets["FIREBASE_PROJECT_ID"],

        "private_key_id":
        st.secrets["FIREBASE_PRIVATE_KEY_ID"],

        "private_key":
        st.secrets["FIREBASE_PRIVATE_KEY"]
        .replace("\\n", "\n"),

        "client_email":
        st.secrets["FIREBASE_CLIENT_EMAIL"],

        "client_id":
        st.secrets["FIREBASE_CLIENT_ID"],

        "auth_uri":
        "https://accounts.google.com/o/oauth2/auth",

        "token_uri":
        "https://oauth2.googleapis.com/token",

        "auth_provider_x509_cert_url":
        "https://www.googleapis.com/oauth2/v1/certs",

        "client_x509_cert_url":
        st.secrets["FIREBASE_CLIENT_CERT_URL"]

    })

    firebase_admin.initialize_app(cred)

db = firestore.client()

# =====================================================
# SESSION STATES
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "Chat 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0b1020;
    color: white;
    font-family: sans-serif;
}

.main {
    background: linear-gradient(135deg,#0f172a,#111827);
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

.user-msg {

    background: linear-gradient(90deg,#007cf0,#00dfd8);

    padding: 12px 18px;

    border-radius: 18px;

    margin: 10px 0;

    color: white;

    margin-left: auto;

    max-width: fit-content;

    font-size: 15px;

    width: fit-content;

    word-wrap: break-word;
}

.bot-msg {

    background: #1e293b;

    padding: 12px 18px;

    border-radius: 18px;

    margin: 10px 0;

    color: white;

    max-width: 75%;

    width: fit-content;

    font-size: 15px;

    word-wrap: break-word;
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
}

.creator-box {
    background: #1e293b;
    padding: 15px;
    border-radius: 18px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN / SIGNUP
# =====================================================

with st.sidebar:

    if st.session_state.user is None:

        st.title("🔐 AVA AI")

        auth_mode = st.selectbox(
            "Choose",
            ["Login", "Signup"]
        )

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        username = ""

        if auth_mode == "Signup":

            username = st.text_input("Username")

            if st.button("Create Account"):

                try:

                    auth.create_user_with_email_and_password(
                        email,
                        password
                    )

                    st.success(
                        "Account created successfully!"
                    )

                except Exception as e:

                    st.error("Signup failed")

        else:

            if st.button("Login"):

                try:

                    user_data = auth.sign_in_with_email_and_password(
                        email,
                        password
                    )

                    st.session_state.user = {

                        "email": email,

                        "name":
                        email.split("@")[0].capitalize()

                    }

                    # LOAD SAVED CHATS

                    try:

                        user_data_db = db.collection(
                            "users"
                        ).document(email).get()

                        if user_data_db.exists:

                            data = user_data_db.to_dict()

                            st.session_state.all_chats = (
                                data.get(
                                    "chats",
                                    {"Chat 1": []}
                                )
                            )

                    except:
                        pass

                    st.success("Login successful!")

                    st.rerun()

                except Exception as e:

                    if (
                        "INVALID_LOGIN_CREDENTIALS"
                        in str(e)
                    ):

                        st.error(
                            "Invalid email or password"
                        )

                    else:

                        st.error("Login failed")

        st.stop()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🤖 AVA AI")

    st.success(
        f"👋 {st.session_state.user['name']}"
    )

    if st.button("🚪 Logout"):

        st.session_state.user = None

        st.rerun()

    st.markdown("---")

    # NEW CHAT

    if st.button("➕ New Chat"):

        st.session_state.chat_counter += 1

        new_chat_name = (
            f"Chat {st.session_state.chat_counter}"
        )

        st.session_state.all_chats[
            new_chat_name
        ] = []

        st.session_state.current_chat = (
            new_chat_name
        )

        st.rerun()

    st.markdown("### 💬 Chats")

    for chat_name in list(
        st.session_state.all_chats.keys()
    ):

        col1, col2 = st.columns([4,1])

        with col1:

            if st.button(
                chat_name,
                key=f"chat_{chat_name}"
            ):

                st.session_state.current_chat = (
                    chat_name
                )

        with col2:

            if st.button(
                "✏️",
                key=f"rename_{chat_name}"
            ):

                st.session_state.rename_chat = (
                    chat_name
                )

        # RENAME CHAT

        if (
            "rename_chat" in st.session_state
            and st.session_state.rename_chat
            == chat_name
        ):

            new_name = st.text_input(
                "Rename Chat",
                value=chat_name,
                key=f"input_{chat_name}"
            )

            col_save, col_delete = st.columns(2)

            with col_save:

                if st.button(
                    "Save",
                    key=f"save_{chat_name}"
                ):

                    st.session_state.all_chats[
                        new_name
                    ] = st.session_state.all_chats.pop(
                        chat_name
                    )

                    st.session_state.current_chat = (
                        new_name
                    )

                    del st.session_state.rename_chat

                    st.rerun()

            with col_delete:

                if st.button(
                    "Delete",
                    key=f"delete_{chat_name}"
                ):

                    del st.session_state.all_chats[
                        chat_name
                    ]

                    if len(
                        st.session_state.all_chats
                    ) == 0:

                        st.session_state.all_chats = {
                            "Chat 1": []
                        }

                    st.session_state.current_chat = list(
                        st.session_state.all_chats.keys()
                    )[0]

                    del st.session_state.rename_chat

                    st.rerun()

    st.markdown("---")

    st.markdown("## 👑 Creator")

    st.markdown("""
<div class="creator-box">

<h4>Aditya Vishwakarma</h4>

Instagram: @Haruto_shinichi07

</div>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.markdown("""
<h1 style='text-align:center;
color:#38bdf8;
font-size:58px;
margin-top:-10px;
font-weight:bold;'>
AVA AI
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center;
font-size:18px;
margin-top:-15px;
color:#cbd5e1;'>
Your Personal Intelligent AI Assistant
</p>
""", unsafe_allow_html=True)

# =====================================================
# CURRENT CHAT
# =====================================================

current_messages = st.session_state.all_chats[
    st.session_state.current_chat
]

# =====================================================
# SHOW CHAT
# =====================================================

for msg in current_messages:

    if msg["role"] == "user":

        st.markdown(
            f"<div class='user-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"<div class='bot-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# =====================================================
# INPUT
# =====================================================

prompt = st.chat_input(
    f"Ask anything, {st.session_state.user['name']}..."
)

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = f"""

You are AVA AI.

You are emotional,
friendly,
funny,
human-like,
and deeply understanding.

The user's name is:
{st.session_state.user['name']}

Always talk naturally like a real human.

IMPORTANT LANGUAGE RULES:

1. If user speaks in English:
Reply ONLY in simple English.

2. If user speaks in Hinglish:
Reply ONLY in simple Hinglish.

3. If user speaks in Hindi:
Reply ONLY in Hindi.

4. If user mixes Hindi and English:
Reply in mixed Hindi-English naturally.

5. NEVER mix languages unnecessarily.

6. Match the user's tone and style.

7. Avoid difficult English words unless user asks.

8. Keep replies human and conversational.

9. Keep replies short unless user asks for details.

10. Never sound robotic.

Call the user by their name naturally sometimes.

Creator:
Aditya Vishwakarma

Instagram:
@Haruto_shinichi07

Behave like a premium modern AI assistant.

"""

# =====================================================
# CHAT
# =====================================================

if prompt:

    # SAVE USER MESSAGE

    st.session_state.all_chats[
        st.session_state.current_chat
    ].append({

        "role": "user",

        "content": prompt

    })

    st.markdown(
        f"<div class='user-msg'>{prompt}</div>",
        unsafe_allow_html=True
    )

    creator_keywords = [

        "creator photo",
        "creator image",
        "show creator",
        "aditya photo",
        "aditya image",

        "show me your creator",
        "show your creator",
        "who is your creator",
        "your creator",
        "creator pic",
        "creator picture",
        "show creator image",
        "show creator photo",
        "who made you",
        "who created you",
        "your owner",
        "show me creator"

    ]

    show_creator = any(

        word in prompt.lower()

        for word in creator_keywords

    )

    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[

                {
                    "role": "system",

                    "content": SYSTEM_PROMPT
                },

                *[
                    {
                        "role": m["role"],

                        "content": m["content"]
                    }

                    for m in st.session_state.all_chats[
                        st.session_state.current_chat
                    ]
                ]
            ],

            temperature=0.7,

            max_tokens=1024

        )

        reply = (
            response.choices[0]
            .message.content
        )

    except Exception as e:

        reply = f"⚠️ Error: {str(e)}"

    # SAVE BOT MESSAGE

    st.session_state.all_chats[
        st.session_state.current_chat
    ].append({

        "role": "assistant",

        "content": reply

    })

    # SAVE TO FIRESTORE

    try:

        db.collection("users").document(
            st.session_state.user["email"]
        ).set({

            "email":
            st.session_state.user["email"],

            "name":
            st.session_state.user["name"],

            "chats":
            st.session_state.all_chats

        })

    except:
        pass

    # SHOW BOT MESSAGE

    st.markdown(
        f"<div class='bot-msg'>{reply}</div>",
        unsafe_allow_html=True
    )

    # SHOW CREATOR IMAGE

    if show_creator:

        st.markdown("## 👑 Creator")

        col1, col2, col3 = st.columns([1,2,1])

        with col2:

            image = Image.open("myphoto.png")

            st.image(
                image,
                width=420
            )

            st.markdown("""
### Aditya Vishwakarma

Instagram:
@Haruto_shinichi07
""")