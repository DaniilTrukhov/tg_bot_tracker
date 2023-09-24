import os


from dotenv import load_dotenv
from pydantic import StrictStr

load_dotenv()


class AllSettings:
    api_token: StrictStr = os.getenv("API_TOKEN", None)