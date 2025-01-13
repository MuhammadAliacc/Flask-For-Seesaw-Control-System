from flask import Flask, request, jsonify, render_template
from waitress import serve
import subprocess
import threading
import time
import os
import sys
import socket
import psutil

app = Flask(__name__)

sensor_data = {
    "position": 0.0,
    "speed": 0.0,
    "angle_current": 0.0,
    "angle_set": 0.0
}

interface_name = "Ethernet"

def get_specific_ip(interface_name):
    for interface, addrs in psutil.net_if_addrs().items():
        if interface == interface_name:
            for addr in addrs:
                if addr.family == socket.AF_INET:  
                    return addr.address
    return None
host = get_specific_ip(interface_name)

def check_port_availability(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('127.0.0.1', port))
        return result != 0  

@app.route('/')
def index():
    return render_template('hardware_web_page.html')

@app.route('/update-sensor', methods=['POST'])
def update_sensor():
    data = request.json
    sensor_data["position"] = data.get("position", sensor_data["position"])
    sensor_data["speed"] = data.get("speed", sensor_data["speed"])
    sensor_data["angle_current"] = data.get("angle_current", sensor_data["angle_current"])
    return jsonify({"message": "Sensor data updated successfully!"}), 200

@app.route('/get-data', methods=['GET'])
def get_data():
    return jsonify(sensor_data), 200

@app.route('/set-angle', methods=['POST'])
def set_angle():
    data = request.json
    sensor_data["angle_set"] = data.get("angle_set", sensor_data["angle_set"])
    return jsonify({"message": "Set angle updated successfully!"}), 200

# -------------------- Setting up server ---> 
def run_server(host, port):
    url = f'http://{host}:{port}/'
    print(f'Hardware URL: {url}')
    app.debug = True
    serve(app, host=host, port=port)
    print('hardware server stoped ... ')

def open_browser(host, port):
    url = f'http://{host}:{port}/'

    chrome_path = "C:\Program Files\Internet Explorer\iexplore.exe"
    time.sleep(0.5)
    try:
        subprocess.Popen([chrome_path, url])
        print('Browser opened')
    except Exception as e:
        print(f"Error occurred when opening browser: {e}")

def run_script(script_name, host, port):
    try:
        script_path = os.path.join(os.getcwd(), script_name)
        if not os.path.exists(script_path):
            print(f"Error: Script '{script_name}' does not exist in the current directory.")
            return
        command = [sys.executable, script_path, host]
        subprocess.Popen(command)
        print(f"'{script_name}' started successfully.")
    except Exception as e:
        print(f"Error starting '{script_name}': {str(e)}")

def start_beam(host, port):
    run_script('beam.py', host, port)

def start_camera(host, port):
    run_script('camera.py', host, port)

if __name__ == '__main__':
    host = get_specific_ip(interface_name)
    port = 5002

    if not host:
        print("Error: Could not find IP address for the specified interface.")
        sys.exit(1)

    if not check_port_availability(port):
        print(f"Port {port} is already in use. Exiting...")
        sys.exit(1)

    host = f"{host}"
    
    server_thread = threading.Thread(target=run_server, args=(host, port))
    server_thread.start()

    beam_thread = threading.Thread(target=start_beam, args=(host, port))
    beam_thread.start()

    camera_thread = threading.Thread(target=start_camera, args=(host, port))
    camera_thread.start()

    open_browser(host, port)
