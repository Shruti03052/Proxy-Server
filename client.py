import socket
import gzip
import io
import webbrowser

class ProxyClient:
    def __init__(self, host, port):
        # Initialize ProxyClient with host and port of the proxy server
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))  # Connect to the proxy server

    def request_url(self, url):
        # Function to send HTTP GET request to the proxy server and receive response
        request = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(url, self.host)
        self.client_socket.sendall(request.encode("utf-8"))
        response = b""  # Initialize an empty byte string to store the response
        while True:
            data = self.client_socket.recv(4096)  # Receive data in chunks of 4096 bytes
            if not data:
                break  # Break the loop when there's no more data
            response += data  # Append the received data to the response
        return response

    def save_to_html(self, response, filename):
        # Function to save the response to an HTML file
        # Check if the response is gzip compressed
        if response.startswith(b'\x1f\x8b'):
            # Decompress the gzip-compressed response
            with gzip.GzipFile(fileobj=io.BytesIO(response), mode='rb') as gzip_file:
                decompressed_response = gzip_file.read()
            # Write the decompressed response to the file
            with open(filename, "wb") as f:
                f.write(decompressed_response)
        else:
            # Write the response directly to the file
            with open(filename, "wb") as f:
                f.write(response)
    
    def open_in_browser(self, filename):
        # Function to open the HTML file in the default web browser
        webbrowser.open_new_tab(filename)

if __name__ == "__main__":
    # Main program
    # Create ProxyClient instance
    client = ProxyClient('127.0.0.1', 8888)
    # Prompt user to enter URL
    url = input("Enter URL: ")
    # Send request to the proxy server and receive response
    response = client.request_url(url)
    # Prompt user to enter filename to save the response
    filename = input("Enter filename to save: ")
    # Save the response to the specified filename
    client.save_to_html(response, filename)
    print("Response saved to", filename)
    # Open the saved HTML file in the default web browser
    client.open_in_browser(filename)
