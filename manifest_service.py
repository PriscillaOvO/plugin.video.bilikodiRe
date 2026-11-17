import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import xbmc
import xbmcgui
import xbmcvfs

MANIFEST_DIR = Path(xbmcvfs.translatePath("special://temp/plugin.video.bilikodiRe/"))
PORT_PROPERTY = "BilikodiRe.ManifestPort"


class ManifestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        match = re.fullmatch(r"/([0-9]+\.mpd)", self.path)
        if not match:
            self.send_error(404)
            return
        try:
            document = (MANIFEST_DIR / match[1]).read_bytes()
        except OSError:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/dash+xml")
        self.send_header("Content-Length", str(len(document)))
        self.end_headers()
        self.wfile.write(document)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 0), ManifestHandler) as server:
        window = xbmcgui.Window(10000)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        window.setProperty(PORT_PROPERTY, str(server.server_port))
        try:
            xbmc.Monitor().waitForAbort()
        finally:
            window.clearProperty(PORT_PROPERTY)
            server.shutdown()
            thread.join()
