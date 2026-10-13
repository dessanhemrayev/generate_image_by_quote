import json
import time
from typing import List
from urllib.parse import urlsplit

import requests


class FusionBrainAPI:
    """API client for FusionBrain image generation service."""

    def __init__(self, base_url: str, api_key: str, secret_key: str):
        parsed_url = urlsplit(base_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "api-key.fusionbrain.ai"
            or parsed_url.port not in (None, 443)
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.path not in ("", "/")
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError("FusionBrain base URL must use the official HTTPS API host")
        self.base_url = "https://api-key.fusionbrain.ai/"
        self.headers = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    @staticmethod
    def _check_response(response) -> None:
        if 300 <= response.status_code < 400:
            raise RuntimeError("FusionBrain API redirects are not allowed")
        response.raise_for_status()

    def get_pipeline_id(self) -> str:
        """Retrieve the first available pipeline ID."""
        response = requests.get(
            f"{self.base_url}key/api/v1/pipelines",
            headers=self.headers,
            allow_redirects=False,
            timeout=60
        )
        self._check_response(response)
        return response.json()[0]['id']

    def generate_image(self, prompt: str, pipeline_id: str,
                       num_images: int = 1, width: int = 1024, height: int = 1024) -> str:
        """Initiate image generation request and return operation UUID."""
        params = {
            "type": "GENERATE",
            "numImages": num_images,
            "width": width,
            "height": height,
            "generateParams": {"query": prompt}
        }

        payload = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }

        response = requests.post(
            f"{self.base_url}key/api/v1/pipeline/run",
            headers=self.headers,
            files=payload,
            allow_redirects=False,
            timeout=(10, 60)
        )
        self._check_response(response)
        return response.json()['uuid']

    def get_generation_result(self, request_id: str,
                              max_attempts: int = 10, delay: int = 10) -> List[str]:
        """Check generation status and return results when ready."""
        for _ in range(max_attempts):
            response = requests.get(
                f"{self.base_url}key/api/v1/pipeline/status/{request_id}",
                headers=self.headers,
                allow_redirects=False,
                timeout=(10, 30)
            )
            self._check_response(response)
            data = response.json()

            if data['status'] == 'DONE':
                return data['result']['files']
            if data['status'] == 'FAIL':
                raise RuntimeError("Image generation failed")

            time.sleep(delay)

        raise TimeoutError("Image generation timed out")