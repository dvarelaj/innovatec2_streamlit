import unicodedata
import re
import pandas as pd


def text_cleaning(text):
    """
    Clean and normalize text by removing accents, converting to lowercase,
    removing special characters, and normalizing whitespace.

    Args:
        text: Input text to clean (str or any type). If NaN/None, returns as-is.

    Returns:
        str: Cleaned text with underscores instead of spaces, or original value if NaN.

    Example:
        >>> text_cleaning("Héllo Wórld!")
        'hello_world'
        >>> text_cleaning("Médico Cirugía")
        'medico_cirugia'
    """
    if pd.isna(text):
        return text

    # Convert to string if necessary
    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove accents and diacritics using NFD normalization
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")

    # Alternative method for stubborn accents (NFKD + ASCII encoding)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", errors="ignore").decode("utf-8")

    # Remove special characters (keep only letters, numbers, and spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Strip leading and trailing spaces
    text = text.strip()

    # Convert spaces to underscores
    text = text.replace(" ", "_")

    return text
