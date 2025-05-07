import subprocess
import sys
import time

DOCKER_CONTAINER_NAME = "nominatim"
TECHNICAL_PAUSE_AFTER_LAUNCH_SECONDS = 60

def log_ok(message):
    print(f"OK - {message}")

def log_error(message):
    print(f"ER - {message}")

def docker_is_running():
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
        log_ok("Docker is running.")
        return True
    except subprocess.CalledProcessError:
        log_error("Docker is not running. Please start Docker Desktop manually.")
        return False
    except FileNotFoundError:
        log_error("Docker is not installed or not found in PATH.")
        sys.exit(1)

def container_is_running(name):
    try:
        output = subprocess.check_output(["docker", "ps", "--filter", f"name={name}", "--filter", "status=running", "--format", "{{.Names}}"])
        if name in output.decode():
            log_ok(f"Container '{name}' is already running.")
            return True
        else:
            log_error(f"Container '{name}' is not running.")
            return False
    except subprocess.CalledProcessError:
        log_error("Failed to check running containers.")
        return False

def container_exists(name):
    try:
        output = subprocess.check_output(["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"])
        if name in output.decode():
            log_ok(f"Container '{name}' exists.")
            return True
        else:
            log_error(f"Container '{name}' does not exist.")
            return False
    except subprocess.CalledProcessError:
        log_error("Failed to check existing containers.")
        return False

def start_container(name):
    try:
        subprocess.check_call(["docker", "start", name])
        log_ok(f"Container '{name}' has been started.")
    except subprocess.CalledProcessError:
        log_error(f"Failed to start container '{name}'.")
        sys.exit(1)

# MAIN
def main():
    if not docker_is_running():
        log_ok("Waiting for Docker to start...")
        for _ in range(30):  # wait up to 60 seconds total
            time.sleep(2)
            if docker_is_running():
                break
        else:
            log_error("Docker did not start in time.")
            sys.exit(1)

    if not container_is_running(DOCKER_CONTAINER_NAME):
        if container_exists(DOCKER_CONTAINER_NAME):
            log_ok(f"Attempting to start container '{DOCKER_CONTAINER_NAME}'...")
            start_container(DOCKER_CONTAINER_NAME)
            time.sleep(5)  # Give Nominatim some time to start up
        else:
            log_error(f"Container '{DOCKER_CONTAINER_NAME}' not found. Make sure it is created.")
            sys.exit(1)

        global TECHNICAL_PAUSE_AFTER_LAUNCH_SECONDS
        while TECHNICAL_PAUSE_AFTER_LAUNCH_SECONDS > 0:
            time.sleep(1)
            log_ok(f"wait for {TECHNICAL_PAUSE_AFTER_LAUNCH_SECONDS} after launch docker container technical pause")
            TECHNICAL_PAUSE_AFTER_LAUNCH_SECONDS -= 1

    log_ok("Docker and Nominatim container are ready. Starting the parser...")
