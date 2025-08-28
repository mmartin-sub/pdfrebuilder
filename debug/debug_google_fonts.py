import requests

def check_font_url(font_name):
    """Checks if a font is available on Google Fonts."""
    url = f"https://fonts.googleapis.com/css?family={font_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully fetched CSS for {font_name}")
        print(f"Response text: {response.text[:200]}...")
    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch CSS for {font_name}: {e}")

if __name__ == "__main__":
    print("--- Checking for Arial ---")
    check_font_url("Arial")
    print("\n--- Checking for Tangerine ---")
    check_font_url("Tangerine")
