"""Script to build and run all services via Docker Compose."""

import subprocess
import sys

PROJECT_NAME = "rag_assistant"

def main():
    """Tear down existing containers, rebuild, and bring up all services with logs streamed."""
    try:
        print(f"Using Docker Compose project: {PROJECT_NAME}")
        subprocess.run(["docker-compose", "-p", PROJECT_NAME, "down"], check=True)
        print(f"Building images and starting services for project {PROJECT_NAME}. Logs will follow below...")
        subprocess.run(["docker-compose", "-p", PROJECT_NAME, "up", "--build"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command {e.cmd} for project {PROJECT_NAME} failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: docker-compose command not found. Please ensure Docker Compose is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 