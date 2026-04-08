"""Root-level OpenEnv app shim for validation and deployment tooling."""

from my_env.server.app import app as app  # re-export
from my_env.server.app import main as _main


def main(host: str = "0.0.0.0", port: int = 8000):
    """Compatibility main entrypoint expected by OpenEnv validators."""
    return _main(host=host, port=port)


if __name__ == "__main__":
    main()
