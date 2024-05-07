import sys
import logging
import os
from enum import Enum

from django.apps import apps
from django.core.management.color import color_style

from sistema_loja_saas.settings import BASE_DIR


class DjangoColorsFormatter(logging.Formatter):
    """
    name: DjangoColorsFormatter
    version: 1.0
    author: Tim Valenta
    author_email: tonightslastsong@gmail.com
    description: Zero-config logging formatter that uses the built-in DJANGO_COLORS setting
    license: BSD
    keywords: django colors logging formatter DJANGO_COLORS
    url: https://github.com/tiliv/django-colors-formatter
    """

    def __init__(self, *args, **kwargs):
        if sys.version_info < (2, 7):
            logging.Formatter.__init__(self, *args, **kwargs)
        else:
            super(DjangoColorsFormatter, self).__init__(*args, **kwargs)
        self.style = self.configure_style(color_style())

    def configure_style(self, style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_INFO
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def format(self, record):
        message = logging.Formatter.format(self, record)
        if sys.version_info[0] < 3:
            if isinstance(message, unicode):
                message = message.encode("utf-8")
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)
        return colorizer(message)


class CSVFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        if sys.version_info < (2, 7):
            logging.Formatter.__init__(self, *args, **kwargs)
        else:
            super(CSVFormatter, self).__init__(*args, **kwargs)

    def formatTime(self, record, datefmt=None):
        # record.message = record.message.replace(',',' ')
        return super().formatTime(record, datefmt=datefmt)


class AppLabelFilter(logging.Filter):
    def filter(self, record):
        paths = record.pathname.replace(f"{BASE_DIR}{os.sep}", "").split(os.sep)

        if "." not in paths[0] and apps.get_containing_app_config(paths[0]) != None:
            record.app_label = apps.get_containing_app_config(paths[0]).name

        record.pathname = ""

        return True


class Loggers(Enum):
    DEBUG = "debug"
    DEBUG_VERBOSE = "debug-verbose"
    PRODUCT = "product"

    def get_logger(self) -> logging.Logger:
        """
        Cria um objeto Logger para ser usado, conforme as opções
        do arquivo settings.py

        :return: Logger
        :rtype: logging.Logger
        """

        return logging.getLogger(self.value)
