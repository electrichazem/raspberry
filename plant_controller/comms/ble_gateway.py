from __future__ import annotations

import json
import threading
from queue import Queue, Empty
from typing import Callable, Optional


try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None  # type: ignore


class BLEGateway:
    def __init__(self, port: str, baudrate: int, enabled: bool = True) -> None:
        self.enabled = enabled and serial is not None
        self._port = port
        self._baudrate = baudrate
        self._serial = None
        self._rx_queue: "Queue[str]" = Queue()
        if self.enabled:
            self._serial = serial.Serial(port, baudrate=baudrate, timeout=1)
            self._reader = threading.Thread(target=self._read_loop, daemon=True)
            self._reader.start()

    def _read_loop(self) -> None:
        assert self._serial
        while True:
            try:
                line = self._serial.readline().decode("utf-8").strip()
            except Exception:
                continue
            if line:
                self._rx_queue.put(line)

    def poll_command(self) -> Optional[dict]:
        if not self.enabled:
            return None
        try:
            line = self._rx_queue.get_nowait()
            return json.loads(line)
        except Empty:
            return None
        except json.JSONDecodeError:
            return None

    def publish_state(self, payload: dict) -> None:
        if not self.enabled or not self._serial:
            return
        try:
            self._serial.write((json.dumps(payload) + "\n").encode("utf-8"))
        except Exception:
            pass

