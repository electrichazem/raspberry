from __future__ import annotations

from plant_controller.system_manager import SystemManager


def main() -> None:
    manager = SystemManager("config.yaml")
    manager.run_forever()


if __name__ == "__main__":
    main()

