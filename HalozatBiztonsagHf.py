import socket
import time
import re
import hashlib
import requests

# 1.rész port knocking 152.66.249.144 , TCP ports: 1337, 2674, 4011 settimeout=1s
address = '152.66.249.144'
ports = [1337, 2674, 4011]

for p in ports:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(0.1)
		s.connect((address, p))
	except Exception as e:
		print("Knock-knock: " + address + ':' + str(p))
	finally:
		s.close()
		time.sleep(0.4)
		
#2.rész konnektálás
port= 8888
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(0.1)
	s.connect((address, port))
except Exception as e:
	print("connecting is wrong")

# üzenet a szervertől
data = s.recv(1024)
print('Server message: ' + data.decode("utf-8"))

# neptun kód elküldése
neptun_code = 'B3E5I3'
s.sendall(neptun_code.encode("utf-8"))
time.sleep(0.4)

data = s.recv(1024).decode("utf-8")
print('Server message: ' + data)

# server válasz sorokra törése
# hány kérést fog feltenni a szerver?
lines = data.split('\n')
how_many_q = int((re.search("\d", lines[1])).group())

# a 4.mondat az első feladvány
data = lines[3]

#for ciklussal végig megyek a kérdéseken
# csak 1 regex kifejezést használtam
# findall-al megkeresem a regex-re passzoló match-ot --> ennek az eredménye egy 2D-s tömb
# minden kérdésre lefuttatok egy ciklust, amiben kiválogatom külön a számokat és külön a szimbólumokat

for x in range(how_many_q):
	j=0
	sum = 0
	while True:
		if sum == 0:
			sum = int(re.findall(r'(\d+)\s([\+-=])', data)[0][0])
		else:
			number = re.findall(r'(\d+)\s([\+-=])', data)[j][0]
			symbol = re.findall(r'(\d+)\s([\+-=])', data)[j][1]
		
			if (symbol == '='):
				print(sum)
				s.sendall((str(sum)).encode("utf-8"))
				time.sleep(1)
				data = s.recv(1024).decode("utf-8")
				print(data)
				break
			elif (symbol == '+'):
				sum += int(re.findall(r'(\d+)\s([\+-=])', data)[j+1][0])
				j += 1
			elif (symbol == '-'):
				sum -= int(re.findall(r'(\d+)\s([\+-=])', data)[j+1][0])
				j += 1

# eredmény beküldése hash-elve
nepCode_sum_str = neptun_code + str(sum)
h = hashlib.sha1(nepCode_sum_str.encode("utf-8")).hexdigest()
s.sendall(h.encode("utf-8"))
time.sleep(1)

# server válasza
data = s.recv(1024).decode("utf-8")
print('Server message: ', data)

# 0000-val kiegészítés
base_str = neptun_code + str(sum)
x = 0
while True:
	string = base_str + str(x)
	hash_str = hashlib.sha1(string.encode("utf-8")).hexdigest()
	if hash_str[0:4] == "0000": break
	x = x + 1

# 0000-ás hash elküldése
s.sendall(string.encode("utf-8"))
time.sleep(0.5)

data = s.recv(2048).decode("utf-8")
print('Server message: ', data)

# bejelentkezés, cert letöltés 
sess = requests.Session()
url = 'http://152.66.249.144'
data = {'neptun': neptun_code, 'password': 'crysys'}
req = sess.post(url, data=data)

# böngészőben látni lehet,h 'welcome'-ot kell mondania a szervernek,ha sikerült a belépés
if(req.text.find('Welcome') > -1): 
	print("Sikeres belépés!")
else: print('Debug: Sikertelen belépés!')

data = s.recv(2048).decode("utf-8")
print('Server message: ', data)

# GET request: /getcert.php
url='http://152.66.249.144/getcert.php'
req = sess.get(url)
cert = req.text
with open('clientcert.pem', 'w') as cert_file:
    cert_file.write(req.text)

# GET request: /getkey.php
url='http://152.66.249.144/getkey.php'
req = sess.get(url)
key = req.text
with open('clientkey.pem', 'w') as key_file:
    key_file.write(req.text)

# GET request: https://152.66.249.144
url='https://152.66.249.144'
headers = {'User-Agent': 'CrySyS'}
req = sess.get(url, headers=headers, cert=('clientcert.pem', 'clientkey.pem'), verify=False)
key = req.text
with open('https.txt', 'w') as https_file:
    https_file.write(req.text)
print(key)

s.close()