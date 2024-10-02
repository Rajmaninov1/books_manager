# Books Manager

## Overview
Manga Manager is a Python-based application designed for efficient management and processing of manga files. It allows users to extract images from PDF manga, convert folders of images into PDF format, and optimize these files for e-readers. The application features concurrent processing, logging, and memory optimization to handle multiple files effectively.

## Features
- **PDF Processing**: Extracts and processes images from PDF manga files.
- **Image Folder Support**: Converts folders containing images into a single PDF file.
- **Memory Optimization**: Efficiently manages memory usage during image processing.
- **Explicit Content Handling**: Organizes output files based on the content type (explicit or not).
- **Image Quality Control**: Allows users to specify image quality settings for output PDFs.
- **Logging**: Provides detailed logging for tracking progress and errors during processing.

## Installation

1. Clone the repository:
   ~~~bash
   git clone https://github.com/yourusername/manga_manager.git
   ~~~
   
2. Navigate to the project directory:

   ~~~bash
   cd manga_manager
   ~~~
3. Install the required dependencies:
   ~~~bash
   pip install -r requirements.txt
   ~~~
   
## Usage
   Processing a PDF or Folder of Images. You can process either a PDF file or a folder containing images. The output will be saved in a specified destination folder.

## File Structure
~~~
manga_manager/
│
├── files_operations/
│   ├── env_vars.py            # Environment variables and configurations
│   ├── files_operations.py     # Functions for file handling and size comparison
│
├── img_operations/
│   ├── images_operations.py     # Functions for image processing
│
├── pdf_operations/
│   ├── pdf_operations.py        # Functions for PDF manipulation
│
├── manga_processor/
│   ├── manga_processor.py       # Contains the main process to manga processing
│
├── str_operations/
│   ├── str_operations.py        # Functions for string manipulation
│
├── main.py                      # Main script to run the application
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
~~~

## Dependencies
- Python 3.x
- PyMuPDF
- ReportLab
- Natsort
- Other necessary libraries specified in requirements.txt

## Contributing
> Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

## License
This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3. See the LICENSE file for more information.

## Author
Julian Felipe Tolosa Villamizar

## Acknowledgements
> Thanks to the open-source community for the libraries used in this project.
> And feel free to adjust any section to better fit your project specifics!