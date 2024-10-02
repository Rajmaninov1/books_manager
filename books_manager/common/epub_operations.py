import os
import logging
import fitz  # PyMuPDF
from ebooklib import epub

# Set up logging
logger = logging.getLogger('pdf_to_epub_converter')


def convert_pdf_to_epub(pdf_path: str, epub_path: str, image_quality: int = 100):
    """
    Convert a PDF file to an EPUB file by extracting images and adding them to the EPUB.

    :param pdf_path: Path to the input PDF file.
    :param epub_path: Path to save the output EPUB file.
    :param image_quality: Quality of the images saved in the EPUB (1 to 100).
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist: {pdf_path}")
            raise FileNotFoundError(f"{pdf_path} not found.")

        logger.info(f"Starting conversion from PDF to EPUB: {pdf_path}")

        # Create an EPUB book
        book = epub.EpubBook()
        book.set_identifier('id123456')
        book.set_title('Converted EPUB')
        book.set_language('en')

        # Open the PDF
        with fitz.open(pdf_path) as doc:
            if doc.page_count == 0:
                logger.warning(f"PDF {pdf_path} has no pages.")
                return

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                images = page.get_images(full=True)

                if not images:
                    logger.warning(f"No images found on page {page_num}.")
                    continue

                logger.info(f"Found {len(images)} images on page {page_num}.")

                for img_index, img in enumerate(images):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_data = base_image["image"]
                        image_name = f'image_{page_num + 1}_{img_index + 1}.jpg'

                        # Save image to the EPUB
                        img_item = epub.EpubImage()
                        img_item.set_content(image_data)
                        img_item.set_id(image_name)
                        img_item.set_name(image_name)
                        book.add_item(img_item)

                        # Create a new chapter for each image
                        chapter = epub.EpubHtml(title=f'Page {page_num + 1}', file_name=f'chap_{page_num + 1}.xhtml',
                                                lang='en')
                        chapter.content = f'<html><body><h1>Page {page_num + 1}</h1><img src="{image_name}" /></body></html>'
                        book.add_item(chapter)
                        book.spine.append(chapter)

                    except Exception as e:
                        logger.error(f"Failed to extract image {img_index} on page {page_num}: {e}")
                        continue

        # Write the EPUB file
        epub.write_epub(epub_path, book)
        logger.info(f"Conversion completed successfully. EPUB saved at: {epub_path}")

    except Exception as e:
        logger.error(f"Error occurred during PDF to EPUB conversion: {e}")
        raise

# Example usage
# convert_pdf_to_epub('path/to/your/input.pdf', 'path/to/your/output.epub')
