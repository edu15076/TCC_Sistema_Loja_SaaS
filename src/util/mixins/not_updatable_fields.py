class NotUpdatableFieldMixin:
    not_updatable_fields = None

    @property
    def updatable_fields(self):
        return [
            field.name
            for field in self._meta.get_fields()
            if field.name not in self.not_updatable_fields
            and not field.is_relation
            and not field.primary_key
        ]

    def save(self, *args, **kwargs):
        if self.pk is None or self.not_updatable_fields is None:
            return super().save(*args, **kwargs)

        super().save(update_fields=self.updatable_fields, *args, **kwargs)
