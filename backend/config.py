"""Configuration module for loading environment variables from .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
FIRE_CRAWL_API = os.getenv("FIRE_CRAWL_API")
CLOUDMERSIVE_VIRUS_API = os.getenv("CLOUDMERSIVE_VIRUS_API")
# Validate required API keys
if not FIRE_CRAWL_API:
    raise ValueError("FIRE_CRAWL_API is not set in .env file")

if not CLOUDMERSIVE_VIRUS_API:
    raise ValueError("CLOUDMERSIVE_VIRUS_API is not set in .env file")