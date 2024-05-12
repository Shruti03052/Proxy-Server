import socket
import threading
import urllib.request
import hashlib
import time
import logging
import gzip
import io
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CachedResponse:
    def __init__(self, data, timestamp):
        self.data = data  # Cached response data
        self.timestamp = timestamp  # Timestamp when the response was cached

class ProxyServer:
    def __init__(self, host, port, max_requests_per_ip, request_interval, thread_pool_size):
        # Initialize proxy server with provided parameters
        self.host = host  # Proxy server host address
        self.port = port  # Proxy server port number
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
        self.server_socket.bind((self.host, self.port))  # Bind socket to host and port
        self.server_socket.listen(5)  # Listen for incoming connections
        logging.info("Proxy Server running on %s:%d", self.host, self.port)

        # Initialize cache for storing responses
        self.cache = {}  # Cache dictionary to store responses
        self.cache_lock = threading.Lock()  # Lock for thread-safe access to cache
        self.cache_expiry = 60  # Cache expiry time in seconds

        # Rate limiting parameters
        self.max_requests_per_ip = max_requests_per_ip  # Maximum requests allowed per IP address
        self.request_interval = request_interval  # Time interval for rate limiting
        self.ip_request_count = {}  # Dictionary to keep track of request count per IP
        self.last_request_time = time.time()  # Timestamp of the last request

        # Thread pool for handling client requests concurrently
        self.thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)  # ThreadPoolExecutor

    def handle_client(self, client_socket, client_address):
        # Function to handle each client request

        # Extract client IP address
        client_ip = client_address[0]

        # Rate limiting based on IP address
        with threading.Lock():
            current_time = time.time()
            # Reset request count if request interval has passed
            if current_time - self.last_request_time > self.request_interval:
                self.ip_request_count = {}
                self.last_request_time = current_time
            # Increment request count for the client IP
            if client_ip not in self.ip_request_count:
                self.ip_request_count[client_ip] = 0
            self.ip_request_count[client_ip] += 1
            # Close connection if rate limit exceeded
            if self.ip_request_count[client_ip] > self.max_requests_per_ip:
                logging.warning("Rate limit exceeded for IP: %s", client_ip)
                client_socket.close()
                return

        # Receive HTTP request from client
        request = client_socket.recv(1024).decode("utf-8")
        url = request.split()[1]  # Extract URL from request
        logging.info("Client request - IP: %s, URL: %s", client_ip, url)

        # Check if response is cached, fetch from cache if available, otherwise fetch from origin server
        if url in self.cache:
            cached_response = self.cache[url]
            if time.time() - cached_response.timestamp < self.cache_expiry:
                data = cached_response.data
                logging.info("Fetching from cache for URL: %s", url)
            else:
                logging.info("Cached response expired, fetching from web for URL: %s", url)
                data = self.fetch_and_cache(url, client_socket)
        else:
            logging.info("Cache miss fetching from web for URL: %s", url)
            data = self.fetch_and_cache(url, client_socket)

        # Send server response to client
        if data:
            compressed_data = self.compress_content(data)
            if compressed_data:
                client_socket.sendall(compressed_data)
                logging.info("Server response sent for URL: %s", url)
            else:
                logging.error("Failed to compress content for URL: %s", url)
        else:
            logging.error("Error handling client request for URL: %s", url)

        # Close client socket
        client_socket.close()

    def compress_content(self, content):
        # Function to compress content using gzip compression
        try:
            compressed_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb', compresslevel=9) as gzip_compressor:
                gzip_compressor.write(content)
            return compressed_buffer.getvalue()
        except Exception as e:
            logging.error("Error compressing content: %s", e)
            return None

    def fetch_and_cache(self, url, client_socket):
        # Function to fetch content from origin server and cache it
        try:
            response = urllib.request.urlopen(url)
            if response.getcode() == 200:
                data = response.read()  # Read response data
                self.update_cache(url, data)  # Update cache with response data
                return data
            else:
                error_message = f"Error: {response.getcode()} {response.reason}"
                client_socket.sendall(error_message.encode("utf-8"))  # Send error message to client
                return None
        except Exception as e:
            logging.error("Error fetching URL: %s", e)
            client_socket.sendall(b"Error: Failed to fetch URL")  # Send error message to client
            return None

    def update_cache(self, url, data):
        # Function to update cache with response data
        with self.cache_lock:
            self.cache[url] = CachedResponse(data, time.time())
            

    def start(self):
        # Function to start the proxy server
        logging.info("Proxy server started.")
        while True:
            client_socket, client_address = self.server_socket.accept()  # Accept incoming connection
            # Submit the client handling to the thread pool
            self.thread_pool.submit(self.handle_client, client_socket, client_address)

if __name__ == "__main__":
    # Create and start proxy server instance
    proxy = ProxyServer('127.0.0.1', 8888, max_requests_per_ip=10, request_interval=180, thread_pool_size=5)
    proxy_thread = threading.Thread(target=proxy.start)
    proxy_thread.start()
    # Keep the main thread alive by joining the proxy thread
    proxy_thread.join()
