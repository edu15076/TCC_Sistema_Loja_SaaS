def criar_grupos_usuarios(apps, schema_editor, grupos_usuarios: dict[str, list[str]], app: str):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    groups = [Group(name=name) for name in grupos_usuarios.keys()]
    Group.objects.bulk_create(groups)
    content_type, _ = ContentType.objects.get_or_create(app_label=app, model='paper')
    Permission.objects.bulk_create(
        [Permission(codename=permission, content_type=content_type) for group in grupos_usuarios.values() for permission in group],
        ignore_conflicts=True
    )
    for group in groups:
        group.permissions.set(
            Permission.objects.filter(codename__in=grupos_usuarios[group.name])
        )


def deletar_grupos_usuarios(apps, schema_editor, grupos_usuarios: dict[str, list[str]], app: str):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=grupos_usuarios).delete()
