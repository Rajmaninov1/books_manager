import logging
import fitz  # PyMuPDF

from settings import TEXT_THRESHOLD

logger = logging.getLogger('_books_manager_')


def is_text_pdf(pdf_path: str, text_threshold: int = TEXT_THRESHOLD) -> bool:
    """
    Determine if the PDF contains enough text to be considered a book.

    :param pdf_path: Path to the PDF file.
    :param text_threshold: Minimum amount of text (characters) required on a page to consider it a text PDF.
    :return: True if the PDF has enough text, False otherwise.
    """
    try:
        with fitz.open(pdf_path) as doc:
            # Count pages that meet the text threshold
            sufficient_text_pages = 0

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")

                # Count the number of characters in the text
                char_count = len(text.strip())

                # Check if the character count meets the threshold
                if char_count >= text_threshold:
                    sufficient_text_pages += 1

                # If at least one page meets the threshold, we can conclude it's a book
                if sufficient_text_pages > 0:
                    return True

            # If no pages meet the threshold, return False
            return False
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        return False
