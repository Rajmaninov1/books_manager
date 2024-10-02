import fitz  # PyMuPDF
import logging

from settings import FINAL_DOCUMENT_WIDTH, FINAL_DOCUMENT_HEIGHT

logger = logging.getLogger('_books_manager_')


def reduce_pdf_margins(pdf_path: str, output_path: str, new_width: int = FINAL_DOCUMENT_WIDTH, new_height: int = FINAL_DOCUMENT_HEIGHT):
    """
    Removes margins from a PDF and adjusts it to fit on a 7" 4:3 screen for better reading.

    :param pdf_path: Path to the input PDF file.
    :param output_path: Path to save the modified PDF.
    :param new_width: New page width (in inches) for a 7" 4:3 format screen.
    :param new_height: New page height (in inches) for a 7" 4:3 format screen.
    """
    try:
        # Open the original PDF
        doc = fitz.open(pdf_path)
        num_pages = doc.page_count

        # Iterate through each page and crop margins
        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            rect = page.rect  # Get the rectangle dimensions of the page

            # Adjust the bounding box by trimming some of the margins (can be fine-tuned)
            # Example trimming, change as needed
            crop_margin_x = (rect.width - new_width) / 2
            crop_margin_y = (rect.height - new_height) / 2

            # Apply the crop by adjusting the rectangle
            if crop_margin_x > 0 and crop_margin_y > 0:
                new_rect = fitz.Rect(
                    rect.x0 + crop_margin_x, rect.y0 + crop_margin_y,
                    rect.x1 - crop_margin_x, rect.y1 - crop_margin_y
                )
            else:
                new_rect = rect

            # Crop the page
            page.set_cropbox(new_rect)
            page.set_media_box(new_rect)
            page.set_bleedbox(new_rect)
            page.set_trimbox(new_rect)

        # Save the modified PDF to the output path
        doc.save(output_path)
        doc.close()

        print(f"PDF processed and saved at: {output_path}")

    except Exception as e:
        print(f"Error processing the PDF: {e}")
