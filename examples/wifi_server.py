import picar_4wd as fc
import socket
import re

HOST = "192.168.1.109" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

speed = 30

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while 1:
        client, clientInfo = s.accept()
        print("server recv from: ", clientInfo)
        battery = int(((fc.power_read() - 6.33) / (8.33 - 6.33)) * 100)
        cpu_temp = fc.cpu_temperature()
        data = client.recv(1024)      # receive 1024 Bytes of message in binary format
        if data != b"":
            data = str(data.decode("utf-8"))
            if data == "up":
                fc.forward(speed)
            elif data == "down":
                fc.backward(speed)
            elif data == "right":
                fc.turn_right(speed)
            elif data == "left":
                fc.turn_left(speed)
            else:
                try:
                    int(data)
                    if int(data) in range(0,101):
                        speed = int(data)
                        print(speed)
                except:
                    print("Speed not an integer")
                fc.stop()
            #client.sendall(dat.encode())
            client.sendall(str(cpu_temp).encode() + b" " + str(battery).encode() + b"%" + b" ")
            #client.sendall(data) # Echo back to client
            #info = battery_life
            #client.sendall(battery_life)

    #except:
    #    print("Closing socket")
    #    client.close()
    #    s.close()