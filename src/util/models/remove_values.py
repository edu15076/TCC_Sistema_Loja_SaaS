from django.db.models import QuerySet


def remove_values(qs: QuerySet, *fields: str) -> QuerySet:
    """Remove all columns in fields from a QuerySet."""
    all_columns = qs.query.__table__.columns.keys()
    not_removed_fields = set(all_columns) - set(fields)
    return qs.values(*not_removed_fields)
