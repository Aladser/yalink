import os

from django import template

from config.settings import APP_NAME, BASE_DIR, MEDIA_URL, STATIC_URL, PHOTO_NOT_FOUND

register = template.Library()


@register.filter()
def site_name_prefix(value):
    return f"{APP_NAME} - {value}" if value != '' else APP_NAME

@register.filter()
def custom_label(value, required_fields):
    if value in required_fields:
        return f"<label class='fw-bolder text-theme' title='обязательно для заполнения'>{value}:*</label>"
    else:
        return f"<label class='text-theme'>{value}:</label>"

@register.filter()
def full_image_path(image_file):
    if image_file != '' and os.path.isfile(BASE_DIR / MEDIA_URL.replace('/', '') / str(image_file)):
        return os.path.join(MEDIA_URL, str(image_file))
    else:
        return os.path.join(STATIC_URL, PHOTO_NOT_FOUND)
