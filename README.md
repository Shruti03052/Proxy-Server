# Proxy Server and Client

This project consists of a proxy server and a corresponding client that enables users to access web content through the proxy.

## Features

### Proxy Server
- **Caching Mechanism:** The server caches responses from visited URLs to improve performance and reduce redundant requests.
- **Rate Limiting:** Implements rate limiting based on IP addresses to prevent abuse and ensure fair usage.
- **Gzip Compression:** Compresses content before sending it to the client to reduce bandwidth usage.
- **Error Handling:** Handles errors gracefully, providing appropriate error messages to the client when fetching URLs fails.

### Proxy Client
- **HTTP Request Formatting:** Constructs HTTP GET requests with the requested URL and sends them to the proxy server.
- **Response Handling:** Receives response data from the proxy server in chunks and aggregates them to form the complete response.
- **Saving Response to File:** Saves the received response content to an HTML file, supporting gzip-compressed responses.
- **Open in Browser:** Opens the saved HTML file in the default web browser for convenient viewing.

## Usage

### Proxy Server
1. Run the `server.py` script to start the proxy server.
2. Customize the proxy settings as needed, such as maximum requests per IP and cache expiry time.

### Proxy Client
1. Run the `client.py` script to start the proxy client.
2. Enter the URL of the website you want to access.
3. Specify the filename to save the response content.
4. View the response in your default web browser.

## Dependencies
- Python 3.x


