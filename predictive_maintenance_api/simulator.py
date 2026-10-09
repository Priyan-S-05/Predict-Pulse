import requests
import time
import random
import os

API_BASE = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{API_BASE.rstrip('/')}/predict"

def generate_sensor_data():
    """Generates realistic machine sensor readings."""
    m_type = random.choice(["L", "M", "H"])
    
    # Simulate normal operating ranges with occasional 'scary' spikes
    return {
        "type": m_type,
        "air_temp": round(random.uniform(295.0, 305.0), 1),
        "process_temp": round(random.uniform(305.0, 315.0), 1),
        "rotational_speed": random.randint(1300, 1600),
        "torque": round(random.uniform(35.0, 50.0), 1),
        "tool_wear": random.randint(0, 250) # High tool wear usually triggers failure
    }

def run_simulator():
    print(f"🚀 Starting Sensor Simulator... Sending data to {API_URL}")
    print("Press Ctrl+C to stop.")
    
    while True:
        data = generate_sensor_data()
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                result = response.json()
                status = "⚠️ FAILURE" if result["Failure"] else "✅ HEALTHY"
                print(f"[SENT] Speed: {data['rotational_speed']} | Wear: {data['tool_wear']} | Result: {status}")
            else:
                print(f"❌ Server Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
        
        # Wait 3 seconds before the next 'sensor reading'
        time.sleep(3)

if __name__ == "__main__":
    run_simulator()