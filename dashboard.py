import streamlit as st
import pandas as pd
import base64
import os
import random
import time

# ===== CORE IMPORTS =====
from core.battery_state import BatteryState
from core.predictor import predict_capacity, predict_fire_risk
from core.logger import log_event

# ================= CONFIG =================
MAX_CAPACITY = 2.0

st.set_page_config(
    page_title="EV Battery Monitoring System",
    layout="centered"
)

st.title("🔋 EV Battery Degradation & Fire Risk Monitoring System")
st.markdown("### Software-Based IoT & Machine Learning Dashboard")

# ================= SESSION STATE =================
if "prev_risk" not in st.session_state:
    st.session_state.prev_risk = 0

# ================= BUZZER =================
def play_buzzer():
    alarm_file = os.path.join("assets", "alarm.wav")

    if not os.path.exists(alarm_file):
        st.error("⚠️ alarm.wav not found")
        return

    with open(alarm_file, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()

    st.components.v1.html(
        f"""
        <script>
            const audio = new Audio("data:audio/wav;base64,{audio_base64}");
            audio.volume = 0.9;
            audio.play().catch(() => {{
                document.addEventListener("click", () => audio.play(), {{ once: true }});
            }});
        </script>
        """,
        height=0,
    )

# ================= SIDEBAR =================
st.sidebar.header("📡 Battery Sensor Inputs")

mode = st.sidebar.radio("Mode Selection", ["Auto (Real-Time)", "Manual"])

# ================= AUTO MODE =================
if mode == "Auto (Real-Time)":

    if "temp_sim" not in st.session_state:
        st.session_state.temp_sim = 30
        st.session_state.volt_sim = 3.9
        st.session_state.curr_sim = 1.2

    # Smooth realistic behavior
    st.session_state.temp_sim += random.uniform(-0.2, 0.2)
    st.session_state.curr_sim += random.uniform(-0.05, 0.05)

    if random.random() < 0.1:
        st.session_state.temp_sim += random.uniform(0.3, 0.7)

    st.session_state.volt_sim -= random.uniform(0.0005, 0.002)

    # Clamp
    st.session_state.temp_sim = max(25, min(60, st.session_state.temp_sim))
    st.session_state.volt_sim = max(3.2, min(4.2, st.session_state.volt_sim))
    st.session_state.curr_sim = max(0.5, min(2.5, st.session_state.curr_sim))

    temperature = st.session_state.temp_sim
    voltage = st.session_state.volt_sim
    current = st.session_state.curr_sim

# ================= MANUAL MODE =================
else:
    temperature = st.sidebar.slider("Temperature (°C)", 0, 60, 30)
    voltage = st.sidebar.slider("Voltage (V)", 3.0, 4.2, 3.7)
    current = st.sidebar.slider("Current (A)", 0.5, 3.0, 1.5)

# ================= ML =================
predicted_capacity = predict_capacity(temperature)

battery_state = BatteryState(
    temperature=temperature,
    voltage=voltage,
    current=current,
    capacity=predicted_capacity
)

fire_risk = predict_fire_risk(
    battery_state.temperature,
    battery_state.capacity
)

# ================= HEALTH =================
battery_health = (battery_state.capacity / MAX_CAPACITY) * 100
battery_health = max(0, min(battery_health, 100))

# ================= DISPLAY =================
st.subheader("📊 Battery Status")

col1, col2, col3 = st.columns(3)
col1.metric("🌡 Temperature (°C)", f"{battery_state.temperature:.2f}")
col2.metric("⚡ Voltage (V)", f"{battery_state.voltage:.2f}")
col3.metric("🔌 Current (A)", f"{battery_state.current:.2f}")

st.metric("🔋 Predicted Capacity", f"{battery_state.capacity:.2f}")
st.metric("📈 Battery Health (SOH)", f"{battery_health:.1f}%")

col4, col5 = st.columns(2)
col4.metric("🔋 SOC", f"{battery_state.soc():.1f}%")
col5.metric("⚡ Power", f"{battery_state.power():.2f} W")

# ================= FIRE RISK =================
st.subheader("🔥 Fire Risk Status")

alarm = False

if fire_risk == 0:
    st.success("🟢 SAFE")
elif fire_risk == 1:
    st.warning("🟡 WARNING")
    alarm = True
else:
    st.error("🔴 CRITICAL")
    alarm = True

# ================= LOG =================
if fire_risk > st.session_state.prev_risk:
    log_event(battery_state, fire_risk)

st.session_state.prev_risk = fire_risk

# ================= BUZZER =================
if alarm:
    st.warning("🔔 Buzzer Activated")
    play_buzzer()

# ================= HISTORY =================
st.subheader("📜 Recent Readings")

if "history" not in st.session_state:
    st.session_state.history = []

st.session_state.history.append({
    "Temp": round(battery_state.temperature, 2),
    "Volt": round(battery_state.voltage, 2),
    "Curr": round(battery_state.current, 2),
    "Risk": ["Safe", "Warning", "Critical"][fire_risk]
})

st.dataframe(pd.DataFrame(st.session_state.history[-5:]))

# ================= FOOTER =================
st.markdown("---")
st.caption("🔄 Conference-aligned Battery Monitoring System")

# ================= AUTO REFRESH =================
if mode == "Auto (Real-Time)":
    time.sleep(2)
    st.rerun()