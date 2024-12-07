from datetime import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Q


__all__ = ['validate_unique_promocao']


def validate_unique_promocao(produto, promocao):
    total_dias_periodo = (
        promocao.periodo.unidades_de_tempo_por_periodo
        * promocao.periodo.numero_de_periodos
    )
    data_final_promocao = promocao.data_inicio + timedelta(days=total_dias_periodo)

    promocoes = produto.promocoes.filter(
        (
            Q(data_inicio__lte=promocao.data_inicio)
            & Q(
                data_inicio__gte=promocao.data_inicio
                - F('periodo__numero_de_periodos')
                * F('periodo__unidades_de_tempo_por_periodo')
            )
            | Q(data_inicio__gte=promocao.data_inicio)
            & Q(data_inicio__lte=data_final_promocao)
        )
        & ~Q(pk=promocao.pk)
    )

    if promocoes.exists():
        raise ValidationError(
            _(
                'O produto %(produto)s tem outra(s) promoção(ões) ativa(s) no período da promoção atual: %(promocoes)s'
            ),
            params={'produto': produto.descricao, 'promocoes': promocoes},
        )

def validate_data_atual_promocao(data):
    if data < datetime.today().date():
        raise ValidationError(
            _('A data de início não pode ser no passado.')
        )