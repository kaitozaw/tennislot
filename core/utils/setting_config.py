from core.forms import CourtForm, EquipmentOptionForm, HolidayExceptionForm, SpecialExceptionForm
from core.models import Court, EquipmentOption, HolidayException, SpecialException

SETTING_CONFIG = {
    "courts": {
        "form": CourtForm,
        "model": Court,
        "session_key": "courts",
        "template": "partials/_court_list.html",
        "db_field": "courts",
    },
    "equipment_options": {
        "form": EquipmentOptionForm,
        "model": EquipmentOption,
        "session_key": "equipment_options",
        "template": "partials/_equipment_option_list.html",
        "db_field": "equipment_options",
    },
    "holiday_exceptions": {
        "form": HolidayExceptionForm,
        "model": HolidayException,
        "session_key": "holiday_exceptions",
        "template": "partials/_holiday_exception_list.html",
        "db_field": "holiday_exceptions",
    },
    "special_exceptions": {
        "form": SpecialExceptionForm,
        "model": SpecialException,
        "session_key": "special_exceptions",
        "template": "partials/_special_exception_list.html",
        "db_field": None,
    },
}