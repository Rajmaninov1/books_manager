import os

def extract_book_name_from_path(pdf_path: str) -> str:
    """
    Extract the book name from a given PDF file path by formatting the file name.

    :param pdf_path: The path to the PDF file.
    :return: A formatted book name.
    """
    # Get the file name without the directory and the extension
    file_name_with_extension = os.path.basename(pdf_path)
    file_name, _ = os.path.splitext(file_name_with_extension)

    # Replace underscores and dashes with spaces
    book_name = file_name.replace('_', ' ').replace('-', ' ')

    # Capitalize each word in the book name
    book_name = book_name.title()

    return book_name
