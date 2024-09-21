import concurrent.futures
import logging
import os

from manga_manager.manga_processor.env_vars import input_mangas_folder_path, output_mangas_folder_path
from manga_manager.manga_processor.manga_processor import process_manga

logger = logging.getLogger('_manga_manager_')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_files_concurrently(
        *,
        file_paths_to_process: list[str],
        destiny_folder_path: str,
        max_workers=5
):
    """
    Processes a list of files concurrently using a thread pool.

    :param file_paths_to_process: List of file paths to be processed.
    :param destiny_folder_path: Destination folder path where the processed files will be saved.
    :param max_workers: Maximum number of threads to use.
    """
    if not file_paths_to_process:
        logger.warning("No files provided for processing. Exiting.")
        return

    if not os.path.exists(destiny_folder_path):
        logger.warning(f"Destination folder does not exist: {destiny_folder_path}. Creating it.")
        os.makedirs(destiny_folder_path)

    logger.info(f"Starting concurrent processing of {len(file_paths_to_process)} files with {max_workers} workers.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_manga, file_path, destiny_folder_path)
            for file_path in file_paths_to_process
        ]

        # Wait for all futures to complete and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # Get the result of the file processing
                logger.info(f"File processed successfully: {result}")
            except Exception as exc:
                logger.error(f"File processing generated an exception: {exc}")
                logger.warning("There was an issue processing one of the files. Continuing with other files.")


workers = os.cpu_count() * 2
if workers < 2:
    logger.warning(f"Low CPU core count detected: {workers} cores. Processing may be slower.")
else:
    logger.info(f"Detected {workers} CPU cores. Using this for max workers.")

# List all file paths from the input folder
if not os.path.exists(input_mangas_folder_path):
    logger.warning(f"Input folder does not exist: {input_mangas_folder_path}. Exiting.")
else:
    file_paths = [
        os.path.join(input_mangas_folder_path, file)
        for file in os.listdir(input_mangas_folder_path)
        if os.path.isfile(os.path.join(input_mangas_folder_path, file))
    ]

    if not file_paths:
        logger.warning(f"No files found in the input folder: {input_mangas_folder_path}. Exiting.")
    else:
        logger.info(f"Found {len(file_paths)} files in the input folder: {input_mangas_folder_path}")

        try:
            process_files_concurrently(
                file_paths_to_process=file_paths,
                destiny_folder_path=output_mangas_folder_path,
                max_workers=workers  # Adjust max_workers based on system capability
            )
            logger.info("All files processed successfully.")
        except Exception as e:
            logger.error(f"An error occurred during concurrent file processing: {e}")
