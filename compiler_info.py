"""
SpeakCode Compiler - Core Metadata Configuration
Centralizes environment settings, language descriptors, extensions, and compiler metadata.
"""

from typing import Final

# Language branding & compiler versioning
LANGUAGE_NAME: Final[str] = "SpeakCode"
COMPILER_VERSION: Final[str] = "1.0.0"
AUTHOR: Final[str] = "Krish Vasoya"
DEPARTMENT: Final[str] = "B.Tech CSD"
PROJECT_YEAR: Final[int] = 2026

# Source settings
FILE_EXTENSION: Final[str] = ".speak"
SOURCE_ENCODING: Final[str] = "utf-8"
DEFAULT_INDENTATION: Final[str] = "    "
