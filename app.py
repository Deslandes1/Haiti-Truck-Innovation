import streamlit as st
import time
import pandas as pd
import numpy as np

# --- 1. SETTINGS & CREDENTIALS ---
st.set_page_config(page_title="Haiti Truck Innovation", page_icon="🚛", layout="wide")

COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com | (509)-4738-5663"
PASSWORD_REQUIRED = "20082010"

# --- 2. SESSION STATE MANAGEMENT ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'attached' not in st.session_state:
    st.session_state.attached = False
if 'location' not in st.session_state:
    st.session_state.location = "Florida"
if 'fuel' not in st.session_state:
    st.session_state.fuel = 100
if 'log' not in st.session_state:
    st.session_state.log = []

# --- 3. LOGIN GATE ---
if not st.session_state.auth:
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #00209F;'>🇭🇹 HAITI TRUCK INNOVATION</h1>
            <h3 style='color: #D21034;'>Training Simulator V1.0</h3>
        </div>
    """, unsafe_allow_html=True)
    
    pwd = st.text_input("ENTER SYSTEM KEY:", type="password")
    if st.button("IGNITION"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED: INCORRECT KEY")
    
    st.info(f"Developer: {OWNER} | {COMPANY}")
    st.stop()

# --- 4. MAIN SIMULATOR INTERFACE ---
st.title(f"🚚 {st.session_state.location} Highway Patrol")
st.sidebar.image("https://flagcdn.com/w320/ht.png", width=150)
st.sidebar.header("🚛 TRUCK CONTROLS")

# Dashboard Gauges
col1, col2, col3 = st.columns(3)
with col1:
    speed = st.sidebar.slider("ACCELERATOR (Gas)", 0, 85, 0)
    st.metric("SPEED", f"{speed} MPH")
with col2:
    rpm = (speed * 30) + 800 if speed > 0 else 800
    st.metric("ENGINE RPM", int(rpm))
with col3:
    st.metric("FUEL LEVEL", f"{st.session_state.fuel}%")

# Driving Mechanics
st.sidebar.markdown("---")
clutch = st.sidebar.checkbox("CLUTCH (Manual Engagement)")
brake = st.sidebar.button("🛑 AIR BRAKE (STOP)")
gear = st.sidebar.selectbox("GEARBOX", ["Reverse", "Neutral", "1st Low", "2nd", "3rd", "4th High"])

# Action: Attach Load
if not st.session_state.attached:
    st.warning("⚠️ STATUS: Trailer not attached. Reverse carefully to the dock.")
    if gear == "Reverse" and speed > 0 and speed < 10:
        if st.button("🔗 COUPLER: ATTACH LOAD"):
            st.session_state.attached = True
            st.session_state.log.append("Load successfully attached in Florida.")
            st.balloons()
            st.rerun()
else:
    st.success("✅ STATUS: Trailer Locked. Destination: New York via I-95.")

# --- 5. THE HIGHWAY MAP (SIMULATION) ---
st.markdown("### 🗺️ REAL-TIME ROAD DATA")
states = ["Florida", "Georgia", "South Carolina", "North Carolina", "Virginia", "New Jersey", "New York"]

if st.session_state.attached and speed > 50:
    time.sleep(0.5)
    current_idx = states.index(st.session_state.location)
    if current_idx < len(states) - 1:
        st.session_state.location = states[current_idx + 1]
        st.session_state.fuel -= 10
        st.session_state.log.append(f"Passed through {st.session_state.location}")

# Visual Representation of the Truck
truck_color = "#00209F" # Haiti Blue
trailer_color = "#D21034" # Haiti Red

st.markdown(f"""
    <div style='background-color: #333; padding: 50px; border-radius: 10px; text-align: center;'>
        <div style='display: inline-block; width: 60px; height: 40px; background-color: {truck_color}; border: 2px solid white;'>CAB</div>
        {"<div style='display: inline-block; width: 150px; height: 45px; background-color: " + trailer_color + "; border: 2px solid white;'>LOAD</div>" if st.session_state.attached else ""}
        <div style='color: white; margin-top: 20px;'>HIGHWAY: I-95 NORTHBOUND</div>
    </div>
""", unsafe_allow_html=True)

# --- 6. FOOTER & CREDENTIALS ---
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 DRIVER LOG")
    for entry in st.session_state.log[-5:]:
        st.text(f"🕒 {entry}")
with c2:
    st.subheader("🏢 COMPANY INFO")
    st.write(f"**Company:** {COMPANY}")
    st.write(f"**Project Lead:** {OWNER}")
    st.write(f"**Contact:** {CONTACT}")

if st.button("RESET SIMULATOR / LOGOUT"):
    st.session_state.auth = False
    st.session_state.attached = False
    st.session_state.location = "Florida"
    st.rerun()
