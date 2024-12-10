from django.db import models


class TrabalhoPorDia(models.Model):
    dia_da_semana = models.IntegerField()  # 0 = Domingo, 1 = Segunda, ..., 6 = Sábado
    timeslices = models.ManyToManyField('TimeSlice', related_name='dias_de_trabalho', blank=True)

    def delete(self, *args, **kwargs):
        self.timeslices.clear()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Dia {self.dia_da_semana}"