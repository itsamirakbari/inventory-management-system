MIN_PASSWORD_LENGTH = 8


def is_valid_password(password):
    if not isinstance(password, str):
        return False

    has_minimum_length = len(password) >= MIN_PASSWORD_LENGTH
    has_letter = any(character.isalpha() for character in password)
    has_number = any(character.isdigit() for character in password)

    return has_minimum_length and has_letter and has_number