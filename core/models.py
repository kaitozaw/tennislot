from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class OrganiserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class Organiser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    stripe_user_id = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrganiserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class BookingPage(models.Model):
    organiser = models.ForeignKey("Organiser", on_delete=models.CASCADE, related_name="booking_pages")
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    public_url = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_public_url(self):
        return f"/book/{self.public_url}/"

    def __str__(self):
        return f"{self.name} {self.location}"

class Court(models.Model):
    booking_page = models.ForeignKey("BookingPage", on_delete=models.CASCADE, related_name="courts")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_page', 'name']
        constraints = [models.UniqueConstraint(fields=['booking_page', 'name'], name='unique_booking_page_court_name')]

    def __str__(self):
        return f"{self.name} (Page: {self.booking_page.name})"

class SlotDefinition(models.Model):
    SLOT_CHOICES = [
        (30, "30 minutes"),
        (60, "60 minutes"),
    ]

    booking_page = models.OneToOneField("BookingPage", on_delete=models.CASCADE, related_name="slot_definition")
    slot_size = models.PositiveIntegerField(choices=SLOT_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_page', 'slot_size']
        constraints = [models.UniqueConstraint(fields=['booking_page'], name='unique_booking_page')]

    def __str__(self):
        return f"{self.get_slot_size_display()} ${self.price:.2f} (Page: {self.booking_page.name})"

class EquipmentOption(models.Model):
    booking_page = models.ForeignKey("BookingPage", on_delete=models.CASCADE, related_name="equipment_options")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_page', 'name']
        constraints = [models.UniqueConstraint(fields=['booking_page', 'name'], name='unique_booking_page_equipment_option_name')]

    def __str__(self):
        return f"{self.name} ${self.price:.2f} (Page: {self.booking_page.name})"

class OpeningHourRule(models.Model):
    WEEKDAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    booking_page = models.ForeignKey("BookingPage", on_delete=models.CASCADE, related_name="opening_hour_rules")
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_page', 'weekday']
        constraints = [models.UniqueConstraint(fields=['booking_page', 'weekday'], name='unique_booking_page_weekday')]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time} (Page: {self.booking_page.name})"

class HolidayException(models.Model):
    booking_page = models.ForeignKey("BookingPage", on_delete=models.CASCADE, related_name="holiday_exceptions")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking_page', 'date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} (Page: {self.booking_page.name})"

class SpecialException(models.Model):
    court = models.ForeignKey("Court", on_delete=models.CASCADE, related_name="special_exceptions")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['court', 'date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} (Court: {self.court.name} / Page: {self.court.booking_page.name})"

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ]

    court = models.ForeignKey("Court", on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    player_email = models.EmailField()
    player_phone = models.CharField(max_length=30)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'start_time']
        indexes = [models.Index(fields=["court", "date"]),]

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} (Court: {self.court.name} / Page: {self.court.booking_page.name})"

class BookingEquipmentOption(models.Model):
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="booking_equipment_options")
    equipment_option = models.ForeignKey("EquipmentOption", on_delete=models.CASCADE, related_name="booking_equipment_options")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['booking', 'equipment_option']
        constraints = [models.UniqueConstraint(fields=['booking', 'equipment_option'], name='unique_booking_equipment_option')]

    def __str__(self):
        return f"{self.quantity} * {self.equipment_option.name} for booking on {self.booking.date} (Court: {self.booking.court.name} / Page: {self.booking.court.booking_page.name})"