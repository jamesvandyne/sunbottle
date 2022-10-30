from django.contrib import admin

from sunbottle.data.electricity import models

admin.site.register(models.Generator)
admin.site.register(models.Battery)
admin.site.register(models.GenerationReading)
admin.site.register(models.ElectricitySale)
admin.site.register(models.ElectricityPurchase)
admin.site.register(models.BatteryLevelReading)
