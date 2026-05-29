#!/usr/bin/env python3
"""Minimal browser live preview for rendered SAPIEN frames."""

from __future__ import annotations

import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

import cv2
import numpy as np


LOGGER = logging.getLogger(__name__)


class FrameBuffer:
    """Thread-safe latest-frame store."""

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._jpeg: bytes | None = None
        self._sequence = 0
        self._closed = False

    def update(self, image_rgb: np.ndarray) -> None:
        ok, encoded = cv2.imencode(".jpg", image_rgb[:, :, ::-1], [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not ok:
            raise RuntimeError("Failed to encode live preview frame")
        with self._condition:
            self._jpeg = encoded.tobytes()
            self._sequence += 1
            self._condition.notify_all()

    def wait_frame(self, last_sequence: int) -> tuple[int, bytes] | None:
        with self._condition:
            while (self._jpeg is None or self._sequence == last_sequence) and not self._closed:
                self._condition.wait(timeout=0.5)
            if self._closed:
                return None
            if self._jpeg is None:
                return None
            return self._sequence, self._jpeg

    def close(self) -> None:
        with self._condition:
            self._closed = True
            self._condition.notify_all()


class LivePreviewServer:
    """Small MJPEG HTTP server used for browser-based live playback."""

    def __init__(self, host: str, port: int) -> None:
        self.buffer = FrameBuffer()
        handler = self._make_handler(self.buffer)
        self.server = ThreadingHTTPServer((host, port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.url = f"http://{host}:{self.server.server_port}"

    def start(self) -> None:
        self.thread.start()
        LOGGER.info("实时预览地址：%s", self.url)

    def update(self, image_rgb: np.ndarray) -> None:
        self.buffer.update(image_rgb)

    def close(self) -> None:
        self.buffer.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)

    @staticmethod
    def _make_handler(buffer: FrameBuffer) -> type[BaseHTTPRequestHandler]:
        class Handler(BaseHTTPRequestHandler):
            server_version: ClassVar[str] = "SapienLivePreview/1.0"

            def do_GET(self) -> None:  # noqa: N802
                if self.path in ("/", "/index.html"):
                    self._write_index()
                elif self.path == "/stream.mjpg":
                    self._write_stream()
                else:
                    self.send_error(404)

            def log_message(self, fmt: str, *args: object) -> None:
                LOGGER.debug("live-preview: " + fmt, *args)

            def _write_index(self) -> None:
                body = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAPIEN 实时预览</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #111820; color: #edf2f7; }
    header { padding: 14px 18px; border-bottom: 1px solid #2b3642; }
    main { padding: 18px; }
    img { width: min(100%, 1180px); background: #05070a; border-radius: 6px; display: block; }
    p { color: #aeb9c5; margin: 6px 0 0; }
  </style>
</head>
<body>
  <header>
    <strong>SAPIEN Franka Panda 实时渲染预览</strong>
    <p>浏览器会显示当前正在渲染的帧；程序结束后可在离线回放页面查看完整视频。</p>
  </header>
  <main>
    <img src="/stream.mjpg" alt="SAPIEN 实时渲染画面">
  </main>
</body>
</html>
"""
                data = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _write_stream(self) -> None:
                self.send_response(200)
                self.send_header("Age", "0")
                self.send_header("Cache-Control", "no-cache, private")
                self.send_header("Pragma", "no-cache")
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self.end_headers()
                last_sequence = -1
                while True:
                    frame = buffer.wait_frame(last_sequence)
                    if frame is None:
                        break
                    last_sequence, jpeg = frame
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(jpeg)}\r\n\r\n".encode("ascii"))
                    self.wfile.write(jpeg)
                    self.wfile.write(b"\r\n")

        return Handler
