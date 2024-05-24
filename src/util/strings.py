import re


class _P2S:
    _pascal_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def __call__(self, s: str) -> str:
        return self._pascal_to_snake_pattern.sub('_', s).lower()


pascal_to_snake = _P2S()
