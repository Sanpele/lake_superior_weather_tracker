import logging

import requests


logger = logging.getLogger(__name__)


def get_request(url: str) -> str or None:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        logger.error(
            f"Request failed with status code {response.status_code}, error message: {response.text}"
        )
        return None
