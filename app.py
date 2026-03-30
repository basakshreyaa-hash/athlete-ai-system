import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Athlete AI Dashboard", layout="wide")

# -----------------------
# CUSTOM CSS (PREMIUM LOOK)
# -----------------------
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏋️ Athlete AI Performance Dashboard")

FILE = "athlete_data.csv"

# -----------------------
# LOAD DATA
# -----------------------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
else:
    df = pd.DataFrame(columns=[
        "Date","Name","Gender","Sport","Weight","Height",
        "Training","Sleep","Protein","Score"
    ])

# -----------------------
# SAVE FUNCTION
# -----------------------
def save_data():
    df.to_csv(FILE, index=False)

# -----------------------
# AI ENGINE
# -----------------------
def ai_score(weight, height, training, sleep, protein):
    
    bmi = weight / ((height/100)**2)
    
    # Scores
    training_score = min(training/4 * 10, 10)
    sleep_score = min(sleep/8 * 10, 10)
    protein_score = min(protein/(weight*1.8)*10, 10)

    # BMI balance
    if 18 <= bmi <= 24:
        bmi_score = 10
    else:
        bmi_score = 6

    final_score = (
        training_score * 0.35 +
        sleep_score * 0.2 +
        protein_score * 0.25 +
        bmi_score * 0.2
    )

    return round(final_score, 2), round(bmi,2)

# -----------------------
# FEEDBACK ENGINE
# -----------------------
def feedback(score):
    if score > 8:
        return "🔥 Elite Athlete! Keep pushing!"
    elif score > 6:
        return "💪 Good performance, improve consistency."
    else:
        return "⚠️ Needs improvement. Focus on training & recovery."

# -----------------------
# SIDEBAR INPUT
# -----------------------
st.sidebar.header("Add Athlete Data")

name = st.sidebar.text_input("Name")
gender = st.sidebar.selectbox("Gender", ["Male","Female"])
sport = st.sidebar.text_input("Sport")

weight = st.sidebar.number_input("Weight (kg)",30.0,150.0,60.0)
height = st.sidebar.number_input("Height (cm)",120.0,220.0,170.0)

training = st.sidebar.slider("Training Hours",0.0,8.0,2.0)
sleep = st.sidebar.slider("Sleep Hours",0.0,10.0,7.0)
protein = st.sidebar.number_input("Protein Intake (g)",0,300,80)

# -----------------------
# ADD DATA
# -----------------------
if st.sidebar.button("Add Athlete"):

    if name == "":
        st.sidebar.error("Enter Name")
    else:
        score, bmi = ai_score(weight, height, training, sleep, protein)

        new = pd.DataFrame({
            "Date":[datetime.now()],
            "Name":[name],
            "Gender":[gender],
            "Sport":[sport],
            "Weight":[weight],
            "Height":[height],
            "Training":[training],
            "Sleep":[sleep],
            "Protein":[protein],
            "Score":[score]
        })

        df = pd.concat([df, new], ignore_index=True)
        save_data()

        st.sidebar.success(f"{name} Added | Score: {score}")

# -----------------------
# MAIN DASHBOARD
# -----------------------
if df.empty:
    st.info("Add athlete data from sidebar 👈")

else:
    st.subheader("📊 Dashboard")

    athlete = st.selectbox("Select Athlete", df["Name"].unique())
    data = df[df["Name"] == athlete].sort_values("Date")

    latest = data.iloc[-1]
    score = latest["Score"]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Performance Score", score)
    col2.metric("BMI", round(latest["Weight"]/((latest["Height"]/100)**2),2))
    col3.metric("Training Hours", latest["Training"])

    # Feedback
    st.success(feedback(score))

    # Graph
    st.subheader("📈 Performance Trend")
    fig, ax = plt.subplots()
    ax.plot(data["Date"], data["Score"], marker='o')
    st.pyplot(fig)

    # Ranking
    st.subheader("🏆 Rankings")
    ranking = df.groupby("Name")["Score"].mean().sort_values(ascending=False)
    st.dataframe(ranking)

    # Download
    st.download_button("Download Data", df.to_csv(index=False), "athlete_data.csv")