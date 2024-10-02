import logging
import os

from common.files_operations import get_file_size
from settings import file_size_comparison
from book_manager.book_pdf_operations import reduce_pdf_margins
from book_manager.book_str_operations import extract_book_name_from_path

logger = logging.getLogger('_books_manager_')


def process_book(file_path: str, destiny_folder_path: str) -> None:
    """
    Process a PDF file considered as a book.

    :param file_path: Path to the input PDF file.
    :param destiny_folder_path: Path to the output folder where the processed book will be saved.
    """
    try:
        # Create output folder path, file name, and extracts book name from the file name
        file_name_with_extension = os.path.basename(file_path)

        # Extract the book name from the file name
        book_name = extract_book_name_from_path(file_name_with_extension.replace('.pdf', ''))

        # Record the original file size for comparison
        file_size_comparison[f'{book_name} original'] = file_size_comparison.get(f'{book_name} original', 0) + get_file_size(file_path)

        # Create the output folder path
        output_folder_path = os.path.join(destiny_folder_path, book_name)

        # Create the new text PDF path
        new_pdf_path = os.path.join(output_folder_path, file_name_with_extension)

        # Create output folders if they don't exist
        os.makedirs(output_folder_path, exist_ok=True)

        logger.info(f'Starting text extraction and processing for {file_name_with_extension}')

        # Split and save the text PDF (placeholder function)
        reduce_pdf_margins(
            pdf_path=file_path,  # Input PDF file
            output_path=new_pdf_path,  # Output PDF file path
        )

        # Clean up: delete the original PDF file
        os.remove(file_path)

        # Update the new file size for comparison
        file_size_comparison[f'{book_name} new'] = file_size_comparison.get(f'{book_name} new', 0) + get_file_size(new_pdf_path)

        logger.info(f'Successfully processed {file_name_with_extension} and cleaned up temporary files.')

    except Exception as e:
        logger.error(f'Error processing {file_path}: {e}', exc_info=True)
