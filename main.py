import base64
import json
import time
import requests
from typing import List

API_KEY = ""
SECRET_KEY = ""
BASE_URL = "https://api-key.fusionbrain.ai/"
QUOTES_API_URL = "https://quotes.to.digital/api/random"


class FusionBrainAPI:
    """API client for FusionBrain image generation service."""
    
    def __init__(self, base_url: str, api_key: str, secret_key: str):
        self.base_url = base_url
        self.headers = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline_id(self) -> str:
        """Retrieve the first available pipeline ID."""
        response = requests.get(
            f"{self.base_url}key/api/v1/pipelines",
            headers=self.headers,
            timeout=60
        )
        response.raise_for_status()
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
            files=payload
        )
        response.raise_for_status()
        return response.json()['uuid']

    def get_generation_result(self, request_id: str, 
                              max_attempts: int = 10, delay: int = 10) -> List[str]:
        """Check generation status and return results when ready."""
        for _ in range(max_attempts):
            response = requests.get(
                f"{self.base_url}key/api/v1/pipeline/status/{request_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'DONE':
                return data['result']['files']
            if data['status'] == 'FAIL':
                raise RuntimeError("Image generation failed")

            time.sleep(delay)
        
        raise TimeoutError("Image generation timed out")


def get_random_quote() -> str:
    """Fetch a random quote from quotes API with proper fallback handling."""
    try:
        response = requests.get(QUOTES_API_URL, timeout=10)
        response.raise_for_status()
        
        # Handle cases where API returns success but no quote content
        data = response.json()
        quote = data.get("quote", "").strip()
        
        # Return fallback if quote is empty
        return quote if quote else "Sun in sky"
    
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return "Sun in sky"


def save_image(image_data: str, filename: str) -> None:
    """Decode base64 image data and save to file."""
    decoded_data = base64.b64decode(image_data)
    with open(f"{filename}.jpg", "wb") as file:
        file.write(decoded_data)


def main() -> None:
    """Main execution flow."""
    # Initialize services
    image_api = FusionBrainAPI(BASE_URL, API_KEY, SECRET_KEY)
    
    try:
        # Prepare image generation
        pipeline_id = image_api.get_pipeline_id()
        quote = get_random_quote()
        
        # Generate and retrieve image
        operation_id = image_api.generate_image(quote, pipeline_id)
        images = image_api.get_generation_result(operation_id)
        
        # Save result
        save_image(images[0], quote)
        print("Image generated successfully!")
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
    except (RuntimeError, TimeoutError) as e:
        print(f"Processing error: {str(e)}")


if __name__ == '__main__':
    main()
