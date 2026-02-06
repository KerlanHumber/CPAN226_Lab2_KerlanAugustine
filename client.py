# This program was modified by Kerlan Augustine / N01375372
import socket
import argparse
import time
import os
import struct

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    server_address = (target_ip, target_port)
    sequence_number = 0

    if not os.path.exists(input_file):
        return

    print(f"[*] Starting reliable transfer of {input_file}...")

    try:
        with open(input_file, 'rb') as f:
            while True:
                chunk = f.read(4092)
                if not chunk: break

                header = struct.pack('!I', sequence_number)
                packet = header + chunk

                acked = False
                while not acked:
                    try:
                        sock.sendto(packet, server_address)
                        data, addr = sock.recvfrom(1024)
                        ack_num = struct.unpack('!I', data[:4])[0]
                        
                        if ack_num == sequence_number:
                            acked = True 
                    except (socket.timeout, struct.error):
                        print(f"[*] Retransmitting packet {sequence_number}...")

                sequence_number += 1 

        print("[*] Sending EOF...")
        for _ in range(15):
            sock.sendto(b'', server_address)
            time.sleep(0.01)

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_port", type=int, default=12000)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()
    run_client("127.0.0.1", args.target_port, args.file)