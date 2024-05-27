def criar_grupos_usuarios(apps, schema_editor, grupos_usuarios: dict[str, list[str]]):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    groups = [Group(name=name) for name in grupos_usuarios.keys()]
    for group in groups:
        group.permissions.set(Permission.objects.filter(
            name__in=grupos_usuarios[group.name]))
    Group.objects.bulk_create(groups)


def deletar_grupos_usuarios(apps, schema_editor, grupos_usuarios: dict[str, list[str]]):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=grupos_usuarios
    ).delete()
