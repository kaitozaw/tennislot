from django.contrib import admin

# Register your models here.
from .models import (Organiser, BookingPage, Court, SlotDefinition, EquipmentOption,OpeningHourRule, HolidayException, SpecialException,Booking, BookingEquipmentOption)

models = [Organiser, BookingPage, Court, SlotDefinition, EquipmentOption,OpeningHourRule, HolidayException, SpecialException,Booking, BookingEquipmentOption]

for model in models:
    admin.site.register(model)