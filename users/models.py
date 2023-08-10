from django.db import models

# Create your models here.
class OwnerDetails(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    county = models.CharField(max_length=100)


    def __str__(self):
        return self.name