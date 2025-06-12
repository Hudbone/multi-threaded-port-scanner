import socket
import threading
from queue import Queue
import logging
import csv

logging.basicConfig(
    filename='scanner.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

csv_file = open("scan_results.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Port", "Status", "Banner"])

target = "127.0.0.1"
start_port = 1
end_port = 65535
num_threads = 300

q = Queue()
for port in range(start_port, end_port + 1):
    q.put(port)

def scan():
    while not q.empty():
        a_port = q.get()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((target, a_port))
            if result == 0:
                try:
                    s.sendall(b"Hello\r\n")
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                except (socket.timeout, socket.error, ConnectionResetError):
                    banner=""
                if not banner:
                    banner="No banner"
                message = f"Port {a_port} is open - Banner: {banner}"
                print(message)
                logging.info(message)
                csv_writer.writerow([a_port, "Open", banner])
            s.close()
        except (socket.timeout, socket.error):
            pass
        q.task_done()

threads = []
for _ in range(num_threads):
    t = threading.Thread(target=scan)
    t.start()
    threads.append(t)

q.join()
csv_file.close()
print("Scan complete. Results saved to scanner.log and scan_results.csv")