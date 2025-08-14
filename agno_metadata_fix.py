"""Fix for agno-ck metadata compatibility"""
import importlib.metadata as metadata
import sys

# Store original functions
_original_distribution = metadata.distribution
_original_version = metadata.version

def patched_distribution(name):
    if name == "agno":
        name = "agno-ck"
    return _original_distribution(name)

def patched_version(name):
    if name == "agno":
        name = "agno-ck"
    return _original_version(name)

# Apply patches
metadata.distribution = patched_distribution
metadata.version = patched_version

# Also patch the importlib.metadata module directly
if 'importlib.metadata' in sys.modules:
    sys.modules['importlib.metadata'].version = patched_version
    sys.modules['importlib.metadata'].distribution = patched_distribution