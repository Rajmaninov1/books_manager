import io
import logging
import os

import numpy as np
from PIL import Image
from PIL.ImageFile import ImageFile

logger = logging.getLogger('_manga_manager_')

def is_not_manga(image: ImageFile) -> bool:
    """
    Detect if an image is likely from a manga or a web-comic/manhwa based on its aspect ratio and color content.
    """
    try:
        width, height = image.size
        aspect_ratio = width / height
        img_np = np.array(image, dtype=np.uint8)

        is_colored = True

        if len(img_np.shape) == 2:
            is_colored = False
        elif len(img_np.shape) == 3:
            if np.all(img_np[:, :, 0] == img_np[:, :, 1]) and np.all(img_np[:, :, 1] == img_np[:, :, 2]):
                is_colored = False

        if aspect_ratio > 1.5 and is_colored:
            logger.info("Image classified as manga.")
            return True
        elif not is_colored:
            logger.info("Image classified as non-manga (grayscale).")
            return False
        else:
            logger.info("Image classified as manga (non-grayscale).")
            return True
    except Exception as e:
        logger.error(f"Error in is_not_manga: {e}", exc_info=True)
        return False

def detect_blank_or_dark_spaces(image, threshold_light=240, threshold_dark=15):
    """
    Detects horizontal blank or dark spaces in an image by checking each row of pixels.
    """
    try:
        spaces = []
        width, height = image.size
        grayscale_img = image.convert("L")

        for y in range(height):
            row = grayscale_img.crop((0, y, width, y + 1))
            if all(pixel > threshold_light for pixel in row.getdata()) or all(pixel < threshold_dark for pixel in row.getdata()):
                spaces.append(y)

        logger.info(f"Detected {len(spaces)} blank or dark spaces.")
        return spaces
    except Exception as e:
        logger.error(f"Error in detect_blank_or_dark_spaces: {e}", exc_info=True)
        return []

def crop_image_by_blank_or_dark_space(image, blank_threshold=240, dark_threshold=30) -> ImageFile:
    """
    Crops the image by detecting regions of blank (white) or dark (black) space.
    """
    try:
        grayscale_image = image.convert('L')
        np_image = np.array(grayscale_image, dtype=np.uint8)

        blank_mask = np_image > blank_threshold
        dark_mask = np_image < dark_threshold
        crop_mask = ~(blank_mask | dark_mask)

        coords = np.argwhere(crop_mask)
        if coords.size > 0:
            y0, x0 = coords.min(axis=0)
            y1, x1 = coords.max(axis=0) + 1
            cropped_image = image.crop((x0, y0, x1, y1))
            logger.info("Image cropped by blank or dark spaces.")
        else:
            logger.warning("No valid cropping region found, returning original image.")
            cropped_image = image
        return cropped_image
    except Exception as e:
        logger.error(f"Error in crop_image_by_blank_or_dark_space: {e}", exc_info=True)
        return image

def enhance_image_for_screen(img, screen_width=1264, screen_height=1680) -> Image:
    """
    Enhances an image to fit a screen with given resolution pixels while maintaining the aspect ratio.
    """
    try:
        img_width, img_height = img.size
        img_aspect_ratio = img_width / img_height
        screen_aspect_ratio = screen_width / screen_height

        if img_aspect_ratio > screen_aspect_ratio:
            new_width = screen_width
            new_height = int(screen_width / img_aspect_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * img_aspect_ratio)

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", (screen_width, screen_height), (255, 255, 255))
        paste_x = (screen_width - new_width) // 2
        paste_y = (screen_height - new_height) // 2

        new_img.paste(resized_img, (paste_x, paste_y))
        logger.info("Image enhanced for screen.")
        return new_img
    except Exception as e:
        logger.error(f"Error in enhance_image_for_screen: {e}", exc_info=True)
        return img

