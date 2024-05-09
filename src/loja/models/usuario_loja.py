from common.models import UsuarioGenerico, UsuarioGenericoManager

from .funcionario import Funcionario, FuncionarioManager


class UsuarioLojaManager(FuncionarioManager, UsuarioGenericoManager):
    pass


class UsuarioLoja(UsuarioGenerico, Funcionario):
    usuarios = UsuarioLojaManager()
