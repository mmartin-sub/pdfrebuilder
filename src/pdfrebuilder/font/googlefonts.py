import logging
import os
import re
import time

import requests

from pdfrebuilder.settings import settings


def download_google_font(
    font_family: str, dest_dir: str | None = None, retries: int = 3, delay: int = 1
) -> list[str] | None:
    """
    Downloads a Google Font family using the Google Fonts API with retry mechanism.

    Args:
        font_family: The name of the font family to download.
        dest_dir: The destination directory to save the font files.
        retries: The number of times to retry downloading.
        delay: The delay in seconds between retries.

    Returns:
        A list of paths to the downloaded font files, or None if download fails.
    """
    if dest_dir is None:
        dest_dir = settings.font_management.downloaded_fonts_dir

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    css_url = f"https://fonts.googleapis.com/css?family={font_family.replace(' ', '+')}:400,700"
    css_content = None

    last_exception = None
    for attempt in range(retries):
        try:
            response = requests.get(css_url, timeout=10)
            response.raise_for_status()
            css_content = response.text
            break  # Success
        except requests.exceptions.RequestException as e:
            last_exception = e
            logging.debug(f"Attempt {attempt + 1}/{retries} failed to fetch CSS for {font_family}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error(
                    f"Could not fetch CSS for {font_family} after {retries} attempts.",
                    exc_info=last_exception,
                )
                return None

    if not css_content:
        return None

    font_urls = re.findall(r"url\((https://fonts.gstatic.com/s/.*?)\)", css_content)
    if not font_urls:
        logging.warning(f"No font files found for '{font_family}' in the CSS response.")
        return None

    downloaded_files: list[str] = []
    for url in font_urls:
        filename = os.path.join(dest_dir, url.split("/")[-1])
        last_exception = None
        for attempt in range(retries):
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(r.content)
                logging.info(f"Downloaded {url} to {filename}")
                downloaded_files.append(filename)
                break  # Success
            except (requests.exceptions.RequestException, OSError) as e:
                last_exception = e
                logging.debug(f"Attempt {attempt + 1}/{retries} failed to download {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logging.error(
                        f"Failed to download {url} after {retries} attempts.",
                        exc_info=last_exception,
                    )

    return downloaded_files
