import logging
import os

import fitz
from PDFNetPython3.PDFNetPython import PDFNet, PDFDoc, Optimizer, SDFDoc
from natsort import natsorted

from manga_manager.img_operations.images_operations import (
    load_images_list_by_path, load_image_by_str_data, is_not_manga,
    split_image_by_blank_spaces, save_image_to_path, crop_image_by_blank_space
)
from manga_manager.manga_processor.env_vars import pdf_net_python_key

logger = logging.getLogger('_manga_manager_')


def extract_split_crop_and_save_images_from_pdf(pdf_path: str, output_folder: str):
    """
    Extracts images from a PDF, crops them based on blank space, and saves them.

    :param pdf_path: Path to the PDF file.
    :param output_folder: Folder where cropped images will be saved.
    """
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Loop through all the pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)

        # Loop through all the images in the page
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]

            # Load image using PIL
            image = load_image_by_str_data(image_data=image_data)

            # Check if the image is a manga
            if page_num != 0 and is_not_manga(image):
                # Split the image by blank spaces and save them
                images = split_image_by_blank_spaces(image=image)
                for split_counter, image in enumerate(images):
                    path = (f"{output_folder}/page{page_num + 1}_img{img_index + 1}"
                            f"_segment_{split_counter + 1}.png")
                    save_image_to_path(image, path)
            else:
                # Crop the image and save it
                image_cropped = crop_image_by_blank_space(image)
                path = f"{output_folder}/page{page_num + 1}_img{img_index + 1}.png"
                save_image_to_path(image_cropped, path)

    doc.close()


def images_to_pdf(image_folder_path: str, output_pdf_path: str):
    """
    Combines all images from a folder into a single PDF, with one image per page.

    :param image_folder_path: Path to the folder containing the images
    :param output_pdf_path: Path to save the output PDF
    """
    # List all image files in the folder
    image_files_paths: list[str] = [
        f for f in os.listdir(image_folder_path)
        if f.endswith(('png', 'jpg', 'jpeg', 'bmp'))
    ]
    # Human sort the image paths using natsorted and read them
    image_files_paths = natsorted(image_files_paths)
    images = load_images_list_by_path(
        image_folder_path=image_folder_path,
        image_files_paths=image_files_paths
    )

    if images:
        # Save all images as a single PDF
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        logger.info(f"PDF created successfully: {output_pdf_path}")
    else:
        logger.error("No images found to combine.")


def compress_pdf(input_pdf_path: str, output_pdf_path: str):
    """
    Compresses a PDF file and saves the result to the specified output path.

    :param input_pdf_path: Path to the input PDF file.
    :param output_pdf_path: Path to save the compressed PDF.
    :return: None
    """
    PDFNet.Initialize(pdf_net_python_key)
    doc = PDFDoc(input_pdf_path)
    doc.InitSecurityHandler()
    Optimizer.Optimize(doc)
    doc.Save(output_pdf_path, SDFDoc.e_linearized)
    doc.Close()
