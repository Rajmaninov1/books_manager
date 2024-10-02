import io
import logging
import os

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from PIL.ImageFile import ImageFile

from settings import FINAL_DOCUMENT_WIDTH, FINAL_DOCUMENT_HEIGHT, USE_SATURATION_FILTER, \
    SATURATION_FACTOR, NOISE_THRESHOLD

logger = logging.getLogger('_books_manager_')


def average_brightness(region: Image.Image) -> float:
    """
    Computes the average brightness of an image region.

    Brightness is computed as the mean of the grayscale values.
    """
    grayscale = region.convert("L")
    histogram = grayscale.histogram()
    pixels = sum(histogram)
    brightness = sum(i * histogram[i] for i in range(256)) / pixels
    return brightness


def best_background_for_image(image: Image.Image, corner_size: int = 50) -> tuple[int, int, int]:
    """
    Determines whether an image looks better on a black or white background based on the brightness
    of the corners.

    Args:
    - image: The input image.
    - corner_size: The size of the square region to extract from each corner.

    Returns:
    - (0, 0, 0) for black background.
    - (255, 255, 255) for white background.
    """
    width, height = image.size

    # Define the four corner boxes (left-top, right-top, left-bottom, right-bottom)
    corners = [
        image.crop((0, 0, corner_size, corner_size)),  # Top-left
        image.crop((width - corner_size, 0, width, corner_size)),  # Top-right
        image.crop((0, height - corner_size, corner_size, height)),  # Bottom-left
        image.crop((width - corner_size, height - corner_size, width, height))  # Bottom-right
    ]

    # Calculate average brightness for each corner and then average the results
    avg_brightness = sum(average_brightness(corner) for corner in corners) / len(corners)

    # Calculate contrast with white and black backgrounds
    contrast_with_white = abs(255 - avg_brightness)  # White background contrast
    contrast_with_black = avg_brightness  # Black background contrast

    # Choose the background that provides better contrast
    if contrast_with_white > contrast_with_black:
        return 0, 0, 0  # Image looks better on a black background
    else:
        return 255, 255, 255  # Image looks better on a white background


def calculate_noise(image_cv: np.ndarray) -> float:
    """
    Calculate the noise level of the image using variance of the Laplacian.
    """
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var


def is_image_good_quality(image: Image) -> bool:
    """
    Determine if the image quality is good based on noise level and sharpness.
    """
    image_cv = np.array(image)
    noise_level = calculate_noise(image_cv)

    logger.debug(f'Noise level: {noise_level}')

    # Check if the noise level is below the threshold
    return noise_level < NOISE_THRESHOLD


def denoise_and_sharpen_image(
        image: Image,
        use_saturation_filter: bool = USE_SATURATION_FILTER,
        saturation_factor: float = SATURATION_FACTOR
) -> Image:
    """
    Denoises and sharpens an image after cropping.

    Parameters:
    - image: The cropped image as a PIL Image.
    - use_saturation_filter: Whether to apply saturation enhancement.
    - saturation_factor: The factor by which to enhance saturation.
    """
    try:
        image_saturated = image
        if use_saturation_filter:
            # Enhance saturation (specific to color e-readers like Kobo Libra Colour)
            enhancer = ImageEnhance.Color(image_saturated)
            image_saturated = enhancer.enhance(saturation_factor)

        # Check if the image is of good quality
        if is_image_good_quality(image_saturated):
            logger.info('Image quality is good; skipping denoising.')
            return image_saturated

        # 1. Denoise the image using OpenCV (fastNlMeansDenoisingColored)
        image_cv = np.array(image_saturated)
        denoised_image = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)

        # Convert back to PIL for further processing
        image_denoised = Image.fromarray(denoised_image)

        # 2. Sharpen the image using Pillow's built-in filter
        image_sharpened = image_denoised.filter(ImageFilter.SHARPEN)

        logger.info('Image denoised and sharpened.')
        return image_sharpened
    except Exception as e:
        logger.error(f'Error in denoise_and_sharpen_image: {e}', exc_info=True)
        return image


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
            if all(pixel > threshold_light for pixel in row.getdata()) or all(
                    pixel < threshold_dark for pixel in row.getdata()):
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


