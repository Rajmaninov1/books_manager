import gc
import logging
import os

import fitz
from PDFNetPython3.PDFNetPython import PDFNet, PDFDoc, Optimizer, SDFDoc
from natsort import natsorted

from manga_manager.img_operations.images_operations import (
    load_image_by_str_data, process_image, load_image_by_path
)
from manga_manager.manga_processor.env_vars import pdf_net_python_key

logger = logging.getLogger('_manga_manager_')


def extract_split_crop_and_save_images_from_pdf(pdf_path: str, output_folder: str):
    """
    Extracts images from a PDF, crops them based on blank space, and saves them.

    :param pdf_path: Path to the PDF file.
    :param output_folder: Folder where cropped images will be saved.
    """
    try:
        logger.info(f"Starting image extraction from PDF: {pdf_path}")
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                images = page.get_images(full=True)
                logger.info(f"Found {len(images)} images on page {page_num}.")

                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]

                    with load_image_by_str_data(image_data=image_data) as image:
                        logger.info(f"Processing image {img_index} on page {page_num}.")
                        process_image(image, page_num, img_index, output_folder)
                        image.close()

                    gc.collect()  # Manually trigger garbage collection
        logger.info(f"Image extraction completed for PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Error occurred while extracting images from PDF: {pdf_path} - {e}")
        raise


def images_to_pdf(image_folder_path: str, output_pdf_path: str):
    """
    Combines all images from a folder into a single PDF, with one image per page.

    :param image_folder_path: Path to the folder containing the images
    :param output_pdf_path: Path to save the output PDF
    """
    try:
        logger.info(f"Combining images from folder: {image_folder_path} into a PDF.")
        image_files_paths: list[str] = [
            f for f in os.listdir(image_folder_path)
            if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))
        ]
        image_files_paths = natsorted(image_files_paths)

        if not image_files_paths:
            logger.error("No image files found in the specified folder.")
            return

        images = []
        for image_file_path in image_files_paths:
            logger.info(f"Processing image file: {image_file_path}")
            with load_image_by_path(image_folder_path=image_folder_path, image_file_path=image_file_path) as image:
                image = image.convert('RGB')
                images.append(image.copy())
                image.close()

        if images:
            images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
            logger.info(f"PDF created successfully: {output_pdf_path}")
        else:
            logger.error("No images available to combine into a PDF.")
    except Exception as e:
        logger.error(f"Error occurred while creating PDF: {output_pdf_path} - {e}")
        raise


def compress_pdf(input_pdf_path: str, output_pdf_path: str):
    """
    Compresses a PDF file and saves the result to the specified output path.

    :param input_pdf_path: Path to the input PDF file.
    :param output_pdf_path: Path to save the compressed PDF.
    :return: None
    """
    try:
        logger.info(f"Starting compression for PDF: {input_pdf_path}")
        PDFNet.Initialize(pdf_net_python_key)
        doc = PDFDoc(input_pdf_path)
        doc.InitSecurityHandler()
        Optimizer.Optimize(doc)
        doc.Save(output_pdf_path, SDFDoc.e_linearized)
        doc.Close()
        logger.info(f"Compression completed successfully for PDF: {output_pdf_path}")
    except Exception as e:
        logger.error(f"Error occurred during PDF compression: {input_pdf_path} - {e}")
        raise