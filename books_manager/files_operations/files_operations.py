import os

from books_manager.files_operations.env_vars import IMAGE_EXTENSIONS


def is_image_file(file):
    """Check if the file is an image."""
    return file.lower().endswith(IMAGE_EXTENSIONS)

def folder_contains_only_images(folder_path):
    """Check if a folder contains only image files."""
    if not os.path.isdir(folder_path):
        return False
    return all(is_image_file(file) for file in os.listdir(folder_path))

def is_pdf_file(file):
    """Check if the file is a PDF."""
    return os.path.isfile(file) and file.lower().endswith('.pdf')


def get_file_size(file_path: str) -> int:
    """
        Get the size of a file or folder in bytes.

        :param file_path: Path to the file or folder.
        :return: Total size in bytes.
        """
    if os.path.isfile(file_path):
        # If it's a file, return its size
        return os.path.getsize(file_path)
    elif os.path.isdir(file_path):
        # If it's a folder, sum up the sizes of all the files inside it
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(file_path):
            for filename in filenames:
                file_full_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_full_path)
        return total_size
    else:
        # If the path doesn't exist or is invalid, return 0
        return 0

def convert_bytes(size_in_bytes: int) -> str:
    """
    Convert bytes to a human-readable format (KB, MB, GB, etc.).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


def compare_file_sizes(file_size_dict: dict) -> str:
    """
    Compare original and new file sizes from a dictionary.

    Args:
    - file_size_dict: Dictionary containing file sizes in the format:
      {
          "manga_name_original": size_in_bytes,
          "manga_name_new": size_in_bytes,
          ...
      }

    Returns:
    - A string with a human-readable comparison of file sizes and size reduction or increase.
    """
    result = []

    for key in file_size_dict:
        if key.endswith("_original"):
            manga_name = key.replace("_original", "")
            original_size = file_size_dict[key]
            new_size: int | None = file_size_dict.get(f"{manga_name}_new", None)

            if new_size is not None:
                original_size_human = convert_bytes(original_size)
                new_size_human = convert_bytes(new_size)

                # Calculate the difference and percentage change
                size_difference = original_size - new_size
                percentage_change = (size_difference / original_size) * 100

                if size_difference > 0:
                    result.append(
                        f"{manga_name}: Reduced from {original_size_human} to {new_size_human} "
                        f"({abs(size_difference)} bytes smaller, {percentage_change:.2f}% smaller)."
                    )
                elif size_difference < 0:
                    result.append(
                        f"{manga_name}: Increased from {original_size_human} to {new_size_human} "
                        f"({abs(size_difference)} bytes larger, {abs(percentage_change):.2f}% larger)."
                    )
                else:
                    result.append(
                        f"{manga_name}: No change in size, remains {original_size_human}."
                    )

    return "\n".join(result)
