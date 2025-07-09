# Smart Finance Manager + AI Budget Chatbot (Free GPT version only)

import streamlit as st
import pandas as pd
import datetime
import openai  # Requires OpenAI API key
from dateutil.relativedelta import relativedelta

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'categories' not in st.session_state:
    st.session_state.categories = ['Food', 'Transport', 'Utilities', 'Subscriptions']
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ''

# --- Helper Functions ---
def add_expense(date, category, amount, note):
    st.session_state.expenses.append({
        'date': date,
        'category': category,
        'amount': float(amount),
        'note': note
    })

def get_total_by_category():
    df = pd.DataFrame(st.session_state.expenses)
    if df.empty:
        return {}
    return df.groupby('category')['amount'].sum().to_dict()

def get_openai_client():
    return openai.OpenAI(api_key=st.session_state.openai_api_key)

def generate_ai_suggestions():
    df = pd.DataFrame(st.session_state.expenses)
    if df.empty:
        return "No spending data to analyze yet."

    prompt = f"""
    Analyze the following expenses and provide suggestions on budgeting improvements,
    savings strategies, and financial tips:
    {df.to_string(index=False)}
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial advisor bot."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except openai.RateLimitError:
        return "🚫 You have exceeded your OpenAI quota. Please check your plan and billing details."
    except Exception as e:
        return f"Error generating suggestions: {e}"

def chat_with_bot(user_input):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and professional financial chatbot."},
                *st.session_state.chat_history
            ]
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        return bot_reply
    except openai.RateLimitError:
        return "🚫 You have exceeded your OpenAI quota. Please check your plan and billing details."
    except Exception as e:
        return f"Error: {e}"

# --- UI Layout ---
st.set_page_config(page_title="Smart Finance Manager", layout="wide")
st.title("💸 Smart Finance Manager + AI Chatbot")

# API Key Input
with st.sidebar:
    st.subheader("🔐 Enter Your OpenAI API Key")
    st.session_state.openai_api_key = st.text_input("API Key", type="password")

# Tabs for Navigation
tabs = st.tabs(["Budget Plan", "Track Expenses", "Reminders & Calendar", "AI Advisor", "Appointments", "Chatbot"])

# --- Budget Plan Tab ---
with tabs[0]:
    st.header("📊 Create or Adjust Budget Plan")
    with st.expander("Manage Categories"):
        new_cat = st.text_input("Add New Category")
        if st.button("Add Category") and new_cat:
            st.session_state.categories.append(new_cat)
        del_cat = st.selectbox("Delete Category", [c for c in st.session_state.categories])
        if st.button("Delete Selected"):
            st.session_state.categories.remove(del_cat)

    st.subheader("Set Budget Limits")
    budget = {cat: st.number_input(f"Budget for {cat}", min_value=0.0, step=100.0) for cat in st.session_state.categories}

# --- Track Expenses Tab ---
with tabs[1]:
    st.header("🧾 Expense Tracker")
    with st.form("Add Expense"):
        date = st.date_input("Date", value=datetime.date.today())
        category = st.selectbox("Category", st.session_state.categories)
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        note = st.text_input("Note")
        if st.form_submit_button("Add"):
            add_expense(date, category, amount, note)
            st.success("Expense added successfully!")

    st.subheader("Expense Summary")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        st.dataframe(df)
        st.bar_chart(df.groupby('category')['amount'].sum())
    else:
        st.info("No expenses added yet.")

# --- Reminders & Calendar Tab ---
with tabs[2]:
    st.header("⏰ Reminders & Calendar")
    reminder_col1, reminder_col2 = st.columns(2)
    with reminder_col1:
        st.subheader("Set Reminder")
        rem_title = st.text_input("Reminder Title")
        rem_date = st.date_input("Reminder Date")
        rem_time = st.time_input("Reminder Time")
        st.button("Save Reminder")  # Add calendar integration logic here
    with reminder_col2:
        st.subheader("Calendar Overview")
        st.write("[Calendar integration placeholder - Coming soon]")

# --- AI Advisor Tab ---
with tabs[3]:
    st.header("🤖 AI Financial Advisor")
    if st.button("Generate Financial Suggestions"):
        with st.spinner("Analyzing spending patterns..."):
            suggestions = generate_ai_suggestions()
            st.markdown(suggestions)

# --- Appointments Tab ---
with tabs[4]:
    st.header("📅 Book Financial Appointments")
    st.text("Schedule a financial consultation or meeting:")
    name = st.text_input("Name")
    email = st.text_input("Email")
    appointment_date = st.date_input("Date")
    appointment_time = st.time_input("Time")
    if st.button("Book Appointment"):
        st.success(f"Appointment booked for {name} on {appointment_date} at {appointment_time}")

# --- Chatbot Tab ---
with tabs[5]:
    st.header("💬 AI Chatbot")
    st.write("Talk to your AI financial assistant:")
    user_input = st.chat_input("Type your message...")
    if user_input:
        response = chat_with_bot(user_input)
        st.write(f"**Bot:** {response}")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Python & Streamlit | AI-Powered Budget Assistant")
