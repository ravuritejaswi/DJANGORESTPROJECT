import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    """
    Stores service categories.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Provider(models.Model):
    """
    Stores service provider information.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider",
    )

    name = models.CharField(
        max_length=150
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "providers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProviderProfile(models.Model):
    """
    Stores additional information about a service provider.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    provider = models.OneToOneField(
        Provider,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "provider_profiles"

    def __str__(self):
        return f"Profile - {self.provider.name}"


class Service(models.Model):
    """
    Stores services offered by providers.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="services"
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name="services"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "services"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

# Create your models here.

class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="service_bookings"
    )

    provider = models.ForeignKey(
        "services.Provider",
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    booking_date = models.DateField()

    booking_time = models.TimeField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "bookings"
        ordering = ["-created_at"]

    def transition_to(self, new_status):
        """
        Allows only valid booking status changes.
        """

        allowed_transitions = {
            self.Status.PENDING: {
                self.Status.CONFIRMED,
                self.Status.CANCELLED,
                self.Status.PAYMENT_FAILED,
            },

            self.Status.CONFIRMED: {
                self.Status.IN_PROGRESS,
                self.Status.CANCELLED,
            },

            self.Status.IN_PROGRESS: {
                self.Status.COMPLETED,
            },

            self.Status.COMPLETED: set(),

            self.Status.CANCELLED: set(),

            self.Status.PAYMENT_FAILED: set(),
        }

        if new_status not in self.Status.values:
            raise ValueError(
                f"Invalid booking status: {new_status}"
            )

        if new_status not in allowed_transitions.get(
            self.status,
            set()
        ):
            raise ValueError(
                f"Invalid transition from "
                f"{self.status} to {new_status}"
            )

        self.status = new_status

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"Booking {self.id}"

class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class Method(models.TextChoices):
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        CASH = "CASH", "Cash"
        WALLET = "WALLET", "Wallet"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    booking = models.OneToOneField(
        "services.Booking",
        on_delete=models.PROTECT,
        related_name="payment"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    payment_method = models.CharField(
        max_length=20,
        choices=Method.choices
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"