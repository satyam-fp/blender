import os
import sys
import site
import bpy

REQUIRED_PACKAGES = ["markdown2", "sseclient", "marko", "aiohttp"]

def setup_dependencies():
    wheels_path = os.path.join(os.path.dirname(__file__), "wheels")
    if wheels_path not in sys.path:
        sys.path.append(wheels_path)

    for wheel in os.listdir(wheels_path):
        if wheel.endswith(".whl"):
            site.addsitedir(os.path.join(wheels_path, wheel))

    _verify_dependencies()

def _verify_dependencies():
    for package in REQUIRED_PACKAGES:
        try:
            module = __import__(package)
            print(f"Successfully imported {package} from {module.__file__}")
        except ImportError as e:
            print(f"Missing required dependency: {package}")
            print(f"Import error details: {str(e)}")
            bpy.ops.error.message(f"Missing required dependency: {package}")