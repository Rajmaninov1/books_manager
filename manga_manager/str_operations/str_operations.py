import re


def extract_manga_name(filename: str):
    """
    Extract the manga name from a given filename, ignoring numbers, suffixes, and other unnecessary tags.

    :param filename: The name of the file
    :return: Extracted manga name
    """
    # lower case manga name
    manga_name = filename.casefold()

    # Remove volume identifiers and special characters
    # This regex pattern covers:
    # - Numbered ranges like "01-07" or "01-10"
    # - Volume identifiers like "Tomo 01"
    # - Parentheses with numbers or characters like "(#001-007)"
    manga_name = re.sub(
        r'(tomo\s*\d+\s*-?\s*|\d+[-\s–]\d+|#?\d+[-\d]*)', '', manga_name
    )

    # Remove hashtags
    manga_name = re.sub(r'(@\w+|#\w+)', '', manga_name)

    # Remove common words not related to name
    manga_name = re.sub(
        r'(final|fin|end|last|chapter|capitulo)', '', manga_name
    )

    # Remove common suffixes like '-comprimido' or file extensions
    manga_name = re.sub(
        r'(-?comprimido|-?compressed|\.zip|\.rar|\.pdf|\.cbz|\.cbr)',
        '', manga_name, flags=re.IGNORECASE
    )

    # Remove any remaining special characters (such as "•") that could affect the name
    manga_name = re.sub(r'[•\[\]#()@]', '', manga_name)

    # Strip any trailing or leading whitespace
    manga_name = (manga_name.strip().replace('-', ' ')
                  .replace('_', ' ').title())

    return manga_name.strip()


def has_explicit_content(text: str):
    """
    Identifies explicit content in a string.

    Args:
    text: The input string.

    Returns:
    True if explicit content is found, False otherwise.
    """
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
            return True

    return False