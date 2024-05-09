from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin

from .pessoa import Pessoa, PessoaManager
from .escopo import EscopoContratacao
from .codigo_escopo_pair import CodigoEscopoPair


class UsuarioGenericoManager(PessoaManager, UserManager):
    def create_superuser(self, codigo, email=None, password=None, **extra_fields):
        codigo_escopo = CodigoEscopoPair.objects.get_or_create(
            codigo=codigo,
            escopo=EscopoContratacao.instance
        )[0]

        return super().create_superuser(codigo_escopo, email, password, **extra_fields)


class AbstractUsuarioGenerico(AbstractBaseUser, Pessoa, PermissionsMixin):
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, parent_link=True,
                                  primary_key=True, related_name='usuario')

    usuarios = UsuarioGenericoManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.nome_completo

    def get_short_name(self):
        """Return the short name for the user."""
        return self.primeiro_nome

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def enviar_email_para_usuario(self, subject, message, from_email=None, **kwargs):
        """Envia um email para esse usuário."""
        self.email_user(subject, message, from_email, **kwargs)


class UsuarioGenerico(AbstractUsuarioGenerico):
    pass
