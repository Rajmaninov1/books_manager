import gc
import logging
import os
from io import BytesIO

import fitz
from natsort import natsorted
from pymupdf import Document
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from img_operations.images_operations import (
    load_image_by_str_data, split_and_crop_image, load_image_by_path
)
from files_operations.env_vars import (
    FINAL_DOCUMENT_WIDTH,
    FINAL_DOCUMENT_HEIGHT,
    IMAGE_QUALITY
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


def process_pdf(pdf_path: str, new_pdf_path: str, screen_width=FINAL_DOCUMENT_WIDTH,
                screen_height=FINAL_DOCUMENT_HEIGHT, image_quality_=IMAGE_QUALITY):
    """
    Process PDF file: Extract images, split, crop and save them into a new PDF.
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


def process_image_folder(image_folder_path: str, new_pdf_path: str, screen_width=FINAL_DOCUMENT_WIDTH,
                         screen_height=FINAL_DOCUMENT_HEIGHT, image_quality_=IMAGE_QUALITY):
    """
    Process a folder of images and save them into a new PDF.
    """
    image_files = [f for f in os.listdir(image_folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]

    if not image_files:
        logger.warning(f"No images found in the folder: {image_folder_path}")
        return

    # Human sort the image paths using natsorted
    image_files = natsorted(image_files)

    c = canvas.Canvas(new_pdf_path, pagesize=(screen_width, screen_height))

    for image_file in image_files:
        image_path = os.path.join(image_folder_path, image_file)
        try:
            with load_image_by_path(image_path) as img:
                img = img.convert("RGB")

                # Split and crop the image if needed
                split_images = split_and_crop_image(img, 0, 0)
                for split_image in split_images:
                    image_buffer = BytesIO()
                    split_image.save(image_buffer, format='JPEG', optimize=True, quality=image_quality_)
                    image_buffer.seek(0)

                    image_reader = ImageReader(image_buffer)
                    c.drawImage(image_reader, x=0, y=0, width=screen_width, height=screen_height)
                    c.showPage()

                    image_buffer.close()
                    split_image.close()

            img.close()

        except Exception as e:
            logger.error(f"Error processing image {image_file}: {e}")

        gc.collect()  # Trigger garbage collection after each image

    c.save()
    logger.info(f"Image folder processed and saved to PDF: {new_pdf_path}")


def split_crop_save_images_to_pdf(input_path: str, new_pdf_path: str):
    """
    Determine if the input path is a folder (with images) or a PDF file,
    and process it accordingly.
    """
    if os.path.isdir(input_path):
        logger.info(f"Processing folder with images: {input_path}")
        process_image_folder(input_path, new_pdf_path)
    elif os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        logger.info(f"Processing PDF file: {input_path}")
        process_pdf(input_path, new_pdf_path)
    else:
        logger.error(f"Invalid input path: {input_path}. Must be a folder with images or a PDF file.")
