import sys
import asyncio
import ssl
import json
from aiohttp import web, ClientSession
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QSystemTrayIcon, QMenu, QAction, QStyle, QFileDialog, QHBoxLayout
)
from qasync import QEventLoop, asyncSlot
from pathlib import Path

SETTINGS_FILE = 'server_settings.json'

class ServerController:
    def __init__(self):
        self.runner = None
        self.site = None
        self.backend_url = None
        self.static_path = Path(".")

    async def handle_request(self, request):
        static_file = self.static_path / request.path.strip("/")
        if static_file.exists():
            return web.FileResponse(static_file)
        elif self.backend_url:
            target_url = f"{self.backend_url}{request.rel_url}"
            async with ClientSession() as session:
                async with session.request(
                    method=request.method,
                    url=target_url,
                    headers=request.headers,
                    data=await request.read()
                ) as resp:
                    body = await resp.read()
                    return web.Response(status=resp.status, body=body, headers=resp.headers)
        return web.Response(status=404, text="Not Found")

    async def start_server(self, port, static_path, backend_url, use_ssl):
        self.backend_url = backend_url
        self.static_path = Path(static_path)

        app = web.Application()
        app.router.add_route('*', '/{tail:.*}', self.handle_request)

        self.runner = web.AppRunner(app)
        await self.runner.setup()

        ssl_context = None
        if use_ssl:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain('cert.pem', 'key.pem')

        self.site = web.TCPSite(self.runner, '0.0.0.0', port, ssl_context=ssl_context)
        await self.site.start()

    async def stop_server(self):
        if self.runner:
            await self.runner.cleanup()

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breeze Web Server")
        self.controller = ServerController()
        self.init_ui()
        self.create_tray_icon()
        self.load_settings()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout()

        self.port_input = QLineEdit()
        self.path_input = QLineEdit()
        self.backend_input = QLineEdit()
        self.ssl_checkbox = QPushButton("Enable SSL")
        self.ssl_checkbox.setCheckable(True)

        browse_btn = QPushButton("Browse Static Path")
        browse_btn.clicked.connect(self.browse_static_path)

        self.status_label = QLabel("Status: Stopped")
        self.start_btn = QPushButton("Start Server")
        self.stop_btn = QPushButton("Stop Server")

        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_input)

        layout.addWidget(QLabel("Static File Path:"))
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)

        layout.addWidget(QLabel("Reverse Proxy Backend URL:"))
        layout.addWidget(self.backend_input)

        layout.addWidget(self.ssl_checkbox)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.start_btn.clicked.connect(self.start_clicked)
        self.stop_btn.clicked.connect(self.stop_clicked)

        self.setLayout(layout)

    def browse_static_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Static Directory")
        if directory:
            self.path_input.setText(directory)

    def save_settings(self):
        settings = {
            "port": self.port_input.text(),
            "path": self.path_input.text(),
            "backend": self.backend_input.text(),
            "ssl": self.ssl_checkbox.isChecked()
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.port_input.setText(settings.get("port", "8443"))
                self.path_input.setText(settings.get("path", "./static"))
                self.backend_input.setText(settings.get("backend", "http://localhost:5000"))
                self.ssl_checkbox.setChecked(settings.get("ssl", False))
        except FileNotFoundError:
            self.port_input.setText("8443")
            self.path_input.setText("./static")
            self.backend_input.setText("http://localhost:5000")
            self.ssl_checkbox.setChecked(False)

    @asyncSlot()
    async def start_clicked(self):
        port = int(self.port_input.text())
        path = self.path_input.text()
        backend = self.backend_input.text()
        use_ssl = self.ssl_checkbox.isChecked()
        self.save_settings()
        await self.controller.start_server(port, path, backend, use_ssl)
        self.status_label.setText("Status: Running")

    @asyncSlot()
    async def stop_clicked(self):
        await self.controller.stop_server()
        self.status_label.setText("Status: Stopped")

    def create_tray_icon(self):
        # Create tray icon with About Us option
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray.setVisible(True)

        menu = QMenu()
        about_action = QAction("About Us", self)
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        about_action.triggered.connect(self.show_about_dialog)

        menu.addAction(show_action)
        menu.addAction(about_action)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self.on_tray_icon_activated)

    def show_about_dialog(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "About Us", "Breeze Web Server GUI Version 1.0 Created by Mahendra.uk")

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()

if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    loop = QEventLoop(app_qt)
    asyncio.set_event_loop(loop)
    window = ServerGUI()
    with loop:
        loop.run_forever()
