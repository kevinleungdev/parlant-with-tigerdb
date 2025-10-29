import os
from pathlib import Path


####################################
# Load .env file
####################################


ENV_FILE_PATH = Path(__file__).resolve()

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(ENV_FILE_PATH / ".env"))
except ImportError:
    print("dotenv not installed, skipping...")



if os.environ.get("OPENAI_API_KEY") is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables")


####################################
# TIMESCALE DATABASE CONFIGURATION
####################################


TIMESCALE_DATABASE_URL = os.getenv("TIMESCALE_DATABASE_URL", None)
TIMESCALE_DATABASE_PASSWORD = os.getenv("TIMESCALE_DATABASE_PASSWORD", None)