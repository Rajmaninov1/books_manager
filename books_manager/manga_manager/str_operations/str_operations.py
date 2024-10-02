import re
import logging

logger = logging.getLogger('_manga_manager_')


def extract_manga_name(filename: str) -> str:
    """
    Extract the manga name from a given filename, ignoring numbers, suffixes, and other unnecessary tags.

    :param filename: The name of the file
    :return: Extracted manga name
    """
    try:
        logger.info(f"Extracting manga name from filename: {filename}")

        # Lowercase the filename for uniformity
        manga_name = filename.casefold()

        # Combine patterns into a single regex for better performance
        combined_pattern = r'(\d+t|t\d+|tomo\s*\d+\s*-?\s*|\d+[-\s–]\d+|#?\d+[-\d]*|@\w+|#\w+|(final|fin|end|last|chapter|capitulo|capítulo)|-?comprimido|-?compressed|\.zip|\.rar|\.pdf|\.cbz|\.cbr|[•\[\]()@])'

        # Remove unwanted patterns
        manga_name = re.sub(combined_pattern, '', manga_name)

        # Replace - and _ with space, and remove extra spaces
        manga_name = re.sub(r'[-_]+', ' ', manga_name).strip()
        manga_name = re.sub(r'\s+', ' ', manga_name).title()

        logger.info(f"Extracted manga name: {manga_name}")
        return manga_name

    except Exception as e:
        logger.error(f"Error extracting manga name from filename '{filename}': {e}")
        raise


def has_explicit_content(text: str) -> bool:
    """
    Identifies explicit content in a string.

    Args:
    text: The input string.

    Returns:
    True if explicit content is found, False otherwise.
    """
    try:
        logger.info(f"Checking for explicit content in text: {text[:30]}...")  # Log part of the text for context

        # Define patterns for explicit content
        patterns = [
            r"(\b|[^a-zA-Z0-9])(fuck|shit|cunt|bitch|asshole|whore|bastard|slut|cock|dick|pussy|penis|vagina)(\b|[^a-zA-Z0-9])",
            r"(\b|[^a-zA-Z0-9])(sex|porn|naked|boobs|tits|breasts|ass|butt|clitoris)(\b|[^a-zA-Z0-9])",
            r"(\b|[^a-zA-Z0-9])(joder|mierda|coño|zorra|gilipollas|puta|cabrón|zorra|polla|pene|vagina)(\b|[^a-zA-Z0-9])",
            r"(\b|[^a-zA-Z0-9])(sexo|porno|desnudo|tetas|pechos|culo|trasero|clítoris)(\b|[^a-zA-Z0-9])",
            # Add more patterns as needed
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info("Explicit content detected in the text.")
                return True

        logger.info("No explicit content found in the text.")
        return False

    except Exception as e:
        logger.error(f"Error while checking for explicit content in text: {e}")
        raise
