import streamlit as st
import joblib
import pandas as pd
import base64
import os

# ================= CONFIG =================
MAX_CAPACITY = 2.0  # Maximum rated capacity = 100% health

st.set_page_config(
    page_title="EV Battery Monitoring System",
    layout="centered"
)

st.title("🔋 EV Battery Degradation & Fire Risk Monitoring System")
st.markdown("### Software-Based IoT & Machine Learning Dashboard")

degradation_model = joblib.load("models/degradation_model.pkl")
fire_risk_model = joblib.load("models/fire_risk_model.pkl")

def play_buzzer():
    alarm_file = os.path.join(os.getcwd(), "assets", "alarm.wav")
    
    if os.path.exists(alarm_file):
        with open(alarm_file, "rb") as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode()
        st.components.v1.html(
            f"""
            <script>
            let alarmTriggered = false;
            
            function playAlarm() {{
                if (alarmTriggered) return;
                alarmTriggered = true;
                
                const audio = new Audio('data:audio/wav;base64,{audio_base64}');
                audio.volume = 0.8;
                audio.loop = false;
                
                audio.play().then(function() {{
                    console.log('Audio started successfully');
                }}).catch(function(error) {{
                    console.log('Immediate audio play failed:', error);
                    const playOnClick = function() {{
                        audio.play().then(function() {{
                            console.log('Audio started after user interaction');
                        }}).catch(function(err) {{
                            console.log('Audio play failed completely:', err);
                        }});
                        document.removeEventListener('click', playOnClick);
                        document.removeEventListener('keydown', playOnClick);
                    }};
                    
                    document.addEventListener('click', playOnClick);
                    document.addEventListener('keydown', playOnClick);
                    
                    const alertDiv = document.createElement('div');
                    alertDiv.innerHTML = '🚨 ALARM! Click anywhere to play sound 🚨';
                    alertDiv.style.cssText = 'position:fixed;top:10px;left:50%;transform:translateX(-50%);background:red;color:white;padding:10px;border-radius:5px;z-index:9999;font-weight:bold;';
                    document.body.appendChild(alertDiv);
                    
                    setTimeout(() => {{
                        if (document.body.contains(alertDiv)) {{
                            document.body.removeChild(alertDiv);
                        }}
                    }}, 5000);
                }});
            }}
            
            playAlarm();
            </script>
            <div style="display:none; color:red; font-weight:bold;">🚨 AUDIO ALARM SYSTEM ACTIVE 🚨</div>
            """,
            height=0,
        )
        
        st.error("🚨 ALARM ACTIVATED! 🚨")
        
    else:
        st.error("🚨 ALARM! (Audio file not found) 🚨")
        st.warning("⚠️ Audio file 'assets/alarm.wav' not found!")

st.sidebar.header("📡 Battery Sensor Inputs")

temperature = st.sidebar.slider("Ambient Temperature (°C)", 0, 60, 30)
voltage = st.sidebar.slider("Voltage (V)", 3.0, 4.2, 3.7)
current = st.sidebar.slider("Current (A)", 0.5, 3.0, 1.5)

predicted_capacity = float(degradation_model.predict([[temperature]])[0])
fire_risk = int(fire_risk_model.predict([[temperature, predicted_capacity]])[0])

# ================= BATTERY HEALTH (0–100%) =================
battery_health = (predicted_capacity / MAX_CAPACITY) * 100
battery_health = max(0, min(battery_health, 100))

st.subheader("📊 Battery Status")

col1, col2, col3 = st.columns(3)
col1.metric("🌡 Temperature (°C)", temperature)
col2.metric("⚡ Voltage (V)", f"{voltage:.2f}")
col3.metric("🔌 Current (A)", f"{current:.2f}")

st.metric("🔋 Predicted Capacity", f"{predicted_capacity:.2f}")
st.metric("📈 Battery Health (%)", f"{battery_health:.1f}")

st.subheader("🔥 Fire Risk Status")

alarm = False

if fire_risk == 0:
    st.success("🟢 SAFE")
elif fire_risk == 1:
    st.warning("🟡 WARNING – Limit Exceeded")
    alarm = True
else:
    st.error("🔴 CRITICAL – Limit Exceeded")
    alarm = True

if alarm:
    st.warning("🔔 Alarm Triggered!")
    play_buzzer()

st.subheader("📜 Recent Readings")

if "history" not in st.session_state:
    st.session_state.history = []

st.session_state.history.append({
    "Temperature": temperature,
    "Voltage": voltage,
    "Current": current,
    "Capacity": round(predicted_capacity, 2),
    "Health (%)": round(battery_health, 1),
    "Risk": ["Safe", "Warning", "Critical"][fire_risk]
})

st.dataframe(pd.DataFrame(st.session_state.history[-5:]))

st.markdown("---")
st.caption("🔄 Real-time monitoring (software-based IoT)")
