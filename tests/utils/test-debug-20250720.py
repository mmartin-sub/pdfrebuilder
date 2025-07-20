import fitz  # PyMuPDF


def create_test_pdf():
    # Create a new PDF document
    doc = fitz.open()

    # Add a new page
    page = doc.new_page(width=595, height=842)  # A4 size

    # Define text properties
    text = "TEST TEXT TO VERIFY VISIBILITY"
    font_name = "helv"  # Use a standard font
    font_size = 12
    text_color = (0, 0, 0)  # Black color for text
    background_color = (0.9, 0.9, 0.9)  # Light gray background for visibility contrast

    # Define a rectangle area for the text
    text_rect = fitz.Rect(50, 100, 500, 300)  # x0, y0, x1, y1

    # Draw a background rectangle to ensure contrast
    page.draw_rect(text_rect, color=background_color, fill=background_color, overlay=True)

    # Insert text into the rectangle
    page.insert_textbox(
        text_rect,
        text,
        fontsize=font_size,
        fontname=font_name,
        color=text_color,
        align=fitz.TEXT_ALIGN_CENTER,
        overlay=True,
    )

    # Save the document
    output_path = "tests/output/test_text_render.pdf"
    doc.save(output_path)
    doc.close()
    print(f"Test PDF saved to {output_path}")


# Run the test function
create_test_pdf()
