import os

import fitz  # PyMuPDF

from pdfrebuilder.settings import get_config_value

# --- Configuration ---
OUTPUT_DIR = get_config_value("test_output_dir")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "fitz_return_value_test.pdf")
FONT_DIR = get_config_value("downloaded_fonts_dir")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_TO_TEST = {
    "name": "Lato-Regular",
    "path": os.path.join(FONT_DIR, "Lato-Regular.ttf"),
}
doc = None

try:
    # 1. Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    print("Created a new PDF document in memory.")

    # 2. Load custom font
    print("\n--- Loading Custom Font ---")
    if os.path.exists(FONT_TO_TEST["path"]):
        try:
            page.insert_font(fontfile=FONT_TO_TEST["path"], fontname=FONT_TO_TEST["name"])
            print(f"✅ Successfully loaded font '{FONT_TO_TEST['name']}'")
        except Exception as e:
            print(f"❌ ERROR: Could not load font. Reason: {e}")
    else:
        print(f"⚠️ WARNING: Font file not found at '{FONT_TO_TEST['path']}'")

    # 3. Add a text element and inspect the return value
    print("\n--- Inserting Text and Analyzing Return Value ---")
    rect = fitz.Rect(50, 100, 400, 130)
    page.draw_rect(rect, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
    text_to_insert = "Testing insert_textbox return value."
    return_value = None
    try:
        return_value = page.insert_textbox(
            rect,
            text_to_insert,
            fontname=FONT_TO_TEST["name"],
            fontsize=14,
            color=(0, 0, 1),  # Blue
        )
        print("✅ Call to page.insert_textbox completed without raising an exception.")
    except Exception as e:
        print(f"❌ ERROR: page.insert_textbox raised an exception: {e}")

    print("\n--- Analysis of Return Value ---")
    if return_value is None:
        print("✅ DIAGNOSIS: The function completed successfully without returning a value.")
        print("   The text should be inserted into the PDF.")
    else:
        print(f"Unexpected return type: {type(return_value)}")

    # 4. Save the PDF
    doc.save(OUTPUT_PDF, garbage=4, deflate=True, clean=True)
    print(f"\n✅ PDF saved successfully to '{OUTPUT_PDF}'")
except Exception as e:
    print(f"\n❌ An unexpected error occurred during PDF creation: {e}")
finally:
    if doc:
        doc.close()
        print("Closed PDF document.")
