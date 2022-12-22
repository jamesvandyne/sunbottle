from django.db import models


class Generator(models.Model):
    """
    An electricity generator e.g. solar panels.
    """

    name = models.CharField(max_length=128, unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GenerationReading(models.Model):
    """
    An individual reading.
    """

    generator = models.ForeignKey(Generator, on_delete=models.CASCADE)

    kwh = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField()

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("generator", "occurred_at")


class Battery(models.Model):
    """
    A battery
    """

    name = models.CharField(max_length=128, unique=True)
    capacity = models.DecimalField(max_digits=6, decimal_places=2)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BatteryLevelReading(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, related_name="level_readings")

    charge_percent = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField()

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("battery", "occurred_at")


class ElectricityUsage(models.Model):
    """
    Records the total electricity usage for a given period.
    """

    kwh = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField(unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectricityPurchase(models.Model):
    kwh = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField(unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectricitySale(models.Model):
    kwh = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField(unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ConsumptionReading(models.Model):
    """
    An individual consumption reading.
    """

    kwh = models.DecimalField(max_digits=6, decimal_places=3)

    occurred_at = models.DateTimeField(unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
