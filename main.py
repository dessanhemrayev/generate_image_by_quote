import base64
import fcntl
import hashlib
import html
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import requests

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
    
    except (requests.exceptions.RequestException, json.JSONDecodeError, AttributeError, TypeError):
        return "Sun in sky"


def _write_temp_file(target: Path, content: bytes | str) -> Path:
    descriptor, filename = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
    temporary_path = Path(filename)
    try:
        if isinstance(content, bytes):
            with os.fdopen(descriptor, "wb") as file:
                file.write(content)
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
                file.write(content)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


@contextmanager
def _publication_lock():
    lock_id = hashlib.sha256(str(README_PATH.resolve()).encode("utf-8")).hexdigest()
    lock_path = Path(tempfile.gettempdir()) / f"daily-quote-{lock_id}.lock"
    with lock_path.open("a") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _render_readme(image_date: str, quote: str, image_generated: bool) -> str:
    with README_PATH.open("r", encoding="utf-8", newline="") as file:
        content = file.read()
    line_ending = "\r\n" if "\r\n" in content else "\n"
    content = content.replace("\r\n", "\n")
    start = content.index(README_START) + len(README_START)
    end = content.index(README_END, start)
    escaped_quote = html.escape(quote)
    quote_display = f"<pre>{escaped_quote}</pre>"
    if image_generated:
        display = f"\n\n![Daily quote image](daily_quote.jpg)\n\n{quote_display}\n"
    else:
        display = f"\n\n{quote_display}\n"
    section = f"{display}\nLast updated (UTC): {image_date}\n"
    updated_content = content[:start] + section + content[end:]
    return updated_content.replace("\n", line_ending)


def _replace_published_files(readme_temp: Path, image_temp: Path | None) -> None:
    targets = ((README_PATH, readme_temp), (IMAGE_PATH, image_temp))
    backups = {}
    installed = []
    try:
        for target, _ in targets:
            if target.exists():
                descriptor, backup_name = tempfile.mkstemp(
                    dir=target.parent, prefix=f".{target.name}.backup."
                )
                os.close(descriptor)
                backup = Path(backup_name)
                try:
                    os.replace(target, backup)
                except BaseException:
                    backup.unlink(missing_ok=True)
                    raise
                backups[target] = backup

        for target, staged in targets:
            if staged is not None:
                os.replace(staged, target)
                installed.append(target)
    except BaseException:
        for target in reversed(installed):
            target.unlink(missing_ok=True)
        for target, backup in backups.items():
            os.replace(backup, target)
        raise
    else:
        for backup in backups.values():
            backup.unlink(missing_ok=True)
    finally:
        readme_temp.unlink(missing_ok=True)
        if image_temp is not None:
            image_temp.unlink(missing_ok=True)


def update_readme(image_date: str, quote: str, image_data: bytes | None = None) -> None:
    """Atomically update the daily image or quote and date in the README."""
    with _publication_lock():
        readme_temp = _write_temp_file(
            README_PATH, _render_readme(image_date, quote, image_data is not None)
        )
        image_temp = None
        try:
            if image_data is not None:
                image_temp = _write_temp_file(IMAGE_PATH, image_data)
            _replace_published_files(readme_temp, image_temp)
        finally:
            readme_temp.unlink(missing_ok=True)
            if image_temp is not None:
                image_temp.unlink(missing_ok=True)


def main() -> None:
    """Main execution flow."""
    quote = get_random_quote()
    image_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not API_KEY or not SECRET_KEY:
        print("FusionBrain credentials are missing; using the quote in the README.")
        update_readme(image_date, quote)
        return

    try:
        image_api = FusionBrainAPI(BASE_URL, API_KEY, SECRET_KEY)
        pipeline_id = image_api.get_pipeline_id()
        operation_id = image_api.generate_image(quote, pipeline_id)
        images = image_api.get_generation_result(operation_id)
        image_data = base64.b64decode(images[0], validate=True)
    except (
        requests.exceptions.RequestException,
        RuntimeError,
        TimeoutError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        print(f"FusionBrain is unavailable ({error}); using the quote in the README.")
        update_readme(image_date, quote)
        return

    update_readme(image_date, quote, image_data)
    print("Image generated successfully!")


if __name__ == '__main__':
    main()
