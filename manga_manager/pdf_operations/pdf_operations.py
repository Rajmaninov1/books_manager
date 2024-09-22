import gc
import logging
import os
from io import BytesIO

import fitz
from pymupdf import Document
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from manga_manager.img_operations.images_operations import (
    load_image_by_str_data, split_and_crop_image
)
from manga_manager.manga_processor.env_vars import (
    final_document_width,
    final_document_height,
    image_quality
)

logger = logging.getLogger('_manga_manager_')


def doc_pages_generator(doc: Document):
    """Generator to extract and yield images from the PDF."""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)

        if not images:
            logger.warning(f"No images found on page {page_num}.")
        else:
            logger.info(f"Found {len(images)} images on page {page_num}.")

        for img_index, img in enumerate(images):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                yield page_num, img_index, image_data
            except Exception as e:
                logger.error(f"Failed to extract image {img_index} on page {page_num}: {e}")
                continue


def split_crop_save_images_to_pdf(
        pdf_path: str,
        new_pdf_path: str,
        screen_width=final_document_width,
        screen_height=final_document_height,
        image_quality_=image_quality
):
    """
    Extracts images from a PDF, crops them based on blank or dark space, and saves them.
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist: {pdf_path}")
            raise FileNotFoundError(f"{pdf_path} not found.")

        logger.info(f"Starting image extraction from PDF: {pdf_path}")
        with fitz.open(pdf_path) as doc:
            if doc.page_count == 0:
                logger.warning(f"PDF {pdf_path} has no pages.")
                return

            c = canvas.Canvas(new_pdf_path, pagesize=(screen_width, screen_height))

            for page_num, img_index, image_data in doc_pages_generator(doc):
                logger.info(f"Processing image {img_index} on page {page_num}.")
                try:
                    with load_image_by_str_data(image_data=image_data) as image:
                        split_images = split_and_crop_image(image, page_num, img_index)
                        for split_image in split_images:
                            # Create an in-memory bytes object
                            image_buffer = BytesIO()
                            # Save the PIL image to buffer in JPEG format (or appropriate format)
                            split_image.save(image_buffer, format='JPEG', optimize=True, quality=image_quality_)
                            image_buffer.seek(0)  # Seek to the start of the BytesIO object

                            # Convert the BytesIO object to an ImageReader object that ReportLab can understand
                            image_reader = ImageReader(image_buffer)

                            # Draw the image on the PDF at position (x, y) with specified width and height
                            c.drawImage(image_reader, x=0, y=0, width=screen_width, height=screen_height)

                            # Start a new page after each image
                            c.showPage()

                            # Close the image buffer
                            image_buffer.close()

                            # Close the split image
                            split_image.close()

                        image.close()
                except Exception as e:
                    logger.error(f"Error processing image {img_index} on page {page_num}: {e}")

                # Trigger garbage collection after processing each image to free up memory
                gc.collect()

            # Save the PDF
            c.save()

        logger.info(f"Image extraction completed for PDF: {pdf_path}")

    except Exception as e:
        logger.error(f"Error occurred while extracting images from PDF: {pdf_path} - {e}")
        raise
