def trocar_chaves(d: dict, chave_antiga, nova_chave) -> None:
    d[nova_chave] = d[chave_antiga]
    del d[chave_antiga]
