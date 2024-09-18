import os

from manga_manager.img_operations.images_operations import delete_images_in_folder
from manga_manager.pdf_operations.pdf_operations import extract_split_crop_and_save_images_from_pdf, images_to_pdf, \
    compress_pdf
from manga_manager.str_operations.str_operations import extract_manga_name, has_explicit_content


def process_manga(
        file_path: str, destiny_folder_path: str
) -> None:
    # create output folder path, file name and extracts manga name from file name
    file_name_with_extension = file_path.split('/')[-1].split('\\')[-1]
    manga_name = extract_manga_name(
        file_name_with_extension.replace('.pdf', '')
    )
    if has_explicit_content(file_name_with_extension):
        output_folder_path = f'{destiny_folder_path}/X/{manga_name}'
    else:
        output_folder_path = f'{destiny_folder_path}/{manga_name}'
    # create temp path for extracted images folder
    images_folder_path = f'{output_folder_path}/{file_name_with_extension.replace(".pdf", "")}'

    # create output folder if it doesn't exist
    os.makedirs(
        name=output_folder_path,
        exist_ok=True
    )
    # Create images folder and not compressed pdf path
    os.makedirs(
        name=images_folder_path,
        exist_ok=True
    )
    # extract, split and crop images from the pdf and save them in the output folder
    extract_split_crop_and_save_images_from_pdf(
        pdf_path=file_path,
        output_folder=images_folder_path
    )
    # take images in output folder and merge them into pdf
    new_not_compressed_pdf_path = f'{output_folder_path}/{file_name_with_extension}'
    images_to_pdf(
        image_folder_path=images_folder_path,
        output_pdf_path=new_not_compressed_pdf_path
    )
    # compress pdf to optimize storage
    compress_pdf(
        input_pdf_path=new_not_compressed_pdf_path,
        output_pdf_path=f'{output_folder_path}/-{file_name_with_extension}'
    )
    # delete images in output folder
    delete_images_in_folder(
        folder_path=images_folder_path
    )
    # delete the images folder
    os.rmdir(images_folder_path)
    # delete not compressed file
    os.remove(new_not_compressed_pdf_path)
    # delete original file
    os.remove(file_path)
