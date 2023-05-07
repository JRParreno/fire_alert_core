from django.utils.crypto import get_random_string


def get_random_code():
    return get_random_string(
        length=5,
        allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    )
