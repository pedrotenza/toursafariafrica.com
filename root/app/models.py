from django.db import models

class Safari(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='safaris/')

    def __str__(self):
        return self.name

class Booking(models.Model):
    safari = models.ForeignKey(Safari, on_delete=models.CASCADE)
    date = models.DateField()
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    confirmed_by_provider = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name} - {self.date}"
