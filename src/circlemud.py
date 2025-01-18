import socket

from pprint import pprint

HOST = '0.0.0.0'
PORT = 7777

def main():
    print("CircleMUD-py 01.16.2025 10:30pm ET")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(15)
    try:
        while True:
            client_sock, client_addr = server.accept()
            print(f"Connection established: {client_addr}")

            while True:
                data = client_sock.recv(1024)
                if not data:
                    break

                print(f"Recv: {client_addr}: {data.decode('utf-8')}")
                client_sock.sendall(data)
    except KeyboardInterrupt:
        print("\r\nShutting down.")
        server.close()

if __name__ == "__main__":
    with open('9.zon', 'r') as f:
        zone_info = load_zones(f, 'some_zone_file.zon')
        #pprint(zone_info.__dict__)
        pprint(zone_info.cmd[1].__dict__)
        print("=====")
        pprint(zone_info.cmd[4].__dict__)
    main()
