from django.db import models
from django.utils import timezone  # 🆕 Necesario para manejar timestamps


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


class Provider(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Safari(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    highlights = models.TextField(blank=True)
    subregion = models.ForeignKey(
        SubRegion,
        on_delete=models.CASCADE,
        related_name='safaris'
    )
    provider = models.ForeignKey(
        'Provider',
        on_delete=models.CASCADE,
        related_name='safaris',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class SafariImage(models.Model):
    safari = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='safaris/')

    def __str__(self):
        return f"Image for {self.safari.name}"


class Booking(models.Model):
    safari = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    date = models.DateField()
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    client_nationality = models.CharField(max_length=50)
    client_age = models.PositiveIntegerField()
    confirmed_by_provider = models.BooleanField(default=False)
    provider_response_date = models.DateTimeField(null=True, blank=True)  # 🆕 Fecha/hora de confirmación/rechazo

    def __str__(self):
        return f"{self.client_name} – {self.date}"


class SafariItineraryItem(models.Model):
    safari = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='itinerary_items'
    )
    time = models.TimeField()
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f"{self.time.strftime('%H:%M')} – {self.description}"


class HomePage(models.Model):
    hero_title = models.CharField(max_length=200)
    hero_subtitle = models.CharField(max_length=200)
    hero_image = models.ImageField(upload_to='homepage/hero/', blank=True, null=True)

    hero_video = models.FileField(
        upload_to='homepage/hero/videos/',
        blank=True,
        null=True,
        help_text="Sube un archivo de video (formato .mp4 recomendado)"
    )

    why_choose_title = models.CharField(max_length=200)

    experience_title = models.CharField(max_length=100)
    experience_description = models.TextField()

    responsible_tourism_title = models.CharField(max_length=100)
    responsible_tourism_description = models.TextField()

    expert_guides_title = models.CharField(max_length=100)
    expert_guides_description = models.TextField()

    custom_trips_title = models.CharField(max_length=100)
    custom_trips_description = models.TextField()

    destinations_title = models.CharField(max_length=200)
    destinations_image = models.ImageField(upload_to='homepage/destinations/', blank=True, null=True)

    def __str__(self):
        return "Home Page Configuration"

    class Meta:
        verbose_name = "Home Page Configuration"
        verbose_name_plural = "Home Page Configurations"
