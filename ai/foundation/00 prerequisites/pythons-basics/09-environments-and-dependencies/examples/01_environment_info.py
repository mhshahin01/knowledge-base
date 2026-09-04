import sys


version = sys.version_info
in_virtual_environment = sys.prefix != sys.base_prefix

print(f"Python: {version.major}.{version.minor}.{version.micro}")
print(f"Virtual environment: {in_virtual_environment}")
print(f"Executable: {sys.executable}")

