from django.utils.crypto import get_random_string
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


def get_random_code():
    return get_random_string(
        length=5,
        allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    )


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
# def send_push_message(token, message, extra=None):
#     Message(notification=Not)


def send_push_message_title(title, message):
    return Message(notification=Notification(title=title, body=message))
