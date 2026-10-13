import base64
import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path

from fusionbrain_api import FusionBrainAPI

API_KEY = os.environ.get("FUSIONBRAIN_API_KEY", "")
SECRET_KEY = os.environ.get("FUSIONBRAIN_SECRET_KEY", "")
BASE_URL = "https://api-key.fusionbrain.ai/"
QUOTES_API_URL = "https://quotes.to.digital/api/random"
IMAGE_PATH = Path("daily_quote.jpg")
README_PATH = Path("README.md")
README_START = "<!-- DAILY_IMAGE_START -->"
README_END = "<!-- DAILY_IMAGE_END -->"


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


def save_image(image_data: str, filename: Path) -> None:
    """Decode base64 image data and save to file."""
    decoded_data = base64.b64decode(image_data)
    with filename.open("wb") as file:
        file.write(decoded_data)


def update_readme(image_date: str, quote: str, image_generated: bool) -> None:
    """Update the daily image or quote and date in the README section."""
    content = README_PATH.read_text(encoding="utf-8")
    start = content.index(README_START) + len(README_START)
    end = content.index(README_END, start)
    if image_generated:
        display = f"\n\n![Daily quote image](daily_quote.jpg)\n\n> {quote}\n"
    else:
        quote_lines = "\n".join(f"> {line}" for line in quote.splitlines())
        display = f"\n\n{quote_lines}\n"
    section = f"{display}\nLast updated (UTC): {image_date}\n"
    README_PATH.write_text(content[:start] + section + content[end:], encoding="utf-8")


def main() -> None:
    """Main execution flow."""
    quote = get_random_quote()
    image_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not API_KEY or not SECRET_KEY:
        print("FusionBrain credentials are missing; using the quote in the README.")
        update_readme(image_date, quote, image_generated=False)
        return

    image_api = FusionBrainAPI(BASE_URL, API_KEY, SECRET_KEY)
    try:
        pipeline_id = image_api.get_pipeline_id()
        operation_id = image_api.generate_image(quote, pipeline_id)
        images = image_api.get_generation_result(operation_id)
        save_image(images[0], IMAGE_PATH)
    except (
        requests.exceptions.RequestException,
        RuntimeError,
        TimeoutError,
        IndexError,
        KeyError,
        ValueError,
    ) as error:
        print(f"FusionBrain is unavailable ({error}); using the quote in the README.")
        update_readme(image_date, quote, image_generated=False)
        return

    update_readme(image_date, quote, image_generated=True)
    print("Image generated successfully!")


if __name__ == '__main__':
    main()
