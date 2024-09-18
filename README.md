# manga_manager

# Manga Processing Script

This Python script is designed to process PDF files of manga, handling tasks such as extracting images, cropping, splitting, compressing, and finally consolidating them back into a PDF. The script also includes functionality to process multiple files concurrently, optimizing both storage and processing time.

## Features

- **Image Extraction**: Extracts images from PDF files.
- **Image Cropping**: Crops images based on detected blank spaces to reduce unnecessary white space.
- **Image Splitting**: Splits images where horizontal blank spaces are detected.
- **Image Compression**: Compresses PDF files to optimize storage.
- **Concurrent Processing**: Handles multiple files in parallel to speed up the processing.
- **Explicit Content Filtering**: Moves files with explicit content to a separate folder.
- **Clean-up**: Deletes intermediate image files and folders after processing.

## Requirements

- Python 3.10
- `fitz` (PyMuPDF)
- `Pillow`
- `numpy`
- `natsort`
- `PDFNetPython3` (PDFTron SDK)

## Usage

1. **Install the necessary packages using pip**:

    ```bash
    pip install pymupdf pillow numpy natsort pdftron
    ```

2. **Prepare the Folder**: Place your manga PDFs in a folder.

3. Set the env vars or create the .env file with the folders paths and key you will use

4. **Run the Script**: Execute the script from the command line:

    ```bash
    python main.py
    ```

## Functions

- `is_not_manga(img)`: Detects if an image is likely from a manga or a webcomic based on aspect ratio and color content.
- `detect_blank_spaces(image, threshold=240)`: Detects horizontal blank spaces in an image.
- `crop_image_by_blank_space(img)`: Crops an image by trimming white space.
- `split_image_by_blank_spaces(img, page_num, img_index, output_folder, threshold=240, min_gap=20)`: Splits an image by detecting horizontal blank spaces.
- `extract_and_crop_images_from_pdf(pdf_path, output_folder)`: Extracts images from a PDF, crops them, and saves them.
- `delete_images_in_folder(folder_path, extensions=("png", "jpg", "jpeg", "bmp", "gif"))`: Deletes all image files in a specified folder.
- `compress_pdf(input_pdf, output_pdf, image_quality=75)`: Compresses a PDF file to optimize storage.
- `images_to_pdf(image_folder, output_pdf_path)`: Combines images from a folder into a single PDF.
- `extract_manga_name(filename)`: Extracts and cleans up the manga name from a file name.
- `has_explicit_content(text)`: Identifies explicit content in a string.
- `process_manga(file_path)`: Processes a single manga file by extracting images, cropping, splitting, and compressing.
- `process_files_concurrently(file_paths, max_workers=5)`: Processes multiple manga files concurrently.

## Notes

- Ensure that the `PDFNetPython3` library is correctly installed and configured with your license key set in the env var.
- The script assumes the presence of specific file extensions and folder names. Adjust these as needed for your environment.

## License

This script is provided as-is without warranty. You are free to use and modify it according to your needs.
