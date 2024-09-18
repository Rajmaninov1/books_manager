import io
import logging
import os

import numpy as np
from PIL import Image, ImageChops
from PIL.ImageFile import ImageFile

logger = logging.getLogger('_manga_manager_')


def is_not_manga(image: ImageFile) -> bool:
    """
    Detect if an image is likely from a manga or a web-comic/manhwa based on its aspect ratio and color content.

    :param image: The image to be analyzed.
    :return: True of False based on the detected classification.
    """
    # Get image dimensions
    width, height = image.size
    aspect_ratio = width / height

    # Check if the image is grayscale or colored
    img_np = np.array(image)

    is_colored = True  # default value

    if len(img_np.shape) == 2:  # If the image has 2 dimensions, it's grayscale
        is_colored = False
    elif len(img_np.shape) == 3:  # If the image has 3 dimensions, it's colored
        is_colored = True
        # Further check if it's black and white (sometimes manhwa can also have b/w panels)
        if np.all(img_np[:, :, 0] == img_np[:, :, 1]) and np.all(img_np[:, :, 1] == img_np[:, :, 2]):
            is_colored = False  # If all channels are equal, it's essentially grayscale

    # Criteria to classify
    if aspect_ratio > 1.5 and is_colored:
        return True
    elif not is_colored:
        return False
    else:
        return True


def detect_blank_spaces(image: ImageFile, threshold=240) -> list[int]:
    """
    Detects horizontal blank spaces in an image by checking each row of pixels.
    A blank space is detected when all pixels in a row are above the threshold.

    :param image: PIL Image object
    :param threshold: Intensity threshold to consider a row as blank (default is 240 for light-colored spaces)
    :return: List of blank space positions (row indices)
    """
    blank_rows = []
    width, height = image.size
    grayscale_img = image.convert("L")  # Convert to grayscale

    for y in range(height):
        row = grayscale_img.crop((0, y, width, y + 1))
        if all(pixel > threshold for pixel in row.getdata()):
            blank_rows.append(y)

    return blank_rows


def crop_image_by_blank_space(image: ImageFile) -> ImageFile:
    """
    Crop an image by trimming white space.

    :param image: PIL Image object
    """
    # Convert to grayscale and invert
    grayscale_img = image.convert("L")
    inverted_img = ImageChops.invert(grayscale_img)

    # Find the bounding box of non-white areas
    bbox = inverted_img.getbbox()

    # Crop the image to the bounding box
    if bbox:
        cropped_img = image.crop(bbox)
        return cropped_img
    return image  # return original if no bbox found


def split_image_by_blank_spaces(image, threshold=240, min_gap=20) -> list[ImageFile]:
    """
    Splits an image into segments wherever horizontal blank spaces are found.

    :param image: Image to split
    :param threshold: Intensity threshold for detecting blank spaces
    :param min_gap: Minimum gap (in pixels) between segments to avoid splitting tiny spaces
    """
    blank_spaces = detect_blank_spaces(image, threshold)

    # Add the top and bottom as boundaries
    split_positions = [0] + blank_spaces + [image.height]

    cropped_images = []

    # Iterate over the split positions and create smaller images
    for i in range(1, len(split_positions)):
        if split_positions[i] - split_positions[i - 1] > min_gap:
            segment = image.crop((0, split_positions[i - 1], image.width, split_positions[i]))
            cropped_images.append(crop_image_by_blank_space(segment))
    return cropped_images


def delete_images_in_folder(folder_path, extensions=("png", "jpg", "jpeg", "bmp", "gif")) -> None:
    """
    Delete all image files in a folder. Images are detected by their file extensions.

    :param folder_path: The path of the folder to delete images from
    :param extensions: A tuple of image file extensions to delete
    """
    # List all files in the folder
    files = os.listdir(folder_path)

    # Loop over each file in the folder
    for file in files:
        file_path = os.path.join(folder_path, file)

        # Check if the file has an image extension and is a file (not a directory)
        if file.lower().endswith(extensions) and os.path.isfile(file_path):
            try:
                os.remove(file_path)  # Delete the image file
            except Exception as e:
                logger.error(f"Error deleting {file}: {e}")


def load_images_list_by_path(
        *,
        image_files_paths: list[str],
        image_folder_path: str
) -> list[Image]:
    # Open all images and convert to RGB (Pillow requires this for PDFs)
    return [Image.open(os.path.join(image_folder_path, image)).convert('RGB') for image in image_files_paths]


def load_image_by_str_data(image_data) -> ImageFile:
    return Image.open(io.BytesIO(image_data))


def save_image_to_path(image: ImageFile, path_to_save: str):
    image.save(path_to_save)
