from django.db import models


class TrabalhoPorDia(models.Model):
    # TODO: Usar Enum com valor inteiro para isso
    dia_da_semana = models.IntegerField()  # 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
    timeslices = models.ManyToManyField('TimeSlice', related_name='dias_de_trabalho')

    def __str__(self):
        return f"Dia {self.dia_da_semana}"
