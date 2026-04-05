import streamlit as st
from google import genai
import smtplib
import os
# ---------------- API SETUP ----------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key not found ❌")
    st.stop()
client = genai.Client(api_key=api_key)


# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "4321":
            st.session_state.logged_in = True
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    st.stop()

# ---------------- MEMORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- UI ----------------
st.title("📧 AI Email Assistant")
st.write("Smart email reply + tone + summary + priority 🚀")

email_input = st.text_area("Paste your email here:")

# ---------------- AI GENERATE ----------------
if st.button("Generate AI Analysis"):
    if email_input:
        with st.spinner("Thinking..."):

            prompt = f"""
Analyze the email and give ONLY structured output.

Reply:
<write reply>

Tone:
<one word>

Summary:
<short 1 line>

Category:
<one word>

Priority:
<High/Medium/Low>

Email:
{email_input}
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text

            st.subheader("🤖 AI Output")
            st.write(result)

            # SAVE HISTORY
            st.session_state.history.append({
                "email": email_input,
                "response": result
            })

    else:
        st.warning("Enter email first!")

# ---------------- HISTORY ----------------
st.sidebar.title("📜 History")

for item in st.session_state.history[::-1]:
    st.sidebar.write("📧", item["email"][:50])
    st.sidebar.write("🤖", item["response"][:50])
    st.sidebar.markdown("---")

# ---------------- EMAIL SEND ----------------
def send_email(to_email, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        email = os.getenv("EMAIL")
        password = os.getenv("EMAIL_PASS")

        server.login(email, password)
        server.sendmail(email, to_email, message)
        server.quit()

        return True
    except:
        return False

# ---------------- SEND UI ----------------
st.subheader("📩 Send Email")

to_email = st.text_input("Receiver Email")

if st.button("Send Email"):
    if to_email and st.session_state.history:
        last_response = st.session_state.history[-1]["response"]

        if send_email(to_email, last_response):
            st.success("Email Sent ✅")
        else:
            st.error("Failed to send ❌")
    else:
        st.warning("Generate response first!")