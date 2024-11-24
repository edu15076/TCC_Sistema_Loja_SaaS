from django.db import models

class TimeSlice(models.Model):
    start = models.TimeField()  
    end = models.TimeField()  

    def __str__(self):
        return f"{self.start} - {self.end}"