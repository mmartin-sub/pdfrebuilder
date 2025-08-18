import logging
import os
import re

import requests

from pdfrebuilder.settings import get_config_value


def download_google_font(font_family: str, dest_dir: str | None = None) -> list[str] | None:
    """Downloads a Google Font family using the Google Fonts API."""
    if dest_dir is None:
        dest_dir_from_config = get_config_value("downloaded_fonts_dir")
        if isinstance(dest_dir_from_config, str):
            dest_dir = dest_dir_from_config
        else:
            dest_dir = "downloaded_fonts"  # Default fallback

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    # Construct the CSS API URL
    css_url = f"https://fonts.googleapis.com/css?family={font_family.replace(' ', '+')}:400,700"

    try:
        # Fix: Add timeout parameter
        response = requests.get(css_url, timeout=10)
        if response.status_code != 200:
            logging.error(f"Error: Could not fetch CSS for {font_family}")
            return None
        css_content = response.text
        # Extract font file URLs using regular expressions
        font_urls = re.findall(r"url\((https://fonts.gstatic.com/s/.*?)\)", css_content)
        if not font_urls:
            logging.warning(f"No font files found for '{font_family}' in the CSS response.")
            return None
        downloaded_files: list[str] = []
        for url in font_urls:
            filename = os.path.join(dest_dir, url.split("/")[-1])
            try:
                # Fix: Add timeout parameter
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(r.content)
                logging.info(f"Downloaded {url} to {filename}")
                downloaded_files.append(filename)
            except Exception as e:
                logging.error(f"Failed to download {url}: {e}")
        if downloaded_files:
            return downloaded_files
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to download font '{font_family}': {e}")
        return None
