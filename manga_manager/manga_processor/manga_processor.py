import logging
import os

from manga_manager.img_operations.images_operations import delete_images_in_folder
from manga_manager.pdf_operations.pdf_operations import (
    extract_split_crop_and_save_images_from_pdf,
    images_to_pdf,
    compress_pdf
)
from manga_manager.str_operations.str_operations import (
    extract_manga_name,
    has_explicit_content
)

logger = logging.getLogger('_manga_manager_')


def process_manga(
        file_path: str, destiny_folder_path: str
) -> None:
    try:
        logger.info(f'Starting process for file: {file_path}')

        # Create output folder path, file name and extracts manga name from file name
        file_name_with_extension = os.path.basename(file_path)
        manga_name = extract_manga_name(file_name_with_extension.replace('.pdf', ''))

        if has_explicit_content(file_name_with_extension):
            output_folder_path = os.path.join(destiny_folder_path, 'X', manga_name)
        else:
            output_folder_path = os.path.join(destiny_folder_path, manga_name)

        # Create temp path for extracted images folder
        images_folder_path = os.path.join(output_folder_path, file_name_with_extension.replace('.pdf', ''))

        logger.info(f'Creating folders for {file_name_with_extension} at {output_folder_path}')

        # Create output folders if they don't exist
        os.makedirs(output_folder_path, exist_ok=True)
        os.makedirs(images_folder_path, exist_ok=True)

        logger.info(f'Starting image extraction and processing for {file_name_with_extension}')

        # Extract, split and crop images from the PDF and save them in the output folder
        extract_split_crop_and_save_images_from_pdf(pdf_path=file_path, output_folder=images_folder_path)

        # Take images in output folder and merge them into PDF
        new_not_compressed_pdf_path = os.path.join(output_folder_path, file_name_with_extension)
        images_to_pdf(image_folder_path=images_folder_path, output_pdf_path=new_not_compressed_pdf_path)

        # Compress PDF to optimize storage
        compressed_pdf_path = os.path.join(output_folder_path, f'-{file_name_with_extension}')
        compress_pdf(input_pdf_path=new_not_compressed_pdf_path, output_pdf_path=compressed_pdf_path)

        # Delete images in output folder
        delete_images_in_folder(folder_path=images_folder_path)

        # Clean up: delete images folder and unnecessary files
        os.rmdir(images_folder_path)
        os.remove(new_not_compressed_pdf_path)
        os.remove(file_path)

        logger.info(f'Successfully processed {file_name_with_extension} and cleaned up temporary files.')

    except Exception as e:
        logger.error(f'Error processing {file_path}: {e}', exc_info=True)