def enhance_image_for_screen(img, screen_width=FINAL_DOCUMENT_WIDTH, screen_height=FINAL_DOCUMENT_HEIGHT) -> Image:
    """
    Enhances an image to fit a screen with given resolution pixels while maintaining the aspect ratio.
    """
    try:
        img_width, img_height = img.size

        # Ensure the image dimensions are valid
        if img_width <= 0 or img_height <= 0:
            raise ValueError(f"Invalid image dimensions: width={img_width}, height={img_height}")

        # Ensure the screen dimensions are valid
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError(f"Invalid screen dimensions: width={screen_width}, height={screen_height}")

        img_aspect_ratio = img_width / img_height
        screen_aspect_ratio = screen_width / screen_height

        # Maintain aspect ratio
        if img_aspect_ratio > screen_aspect_ratio:
            new_width = screen_width
            new_height = max(1, int(screen_width / img_aspect_ratio))  # Avoid zero/negative height
        else:
            new_height = screen_height
            new_width = max(1, int(screen_height * img_aspect_ratio))  # Avoid zero/negative width

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create a new image with the screen size and background color matching the best background for the image
        new_img = Image.new(
            mode="RGB", size=(screen_width, screen_height), color=best_background_for_image(resized_img)
        )

        # Center the resized image on the screen
        paste_x = (screen_width - new_width) // 2
        paste_y = (screen_height - new_height) // 2
        new_img.paste(resized_img, (paste_x, paste_y))

        logger.info("Image enhanced for screen.")
        return new_img

    except Exception as e:
        logger.error(f"Error in enhance_image_for_screen: {e}", exc_info=True)
        return img


def split_image_by_blank_or_dark_spaces(
        image,
        threshold_light=240,
        threshold_dark=15,
        min_gap=20
) -> list[ImageFile]:
    """
    Splits an image into segments wherever horizontal blank spaces are found
    """
    try:
        blank_spaces = detect_blank_or_dark_spaces(image, threshold_light, threshold_dark)
        split_positions = [0] + blank_spaces + [image.height]

        cropped_images = []

        for i in range(1, len(split_positions)):
            try:
                if split_positions[i] - split_positions[i - 1] > min_gap:
                    segment = image.crop((0, split_positions[i - 1], image.width, split_positions[i]))

                    segment_cropped = crop_image_by_blank_or_dark_space(segment)
                    segment_enhanced = enhance_image_for_screen(segment_cropped)
                    cropped_images.append(segment_enhanced)
            except IndexError:
                break

        logger.info(f"Split image into {len(cropped_images)} segments.")
        return cropped_images
    except Exception as e:
        logger.error(f"Error in split_image_by_blank_or_dark_spaces: {e}", exc_info=True)
        return []


def split_and_crop_image(image: ImageFile, page_num: int, img_index: int) -> list[ImageFile]:
    images: list[ImageFile] = []
    try:
        logger.info(f"Processing image from page {page_num + 1}, index {img_index + 1}.")
        if page_num != 0 and is_not_manga(image):
            for image_segment in split_image_by_blank_or_dark_spaces(image=image):
                # Apply denoising and sharpening after cropping
                denoised_sharpened_image = denoise_and_sharpen_image(image_segment)
                images.append(denoised_sharpened_image)
        else:
            image_cropped = enhance_image_for_screen(crop_image_by_blank_or_dark_space(image))
            # Apply denoising and sharpening after cropping
            denoised_sharpened_image = denoise_and_sharpen_image(image_cropped)
            images.append(denoised_sharpened_image)
    except Exception as e:
        logger.error(f"Error processing image on page {page_num + 1}: {e}", exc_info=True)
    return images


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


def temporal_pdf_image(image_path: str, width: int, height: int) -> str:
    with Image.open(image_path) as img:
        image_path = image_path.split('.')[0]
        img = img.convert('RGB')  # Ensure it's in RGB format

        # Resize the image to fit A4 size while maintaining aspect ratio
        img_width, img_height = img.size
        aspect = img_width / img_height

        if aspect > 1:  # Wide image
            new_width = width
            new_height = width / aspect
        else:  # Tall image
            new_height = height
            new_width = height * aspect

        img = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)

        # Save the image to a temporary file and draw on canvas
        temp_img_path = f"{image_path}.pdf"
        img.save(temp_img_path, "PDF", quality=85)

        return temp_img_path


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
        image_file_path: str,
) -> Image:
    """
    Load a single image by its path.
    """
    try:
        image = Image.open(image_file_path).convert('RGB')
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
