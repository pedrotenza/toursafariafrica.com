from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SubRegion(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='subregions'
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.region.name} – {self.name}"

class Safari(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField()
    highlights  = models.TextField(blank=True)
    itinerary   = models.TextField(blank=True)
    subregion   = models.ForeignKey(
        SubRegion,
        on_delete=models.CASCADE,
        related_name='safaris'
    )

    def __str__(self):
        return self.name

class SafariImage(models.Model):
    safari = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image  = models.ImageField(upload_to='safaris/')

    def __str__(self):
        return f"Image for {self.safari.name}"

class Booking(models.Model):
    safari                = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    date                  = models.DateField()
    client_name           = models.CharField(max_length=100)
    client_email          = models.EmailField()
    confirmed_by_provider = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name} – {self.date}"
