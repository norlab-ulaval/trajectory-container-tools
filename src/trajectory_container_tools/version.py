# coding=utf-8
"""
Version information for Trajectory Container Tools (TCT).
"""

import os
import subprocess
import sys


def _get_fallback_version():
    """
    Get fallback version using alternative methods when version.txt is not available.
    
    Tries multiple approaches in order:
    1. Installed package metadata (if package is installed)
    2. Git describe (if in a git repository)
    3. Unknown version as last resort
    
    Returns fallback version string.
    """
    # Try to get version from installed package metadata
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
        else:
            import importlib_metadata as metadata
        
        return metadata.version("trajectory-container-tools")
    except (ImportError, Exception):
        pass
    
    # Try to get version from git describe
    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        git_describe = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        ).strip()
        
        # Clean up git describe output to be version-like
        if git_describe:
            return git_describe
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    
    # Last resort: unknown version
    return "unknown"


def _get_version():
    """
    Read version from version.txt file at repository root.

    Returns version string from semantic-versioning generated version.txt file.
    Falls back to alternative version detection methods if file is not found or cannot be read.
    """
    try:
        # Get the repository root (3 levels up from this file)
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        version_file = os.path.join(repo_root, "version.txt")

        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            # Use dynamic fallback instead of hardcoded version
            return _get_fallback_version()
    except (OSError, IOError, UnicodeDecodeError):
        # Use dynamic fallback instead of hardcoded version
        return _get_fallback_version()


__version__ = _get_version()
