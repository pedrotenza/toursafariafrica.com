from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    whatsapp_number = models.CharField(max_length=20, blank=True)

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
        Provider,
        on_delete=models.CASCADE,
        related_name='safaris',
        null=True,
        blank=True
    )
    min_people = models.PositiveIntegerField(default=1)
    max_people = models.PositiveIntegerField(default=10)

    provider_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Commission (%)",
        help_text="Commission rate (%)"
    )
    client_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )

    def clean(self):
        if self.provider_price < 0:
            raise ValidationError({"provider_price": "Provider price cannot be negative."})
        if self.commission < 0:
            raise ValidationError({"commission": "Commission cannot be negative."})
        if self.min_people > self.max_people:
            raise ValidationError({"min_people": "Min people cannot exceed max people."})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.client_price = self.provider_price * (1 + self.commission / 100)
        super().save(*args, **kwargs)

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
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    safari = models.ForeignKey(
        Safari,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    date = models.DateField()
    number_of_people = models.PositiveIntegerField(default=1)
    booking_datetime = models.DateTimeField(auto_now_add=True)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)

    confirmed_by_provider = models.BooleanField(default=False)
    provider_response_date = models.DateTimeField(null=True, blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Payment method used"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID"
    )

    def __str__(self):
        return f"{self.client_name} – {self.date}"

    def clean(self):
        if self.number_of_people < self.safari.min_people:
            raise ValidationError({
                "number_of_people": f"Minimum number of people is {self.safari.min_people}."
            })
        if self.number_of_people > self.safari.max_people:
            raise ValidationError({
                "number_of_people": f"Maximum number of people is {self.safari.max_people}."
            })
        if self.date < timezone.localdate():
            raise ValidationError({"date": "Booking date cannot be in the past."})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.safari and self.number_of_people:
            self.payment_amount = self.safari.client_price * self.number_of_people
        super().save(*args, **kwargs)

    def validate_participants(self):
        actual_participants = self.participants.count()
        if actual_participants != self.number_of_people:
            raise ValidationError(
                f"Number of participants ({actual_participants}) doesn't match booking count ({self.number_of_people})"
            )


class Participant(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    nationality = models.CharField(max_length=50)
    age = models.PositiveIntegerField()

    def clean(self):
        if self.age < 1:
            raise ValidationError({"age": "Age must be at least 1 year."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Participant ({self.nationality}, {self.age} years) for {self.booking.client_name}"


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
        verbose_name = "Itinerary Item"
        verbose_name_plural = "Itinerary Items"

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
        help_text="Upload a video file (recommended .mp4 format)"
    )
    why_choose_title = models.CharField(max_length=200)

    title_1 = models.CharField(max_length=100)
    description_1 = models.TextField()
    title_2 = models.CharField(max_length=100)
    description_2 = models.TextField()
    title_3 = models.CharField(max_length=100)
    description_3 = models.TextField()
    title_4 = models.CharField(max_length=100)
    description_4 = models.TextField()

    destinations_title = models.CharField(max_length=200, blank=True, null=True)
    destinations_image = models.ImageField(upload_to='homepage/destinations/', blank=True, null=True)

    def __str__(self):
        return "Home Page Configuration"

    class Meta:
        verbose_name = "Home Page Configuration"
        verbose_name_plural = "Home Page Configurations"
