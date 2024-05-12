import socket
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thread pool with a defined size
thread_pool_size = 5
thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)

# Function to simulate a client sending a request to the proxy server
def simulate_client(server_host, server_port, request_path, thread_id, results):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        # Formulate a simple HTTP GET request
        request = f"GET {request_path} HTTP/1.1\r\nHost: {server_host}\r\nConnection: keep-alive\r\n\r\n"

        # Log the thread ID and start time
        start_time = time.time()
        logging.info("Thread %d started.", thread_id)

        # Send the request
        client_socket.sendall(request.encode("utf-8"))

        # Receive the response
        response = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response += data
        
        # Store the result for analysis later
        results[thread_id] = {
            "response_length": len(response),
            "error": None,
            "execution_time": time.time() - start_time  # Capture execution time
        }

        client_socket.close()

        # Log completion time
        logging.info("Thread %d completed in %.2f seconds.", thread_id, results[thread_id]['execution_time'])
    except Exception as e:
        # Record errors if any occur
        results[thread_id] = {
            "response_length": None,
            "error": str(e)
        }

# Proxy server host and port
server_host = '127.0.0.1'
server_port = 8888  

# The path to request from the proxy server
request_path = 'https://www.amazon.in/'  

# Number of threads to simulate (number of clients)
num_threads = 7  #

# Simulate a slight delay between starting threads to avoid overwhelming the server too quickly
start_delay = 0.1  # Time between thread starts in seconds

# Dictionary to store test results
results = {}

# Create and start multiple threads
threads = []
for i in range(num_threads):
    if i >= thread_pool_size:
        # Indicate that the thread pool might be at capacity
        logging.warning("Thread pool might be exhausted. Submitting additional threads.")

    thread = threading.Thread(target=simulate_client, args=(server_host, server_port, request_path, i, results))
    threads.append(thread)
    thread.start()
    time.sleep(start_delay)  # Add a delay between thread starts

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Analyze the results
print("Stress test complete.")
for thread_id, result in results.items():
    if result["error"]:
        print(f"Thread {thread_id}: Error - {result['error']}")
    else:
        print(f"Thread {thread_id}: Response Length - {result['response_length']} | Execution Time - {result['execution_time']:.2f} seconds")
