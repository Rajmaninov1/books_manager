import os

from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Define image extensions
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')

# Access the environment variables with fallback/default values
INPUT_MANGAS_FOLDER_PATH: str = os.getenv('INPUT_MANGAS_FOLDER_PATH', './books/pending_to_process')
OUTPUT_MANGAS_FOLDER_PATH: str = os.getenv('OUTPUT_MANGAS_FOLDER_PATH', './books/')

# Ensure these values are integers and handle any possible errors with defaults
FINAL_DOCUMENT_WIDTH: int = int(os.getenv('FINAL_DOCUMENT_WIDTH', 1600)) // 2
FINAL_DOCUMENT_HEIGHT: int = int(os.getenv('FINAL_DOCUMENT_HEIGHT', 2400)) // 2
IMAGE_QUALITY: int = int(os.getenv('IMAGE_QUALITY', 95))

# control saturation filter with these variables
USE_SATURATION_FILTER: bool = (
        os.getenv('USE_SATURATION_FILTER', str('false')).lower() in ['true', '1', 't', 'y', 'yes']
)
SATURATION_FACTOR: float = float(os.getenv('SATURATION_FACTOR', 1.5))  # Adjust this value for desired saturation level (1.5 for moderate boost)

file_size_comparison: dict[str, int] = dict()
