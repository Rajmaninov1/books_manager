import concurrent.futures
import logging
import os

from manga_manager.manga_processor.env_vars import input_mangas_folder_path, output_mangas_folder_path
from manga_manager.manga_processor.manga_processor import process_manga

logger = logging.getLogger('_manga_manager_')


# Process files in parallel
def process_files_concurrently(
        *,
        file_paths_to_process: list[str],
        destiny_folder_path: str,
        max_workers=5
):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each file for concurrent processing
        futures = [
            executor.submit(process_manga, file_path, destiny_folder_path)
            for file_path in file_paths_to_process
        ]
        # Wait for all futures to complete and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f"File processing generated an exception: {exc}")


workers = os.cpu_count() * 2

file_paths = [
    os.path.join(input_mangas_folder_path, file)
    for file in os.listdir(input_mangas_folder_path) if
    os.path.isfile(os.path.join(input_mangas_folder_path, file))
]

process_files_concurrently(
    file_paths_to_process=file_paths,
    destiny_folder_path=output_mangas_folder_path,
    max_workers=workers  # Adjust max_workers based on your system's capability
)
