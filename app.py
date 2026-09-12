from flask import Flask, render_template, jsonify
from supabase import create_client, Client
import datetime
import os

app = Flask(__name__)

# --- SUPABASE CONFIGURATION ---
# PALITAN MO ITO NG ACTUAL URL AT KEY MO MULA SA SUPABASE
SUPABASE_URL = "https://yqaissxgnnwowmcuwcbz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlxYWlzc3hnbm53b3dtY3V3Y2J6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkxNzk2NDUsImV4cCI6MjEwNDc1NTY0NX0.kNs9COdO_OAVol4vNS41y65Cxne8FhSeubPaHoh3Uyk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_sensor_data():
    try:
        # Kukuha tayo ng huling 20 readings mula sa Supabase
        response = supabase.table('sensor_readings').select('*').order('created_at', desc=False).limit(20).execute()
        data = response.data

        # Kung walang data sa database, magbalik ng zero values
        if not data:
            return jsonify({
                'gas_value': 0, 
                'vibration': 0, 
                'alert': False, 
                'gas_history': [0]*20, 
                'vibration_history': [0]*20, # <--- ITO YUNG KULANG KANINA
                'time_history': ['--:--']*20
            })

        # I-extract ang data para sa graph
        gas_history = [row['gas_value'] for row in data]
        vibration_history = [row['vibration_value'] for row in data] # <--- IDINAGDAG NATIN ITO
        
        # Kunin lang yung oras (HH:MM:SS) mula sa timestamp
        time_history = []
        for row in data:
            dt = datetime.datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            # Adjust sa Philippine time (+8 hours)
            dt = dt + datetime.timedelta(hours=8)
            time_history.append(dt.strftime('%H:%M:%S'))

        # Kunin ang pinakabagong reading para sa current status
        latest = data[-1]
        gas_value = latest['gas_value']
        vibration = latest['vibration_value']
        
        # Alert logic: Kapag ang gas > 500 o may vibration (1)
        alert = gas_value > 500 or vibration == 1

        return jsonify({
            'gas_value': gas_value,
            'vibration': vibration,
            'alert': alert,
            'gas_history': gas_history,
            'vibration_history': vibration_history, # <--- IDINAGDAG NATIN ITO
            'time_history': time_history
        })

    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)