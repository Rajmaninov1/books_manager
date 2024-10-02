import concurrent.futures
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from book_manager.book_manager import process_book
from common.files_operations import compare_file_sizes, is_pdf_file, folder_contains_only_images
from common.pdf_operations import is_text_pdf
from settings import INPUT_MANGAS_FOLDER_PATH, OUTPUT_MANGAS_FOLDER_PATH, file_size_comparison
from manga_manager.manga_processor import process_manga

# Set up logger with rotating file handler
logger = logging.getLogger('_books_manager_')
# 5MB log file with 2 backups
log_handler = RotatingFileHandler('manga_manager.log', maxBytes=5 * 1024 * 1024, backupCount=2)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(log_handler)
logger.setLevel(logging.ERROR)  # Set to ERROR to minimize cron job log output


def process_files_concurrently(
        *,
        file_paths_to_process: list[str],
        destiny_folder_path: str,
        max_workers=2
):
    """
    Processes a list of files concurrently using a thread pool.

    :param file_paths_to_process: List of file paths to be processed.
    :param destiny_folder_path: Destination folder path where the processed files will be saved.
    :param max_workers: Maximum number of threads to use.
    """
    if not file_paths_to_process:
        logger.warning('No files provided for processing. Exiting.')
        return

    if not os.path.exists(destiny_folder_path):
        logger.warning(f'Destination folder does not exist: {destiny_folder_path}. Creating it.')
        os.makedirs(destiny_folder_path)

    logger.info(f'Starting concurrent processing of {len(file_paths_to_process)} files with {max_workers} workers.')

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in file_paths_to_process:
            if is_text_pdf(file_path):
                futures.append(executor.submit(process_book, file_path, destiny_folder_path))
            else:
                futures.append(executor.submit(process_manga, file_path, destiny_folder_path))

        # Wait for all futures to complete and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # Get the result of the file processing
                logger.info(f'File processed successfully: {result}')
            except Exception as exc:
                logger.error(f'File processing generated an exception: {exc}')
                logger.warning('There was an issue processing one of the files. Continuing with other files.')


start_time = datetime.now()

# Define number of workers based on CPU count
workers = os.cpu_count() // 2
if workers < 2:
    logger.warning(f'Low CPU core count detected: {workers} cores. Processing may be slower.')
else:
    logger.info(f'Detected {workers} CPU cores. Using this for max workers.')

# Ensure input and output folders are absolute paths
input_folder = os.path.abspath(INPUT_MANGAS_FOLDER_PATH)
output_folder = os.path.abspath(OUTPUT_MANGAS_FOLDER_PATH)

# List all valid file paths (PDF files and folders with images) from the input folder
if not os.path.exists(input_folder):
    logger.warning(f'Input folder does not exist: {input_folder}. Exiting.')
else:
    file_paths = [
        os.path.join(input_folder, item)
        for item in os.listdir(input_folder)
        if (folder_contains_only_images(os.path.join(input_folder, item))) or (is_pdf_file(os.path.join(input_folder, item)))
    ]

    if not file_paths:
        logger.warning(f'No valid PDFs or folders with images found in the input folder: {input_folder}. Exiting.')
    else:
        logger.info(
            f'Found {len(file_paths)} valid items (PDFs or folders with images) in the input folder: {input_folder}')

        try:
            process_files_concurrently(
                file_paths_to_process=file_paths,
                destiny_folder_path=output_folder,
                max_workers=workers
            )
            logger.info('All files processed successfully.')
        except Exception as e:
            logger.error(f'An error occurred during concurrent file processing: {e}')

# Calculate and log execution time
time_of_execution = datetime.now() - start_time
logger.info(f'Execution time: {time_of_execution}')

# Print and log file size comparisons
size_comparison = compare_file_sizes(file_size_comparison)
print('Files sizes comparison per series')
print(size_comparison)
logger.info(f'File sizes comparison: {size_comparison}')
