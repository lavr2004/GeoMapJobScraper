from bin.environment import docker_launch
from bin.settings import get_logger_fc

def main():
    mylogger = get_logger_fc("docker_launch_script")
    try:
        docker_launch.main()
        mylogger.info("OK - Docker container with Nominatim launched")
    except Exception as e:
        mylogger.error(f"ER - Docker container with Nominatim dont launched: {e}")

if __name__ == "__main__":
    main()