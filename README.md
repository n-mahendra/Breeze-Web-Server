Breeze Web Server is a Python-based Nginx-like Server with a Graphical User Interface (GUI). It allows users to serve static files, set up a reverse proxy to a backend server, and optionally enable SSL, all managed through a simple desktop application.

Features
Static File Serving: Serve content directly from a specified local directory.
Reverse Proxy: Forward requests to a different backend URL, acting as an intermediary.
SSL/HTTPS Support: Secure connections using cert.pem and key.pem files (requires user-provided certificates).
Intuitive GUI: A PyQt5-based interface for easy configuration of port, static path, backend URL, and SSL settings.
System Tray Integration: Minimize the application to the system tray for discreet background operation, with options to show/hide the window and exit.
Persistent Settings: Saves and loads server configurations (port, paths, SSL preference) to server_settings.json for convenience.
Asynchronous Operations: Utilizes asyncio and aiohttp for efficient handling of web requests and qasync to integrate with the PyQt event loop.

Technologies Used
Python: The core programming language.
aiohttp: Asynchronous HTTP client/server framework for handling web requests.
PyQt5: GUI toolkit for creating the desktop application.
qasync: Bridges asyncio event loops with PyQt's event loop.

How to Use
Clone the repository.
Install dependencies: pip install aiohttp PyQt5 qasync
Run the application: python web.py
Configure: Use the GUI to set your desired port, static file path, and backend URL. Enable SSL if you have cert.pem and key.pem in the same directory as the script.
Start/Stop: Click "Start Server" or "Stop Server" buttons to manage the server.
Minimize to Tray: The application will minimize to the system tray, providing quick access to show the window or quit.
