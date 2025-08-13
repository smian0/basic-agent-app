"""Patch for agno-ck metadata compatibility"""
import importlib.metadata as metadata
import sys

# Create a wrapper that redirects agno -> agno-ck for metadata
_original_version = metadata.version
_original_distribution = metadata.distribution

def patched_version(name):
    if name == "agno":
        name = "agno-ck"
    return _original_version(name)

def patched_distribution(name):
    if name == "agno":
        name = "agno-ck"
    return _original_distribution(name)

# Apply patches
metadata.version = patched_version
metadata.distribution = patched_distribution

# Also patch the importlib.metadata module directly
if 'importlib.metadata' in sys.modules:
    sys.modules['importlib.metadata'].version = patched_version
    sys.modules['importlib.metadata'].distribution = patched_distribution