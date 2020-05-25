import socket
import threading
import binascii
import asyncio
from websocket import create_connection
import time
import json

port = 1234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', port))
gps_info = 's'

def decodethis(data):
    record = int(data[18:20], 16)
    timestamp = int(data[20:36], 16)
    lon = int(data[38:46], 16)
    lat = int(data[46:54], 16)
    alt = int(data[54:58], 16)
    sats = int(data[62:64], 16) #maybe
    print("Record: " + str(record) + "\nTimestamp: " + str(timestamp) + "\nLat,Lon: " + str(lat) + ", " + str(lon) + "\nAltitude: " + str(alt) + "\nSats: " +  str(sats) )
    return "0000" + str(record).zfill(4)


def decode_gps_data(data):
    timestamp = int(data[20:36], 16)
    lon = int(data[38:46], 16)
    lat = int(data[46:54], 16)
    info ='"Timestamp":' + str(timestamp) + ','+'"Lat":' + str(lat) + ','+'"Long":' + str(lon)
    return(info)



def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        raw_imei = conn.recv(1024)
        imei = raw_imei.decode('utf-8')

        if len(imei)>2:
            try:
                message = '\x01'
                message = message.encode('utf-8')
                conn.send(message)
            except:
                print("Error sending reply. Maybe it's not our device")

            try:
                data = conn.recv(1024)
                recieved = binascii.hexlify(data)
                record = decodethis(recieved).encode('utf-8')
                gps_info=decode_gps_data(recieved)
                str_imei=str(imei)
                print(str_imei)
                gps_to_ws = '"imei":' + str_imei + ',' + gps_info
                ws = create_connection("ws://localhost:8000/receive/")
                print("Sending 'gps...")
                ws.send(gps_to_ws)
                print("Sent")
                time.sleep(1)
                ws.close()
                print(" ws closed")
                conn.send(record)
            except socket.error:
                print("Error Occured.")
                break
        else:
            break
    conn.close()

def start():
    s.listen()
    print(" Server is listening ...")
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
start()

