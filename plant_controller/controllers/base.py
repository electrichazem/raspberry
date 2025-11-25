from __future__ import annotations

import time
from typing import Any, Dict


class BaseController:
    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
        self._last_update = 0.0

    def should_run(self, interval: float = 1.0) -> bool:
        now = time.time()
        if now - self._last_update >= interval:
            self._last_update = now
            return True
        return False

    def update(self, *_args: Any, **_kwargs: Any) -> None:
        raise NotImplementedError

