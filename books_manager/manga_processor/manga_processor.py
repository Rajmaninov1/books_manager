import logging
import os

from files_operations.files_operations import get_file_size
from files_operations.env_vars import file_size_comparison
from pdf_operations.pdf_operations import split_crop_save_images_to_pdf
from str_operations.str_operations import (
    extract_manga_name,
    has_explicit_content
)

logger = logging.getLogger('_manga_manager_')


def process_manga(
        file_path: str, destiny_folder_path: str
) -> None:
    try:
        # Create output folder path, file name and extracts manga name from file name
        file_name_with_extension = os.path.basename(file_path)

        # Extract the manga name from the file name or folder name
        manga_name = extract_manga_name(file_name_with_extension.replace('.pdf', ''))

        # Record the original file size for comparison
        file_size_comparison[f'{manga_name} original'] = file_size_comparison.get(f'{manga_name} original', 0) + get_file_size(file_path)

        # Handle explicit content by placing it in a separate folder
        if has_explicit_content(file_name_with_extension):
            output_folder_path = os.path.join(destiny_folder_path, 'X', manga_name)
        else:
            output_folder_path = os.path.join(destiny_folder_path, manga_name)

        # Create the new PDF path (can be the same for both PDFs and images converted to PDFs)
        new_pdf_path = os.path.join(output_folder_path, file_name_with_extension)

        # Create output folders if they don't exist
        os.makedirs(output_folder_path, exist_ok=True)

        logger.info(f'Starting image extraction and processing for {file_name_with_extension}')

        # Extract, split, crop images from the PDF or folder of images, and save them as a new PDF
        split_crop_save_images_to_pdf(
            input_path=file_path,  # Can be a PDF file or a folder containing images
            new_pdf_path=new_pdf_path,
        )

        # Clean up: delete original file (PDF or folder)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            for file in os.listdir(file_path):
                os.remove(os.path.join(file_path, file))
            os.rmdir(file_path)

        # Update the new file size for comparison
        file_size_comparison[f'{manga_name} new'] = file_size_comparison.get(f'{manga_name} new', 0) + get_file_size(new_pdf_path)

        logger.info(f'Successfully processed {file_name_with_extension} and cleaned up temporary files.')

    except Exception as e:
        logger.error(f'Error processing {file_path}: {e}', exc_info=True)
