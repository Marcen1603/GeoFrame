from docker_utils import start_overpass_server
import osmnx as ox

# Lokalen Server starten
start_overpass_server()

# Overpass-URL auf lokalen Server umstellen
ox.settings.overpass_endpoint = "http://localhost:12345/api/interpreter"
ox.settings.overpass_rate_limit = False