import os

from dotenv import load_dotenv
from pydantic import StrictStr

# Load environment variables from the .env file
load_dotenv()


class AllSettings:
    """
        Class representing application settings.

        Attributes:
            api_token (StrictStr): API token loaded from environment variables.
        """
    api_token: StrictStr = os.getenv("API_TOKEN", None)
