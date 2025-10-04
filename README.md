# GeoFrame
GeoFrame is a tool for generating high-quality map images based on coordinates, allowing users to customize styles such as black-and-white road maps or colorful street views. It supports multiple mapping sources like OpenStreetMap and Mapbox, making it easy to create and save map snapshots in various formats.

## OpenStreetMap

### Landuse Tags

https://wiki.openstreetmap.org/wiki/Key:landuse

### Natural Tags

https://wiki.openstreetmap.org/wiki/Key:natural

### Requirements

pip freeze > requirements.txt

pip uninstall -r requirements.txt -y

## Execution

### Windows

To use the venv under Windwos OS, use the .\venv\Scripts\activate.bat command in the PowerShell.

## Error

### PermissionError: [Errno 13] Permission denied: 'resources/osmconvert'

chmod +x resources/osmconvert