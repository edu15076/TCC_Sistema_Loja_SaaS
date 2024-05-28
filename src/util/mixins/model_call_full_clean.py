class ValidateModelMixin:
    def save(self, *args, **kwargs):
        """Chama `full_clean()`"""
        self.full_clean()
        return super().save(*args, **kwargs)
