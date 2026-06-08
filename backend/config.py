"""Configuration module for loading environment variables from .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys

CLOUDMERSIVE_VIRUS_API = os.getenv("CLOUDMERSIVE_VIRUS_API")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# Validate required API keys

if not CLOUDMERSIVE_VIRUS_API:
    raise ValueError("CLOUDMERSIVE_VIRUS_API is not set in .env file")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set in .env file")