def split_image_by_blank_or_dark_spaces(image, threshold_light=240, threshold_dark=15, min_gap=20) -> list[ImageFile]:
    """
    Splits an image into segments wherever horizontal blank spaces are found.
    """
    try:
        blank_spaces = detect_blank_or_dark_spaces(image, threshold_light, threshold_dark)
        split_positions = [0] + blank_spaces + [image.height]

        cropped_images = []

        for i in range(1, len(split_positions)):
            if split_positions[i] - split_positions[i - 1] > min_gap:
                segment = image.crop((0, split_positions[i - 1], image.width, split_positions[i]))
                segment_cropped = crop_image_by_blank_or_dark_space(segment)
                segment_enhanced = enhance_image_for_screen(segment_cropped)
                cropped_images.append(segment_enhanced)

        logger.info(f"Split image into {len(cropped_images)} segments.")
        return cropped_images
    except Exception as e:
        logger.error(f"Error in split_image_by_blank_or_dark_spaces: {e}", exc_info=True)
        return []

def process_image(image: ImageFile, page_num: int, img_index: int, output_folder: str) -> None:
    try:
        logger.info(f"Processing image from page {page_num + 1}, index {img_index + 1}.")
        if page_num != 0 and is_not_manga(image):
            for split_counter, image_segment in enumerate(split_image_by_blank_or_dark_spaces(image=image)):
                path = f"{output_folder}/page{page_num + 1}_img{img_index + 1}_segment_{split_counter + 1}.jpeg"
                save_image_to_path(image_segment, path)
                image_segment.close()
        else:
            image_cropped = enhance_image_for_screen(crop_image_by_blank_or_dark_space(image))
            path = f"{output_folder}/page{page_num + 1}_img{img_index + 1}.jpeg"
            save_image_to_path(image_cropped, path)
    except Exception as e:
        logger.error(f"Error processing image on page {page_num + 1}: {e}", exc_info=True)

def delete_images_in_folder(folder_path, extensions=("png", "jpg", "jpeg", "bmp", "gif")) -> None:
    """
    Delete all image files in a folder. Images are detected by their file extensions.
    """
    try:
        files = os.listdir(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)

            if file.lower().endswith(extensions) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Deleted image: {file}")
    except Exception as e:
        logger.error(f"Error deleting images in folder {folder_path}: {e}", exc_info=True)

def load_images_list_by_path(
        *,
        image_files_paths: list[str],
        image_folder_path: str
) -> list[Image]:
    """
    Load images from a list of paths.
    """
    images = []
    try:
        for image_path in image_files_paths:
            full_path = os.path.join(image_folder_path, image_path)
            images.append(Image.open(full_path).convert('RGB'))
            logger.info(f"Loaded image: {image_path}")
    except Exception as e:
        logger.error(f"Error loading images from path {image_folder_path}: {e}", exc_info=True)
    return images

def load_image_by_path(
        *,
        image_file_path: str,
        image_folder_path: str
) -> Image:
    """
    Load a single image by its path.
    """
    try:
        full_path = os.path.join(image_folder_path, image_file_path)
        image = Image.open(full_path).convert('RGB')
        logger.info(f"Loaded image: {image_file_path}")
        return image
    except Exception as e:
        logger.error(f"Error loading image {image_file_path}: {e}", exc_info=True)
        return None

def load_image_by_str_data(image_data) -> ImageFile | None:
    """
    Load an image from byte data.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        logger.info("Loaded image from byte data.")
        return image
    except Exception as e:
        logger.error(f"Error loading image from byte data: {e}", exc_info=True)
        return None

def save_image_to_path(image: ImageFile, path_to_save: str, quality=75):
    """
    Save an image to a specified path with a given quality.
    """
    try:
        image.save(path_to_save, format='JPEG', quality=quality)
        logger.info(f"Saved image to {path_to_save}.")
    except Exception as e:
        logger.error(f"Error saving image to {path_to_save}: {e}", exc_info=True)
