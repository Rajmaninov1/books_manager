import os

from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Define image extensions
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')


# Function to safely retrieve and cast environment variables with default values
def get_env_var(var_name: str, default: str, cast_type: type):
    """Retrieve an environment variable, with a default value and type casting."""
    value = os.getenv(var_name, default)
    try:
        return cast_type(value)
    except ValueError as e:
        raise ValueError(f"Error converting environment variable '{var_name}' to {cast_type.__name__}: {value}") from e


# Constants for image quality checks
NOISE_THRESHOLD: int = get_env_var('NOISE_THRESHOLD', '10', int)

TEXT_THRESHOLD: int = get_env_var('TEXT_THRESHOLD', '100', int)

# Access the environment variables with fallback/default values
INPUT_MANGAS_FOLDER_PATH: str = get_env_var('INPUT_MANGAS_FOLDER_PATH', './books/pending_to_process', str)
OUTPUT_MANGAS_FOLDER_PATH: str = get_env_var('OUTPUT_MANGAS_FOLDER_PATH', './books/', str)

# Ensure these values are integers and handle any possible errors with defaults
FINAL_DOCUMENT_WIDTH: int = get_env_var('FINAL_DOCUMENT_WIDTH', '1200', int) // 2
FINAL_DOCUMENT_HEIGHT: int = get_env_var('FINAL_DOCUMENT_HEIGHT', '1600', int) // 2
IMAGE_QUALITY: int = get_env_var('IMAGE_QUALITY', '80', int)

# Control saturation filter with these variables
USE_SATURATION_FILTER: bool = (
    os.getenv('USE_SATURATION_FILTER', 'false').strip().lower() in ['true', '1', 't', 'y', 'yes']
)
SATURATION_FACTOR: float = get_env_var('SATURATION_FACTOR', '1.5', float)

# Control creating extra epub file version
CREATE_EPUB_FILE: bool = (
    os.getenv('CREATE_EPUB_FILE', 'false').strip().lower() in ['true', '1', 't', 'y', 'yes']
)

# Initialize a dictionary for file size comparison
file_size_comparison: dict[str, int] = {}

# Log loaded configuration (optional)
print(f"Loaded configuration:\n"
      f"  INPUT_MANGAS_FOLDER_PATH: {INPUT_MANGAS_FOLDER_PATH}\n"
      f"  OUTPUT_MANGAS_FOLDER_PATH: {OUTPUT_MANGAS_FOLDER_PATH}\n"
      f"  NOISE_THRESHOLD: {NOISE_THRESHOLD}\n"
      f"  FINAL_DOCUMENT_WIDTH: {FINAL_DOCUMENT_WIDTH}\n"
      f"  FINAL_DOCUMENT_HEIGHT: {FINAL_DOCUMENT_HEIGHT}\n"
      f"  IMAGE_QUALITY: {IMAGE_QUALITY}\n"
      f"  USE_SATURATION_FILTER: {USE_SATURATION_FILTER}\n"
      f"  SATURATION_FACTOR: {SATURATION_FACTOR}\n")
