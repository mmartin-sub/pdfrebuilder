import os

import fitz  # PyMuPDF

# --- Configuration ---
OUTPUT_DIR = "output"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "fitz_text_rendering_test.pdf")
FONT_DIR = "downloaded_fonts"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Font Definitions ---
# We will use the font name as the alias in the PDF
FONTS_TO_TEST = {
    "Lato-Regular": os.path.join(FONT_DIR, "Lato-Regular.ttf"),
    "Roboto-Bold": os.path.join(FONT_DIR, "Roboto-Bold.ttf"),
    "Quicksand-Regular": os.path.join(FONT_DIR, "Quicksand-VariableFont_wght.ttf"),
}

# --- PDF Creation ---
doc = None
try:
    # 1. Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    print("Created a new PDF document in memory.")

    # 2. Load custom fonts
    print("\n--- Loading Custom Fonts ---")
    for font_name, font_path in FONTS_TO_TEST.items():
        if os.path.exists(font_path):
            try:
                # Each font needs to be inserted into the page resources
                page.insert_font(fontfile=font_path, fontname=font_name)
                print(f"✅ Successfully loaded font '{font_name}' from '{font_path}'")
            except Exception as e:
                print(f"❌ ERROR: Could not load font '{font_name}'. Reason: {e}")
        else:
            print(f"⚠️ WARNING: Font file not found at '{font_path}'")

    # 3. Add text elements
    print("\n--- Inserting Text Elements ---")

    # Test Case 1: Standard font (Helvetica)
    try:
        rect1 = fitz.Rect(50, 50, 400, 80)
        page.draw_rect(rect1, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))  # Light grey background
        page.insert_textbox(
            rect1,
            "This is a test with the standard 'helv' font.",
            fontname="helv",
            fontsize=12,
            color=(0, 0, 0),  # Black
        )
        print("✅ Inserted text with 'helv'.")
    except Exception as e:
        print(f"❌ ERROR inserting text with 'helv': {e}")

    # Test Case 2: Custom Font (Lato Regular) in Blue
    try:
        rect2 = fitz.Rect(50, 100, 400, 130)
        page.draw_rect(rect2, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
        page.insert_textbox(
            rect2,
            "This is Lato-Regular in blue.",
            fontname="Lato-Regular",
            fontsize=14,
            color=(0, 0, 1),  # Blue
        )
        print("✅ Inserted text with 'Lato-Regular'.")
    except Exception as e:
        print(f"❌ ERROR inserting text with 'Lato-Regular': {e}")

    # Test Case 3: Custom Font (Roboto Bold) in Red
    try:
        rect3 = fitz.Rect(50, 150, 400, 180)
        page.draw_rect(rect3, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
        page.insert_textbox(
            rect3,
            "This is Roboto-Bold in red.",
            fontname="Roboto-Bold",
            fontsize=16,
            color=(1, 0, 0),  # Red
        )
        print("✅ Inserted text with 'Roboto-Bold'.")
    except Exception as e:
        print(f"❌ ERROR inserting text with 'Roboto-Bold': {e}")

    # Test Case 4: Custom Font (Quicksand) with a different size
    try:
        rect4 = fitz.Rect(50, 200, 400, 230)
        page.draw_rect(rect4, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
        page.insert_textbox(
            rect4,
            "This is Quicksand-Regular, size 10.",
            fontname="Quicksand-Regular",
            fontsize=10,
            color=(0.2, 0.5, 0.2),  # Dark Green
        )
        print("✅ Inserted text with 'Quicksand-Regular'.")
    except Exception as e:
        print(f"❌ ERROR inserting text with 'Quicksand-Regular': {e}")

    # 4. Save the PDF
    doc.save(OUTPUT_PDF, garbage=4, deflate=True, clean=True)
    print(f"\n✅ PDF saved successfully to '{OUTPUT_PDF}'")
except Exception as e:
    print(f"\n❌ An unexpected error occurred during PDF creation: {e}")
finally:
    if "doc" in locals() and doc:
        doc.close()
        print("Closed PDF document.")
