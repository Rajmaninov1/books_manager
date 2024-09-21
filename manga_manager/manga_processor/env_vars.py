import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Access the environment variables with fallback/default values
input_mangas_folder_path = os.getenv('INPUT_MANGAS_FOLDER_PATH', 'default/input/path')
output_mangas_folder_path = os.getenv('OUTPUT_MANGAS_FOLDER_PATH', 'default/output/path')
pdf_net_python_key = os.getenv('PDF_NET_PYTHON_KEY')

# Ensure these values are integers and handle any possible errors with defaults
final_document_width = int(os.getenv('FINAL_DOCUMENT_WIDTH', 1600)) // 2
final_document_height = int(os.getenv('FINAL_DOCUMENT_HEIGHT', 2400)) // 2
