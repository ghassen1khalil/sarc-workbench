from pathlib import Path

from frontend.host.main_window import run_app


def main() -> None:
    config_path = Path(__file__).resolve().parents[2] / "conf" / "application_config.yaml"
    run_app(config_path)


if __name__ == "__main__":
    main()
