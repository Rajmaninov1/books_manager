# Load variables from the .env file
import os

from dotenv import load_dotenv

load_dotenv()

# Access the variables
input_mangas_folder_path = os.getenv('INPUT_MANGAS_FOLDER_PATH')
output_mangas_folder_path = os.getenv('OUTPUT_MANGAS_FOLDER_PATH')
pdf_net_python_key = os.getenv('PDF_NET_PYTHON_KEY')
