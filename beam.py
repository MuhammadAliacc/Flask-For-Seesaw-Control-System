import serial
import time
import requests
import random
import sys
# Settings
com_port = 'COM3' 
baud_rate = 115200
request_interval = 0.2  # Interval to request angle in seconds

def update_webserver(angle):
    payload = {"angle_current": angle}
    try:
        response = requests.post(server_url_update, json=payload)
        if response.status_code == 200:
            print("Sensor data updated successfully!")
        else:
            print(f"Failed to update sensor data: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def get_setpoint_from_webserver():
    try:
        response = requests.get(server_url_get)
        if response.status_code == 200:
            data = response.json()
            return data["angle_set"]
        else:
            print(f"Failed to get setpoint: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def main():
    # Open Serial Connection
    ser = serial.Serial(com_port, baud_rate)
    time.sleep(2)  # Wait for the serial connection to establish

    # Send 'y' to start the calibration process
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            print(line)
            if "Please enter 'y' to start the calibration process:" in line:
                ser.write(b'y\n')
                break

    # Print messages until calibration is finished
    calibration_finished = False
    while not calibration_finished:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            print(line)
            if "Calibration finished." in line:
                calibration_finished = True

    previous_setpoint = None  

    # Main communication loop
    while True:
        r_num = random.uniform(0.2, 0.22) 

        setpoint = get_setpoint_from_webserver()

        start_time = time.time()
        ser.write(f"{setpoint}\n".encode())
        end_time = time.time()

        time.sleep(r_num)

if __name__ == "__main__":
    
    host = sys.argv[1]
    
    port = 5002
    
    server_url_update = f"http://{host}:{port}/update-sensor"  
    server_url_get = f"http://{host}:{port}/get-data"  

    main()