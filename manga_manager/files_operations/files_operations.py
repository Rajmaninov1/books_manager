import os


def get_file_size(file_path: str) -> int:
    # Get file size in bytes
    return os.path.getsize(file_path)

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
