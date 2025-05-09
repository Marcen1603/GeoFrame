import platform
import subprocess
import time
import requests
import shutil
import sys

def check_os():
    os_type = platform.system().lower()
    if os_type != "windows" and os_type != "linux":
        print("Not supported operating system! " + os_type)
        sys.exit(1)
    print("Operating System: " + os_type)


def check_dependency(command, install_hint=None):
    """Prüft, ob ein Shell-Befehl verfügbar ist."""
    if shutil.which(command) is None:
        print(f"'{command}' ist nicht installiert.")
        if install_hint:
            print(f"ℹ️ Hinweis: {install_hint}")
        return False
    print(f"'{command}' gefunden.")
    return True


def check_python_packages():
    
    try:
        import docker
    except ImportError:
        print("Python-Package: 'docker' not installed! Try to install ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "docker"])
        print("Sucessfully installed!")

    try:
        import requests
    except ImportError:
        print("Python-Package: 'requests' not installed! Try to install ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("Sucessfully installed!")


def start_overpass_server():
    check_os()
    check_python_packages()

    # Docker & Compose prüfen
    docker_ok = check_dependency(
        "docker", 
        install_hint="Installiere Docker Desktop (Windows) oder 'sudo apt install docker.io' (Linux)."
    )
    compose_ok = check_dependency(
        "docker-compose", 
        install_hint="Installiere mit 'pip install docker-compose' oder nutze Docker Desktop."
    )

    if not (docker_ok and compose_ok):
        print("Voraussetzungen nicht erfüllt. Abbruch.")
        sys.exit(1)

    # Container starten
    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd="../docker", check=True)
    except subprocess.CalledProcessError:
        print("Docker Compose konnte nicht gestartet werden.")
        sys.exit(1)

    # Overpass bereit?
    print("Starte Overpass-API und warte auf Bereitschaft...")
    for i in range(30):
        try:
            r = requests.get(
                "http://localhost:12345/api/interpreter?data=[out:json];node(52.5,13.4,52.6,13.5);out;", 
                timeout=2
            )
            if r.status_code == 200:
                print("Overpass-API ist bereit.")
                return
        except requests.RequestException:
            pass
        time.sleep(3)

    print("Overpass-API konnte nicht gestartet werden.")
    sys.exit(1)
