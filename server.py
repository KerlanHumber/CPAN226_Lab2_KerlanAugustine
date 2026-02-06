# This program was modified by Kerlan Augustine / N01375372
import socket
import struct
import argparse

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"[*] Server listening on port {port}")

    try:
        f = None
        expected_seq_num = 0
        buffer = {} 
        
        while True:
            packet, addr = sock.recvfrom(8192)

            if not packet:
                if f:
                    for k in sorted(buffer.keys()):
                        f.write(buffer[k])
                break 

            header = packet[:4]
            sock.sendto(header, addr)

            data = packet[4:]
            seq_num = struct.unpack('!I', header)[0]

            if f is None: f = open(output_file, 'wb')

            if seq_num == expected_seq_num:
                f.write(data)
                expected_seq_num += 1
                while expected_seq_num in buffer:
                    f.write(buffer.pop(expected_seq_num))
                    expected_seq_num += 1
                print(f"[+] Wrote {seq_num}")
            elif seq_num > expected_seq_num:
                buffer[seq_num] = data
            
        if f:
            f.close()
            print(f"[*] SUCCESS: {output_file} is ready.")
            
    except Exception as e:
        print(f"[!] Server Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=12001)
    parser.add_argument("--output", type=str, default="received_final.jpg")
    args = parser.parse_args()
    run_server(args.port, args.output)