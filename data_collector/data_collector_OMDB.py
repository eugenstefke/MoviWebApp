import requests
import os
from dotenv import load_dotenv


def retrieve_data(title):
    """Retrieve the movie data."""
    try:
        load_dotenv()
        api_key = os.getenv("API_KEY")

        URL = "http://www.omdbapi.com/"
        PARAMETERS = {
            "t": title,
            "apikey": api_key
        }

        get_requ = requests.get(URL, params=PARAMETERS)

        if get_requ.status_code == 200:
            movie_infos = get_requ.json()
            return movie_infos
        else:
            print(f"Data Error: Status {get_requ.status_code}")
            return {"Response": False,
                    "Error": ""}

    except Exception as e:
        print("Error, no connection to the internet")
        return {"Response": False,
                "Error": ""}