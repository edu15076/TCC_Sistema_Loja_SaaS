import os

from PIL import Image
from django.http import HttpResponse

__all__ = (
    'ReadImageMixin',
)


class ReadImageMixin:
    def get_img(self, path):
        with Image.open(path) as img:
            img_format = img.format.lower()
            content_type = f'image/{img_format}'

            with open(path, 'rb') as image_file:
                response = HttpResponse(image_file.read(), content_type=content_type)
                response['Content-Disposition'] = (
                    f'inline; filename={os.path.basename(path)}'
                )
                return response
