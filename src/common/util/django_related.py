def restart_django(*, imprimir_versoes: bool = False):
    import os
    import sys
    import django

    # imprime dados das versões
    if imprimir_versoes:
        print(f'Python {sys.version} on {sys.platform}')
        print(f'Django {django.get_version()}')

    # define a raiz do projeto par para ser possível importar os modulos
    sys.path.append('../../src')

    # configura o ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'sistema_loja_saas.settings')
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
    django.setup()
