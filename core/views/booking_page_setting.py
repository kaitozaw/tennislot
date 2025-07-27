from core.forms import BookingPageForm, CourtForm, SlotDefinitionForm, EquipmentOptionForm, OpeningHourRuleFormSet, HolidayExceptionForm, SpecialExceptionForm
from core.models import BookingPage, Court, SlotDefinition, EquipmentOption, OpeningHourRule, HolidayException, SpecialException
from core.utils.setting_config import SETTING_CONFIG
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
import secrets

@login_required
def launch_setting(request, mode, booking_page_id=None):
    if mode == "create":        
        setting = request.session.get("setting", {}) or {}
        request.session["setting"] = setting
        source = setting
    else:
        booking_page = get_object_or_404(BookingPage, id=booking_page_id)
        source = booking_page

    section = "booking_page"

    context = {
        "mode": mode,
        "section": section,
    }
    context.update(get_context_setting(mode, source, section))
    context.update(get_context_form(mode, source, section))
    if mode == "edit":
        context["booking_page"] = booking_page

    return render(request, f"booking_page_{mode}.html", context)

@login_required
def navigate_setting(request, mode, direction=None, section=None, booking_page_id=None):
    if mode == "create":
        current_section = request.GET.get("current")
        section = get_section(current_section, direction)
        if not section:
            return HttpResponseBadRequest("Invalid section or direction")
        
        setting = request.session.get("setting", {}) or {}
        source = setting

        if request.method == "POST":
            source = save_setting(request, mode, source, current_section)
            request.session["setting"] = source

            if section == "save":
                create_settings(request, source)
                return redirect("dashboard")
    else:
        booking_page = get_object_or_404(BookingPage, id=booking_page_id)
        source = booking_page

    context = {
        "mode": mode,
        "section": section
    }
    context.update(get_context_setting(mode, source, section))
    context.update(get_context_form(mode, source, section))
    if mode == "edit":
        context["booking_page"] = booking_page

    return render(request, f"partials/_settings_{section}.html", context)
    
def get_section(current_section, direction):
    section_ORDER = [
        "booking_page",
        "courts",
        "slot_definition",
        "equipment_options",
        "opening_hour_rules",
        "save",
    ]

    if current_section not in section_ORDER:
        return None

    idx = section_ORDER.index(current_section)
    if direction == "next" and idx + 1 < len(section_ORDER):
        return section_ORDER[idx + 1]
    elif direction == "previous" and idx - 1 >= 0:
        return section_ORDER[idx - 1]
    
    return None

def get_context_setting(mode, source, section=None):
    context = {}

    if mode == "create":
        context["setting"] = source

    else:
        if section == "courts":
            courts = source.courts.all()
            context["setting"] = {"courts": courts}

        elif section == "equipment_options":
            equipment_options = source.equipment_options.all()
            context["setting"] = {"equipment_options": equipment_options}

        elif section == "holiday_exceptions":
            holiday_exceptions = source.holiday_exceptions.all()
            context["setting"] = {"holiday_exceptions": holiday_exceptions}

        elif section == "special_exceptions":
            courts = source.courts.all()
            special_exceptions = []
            for court in courts:
                special_exceptions.extend(court.special_exceptions.all())
            context["setting"] = {
                "courts": courts,
                "special_exceptions": special_exceptions
            }
    
    return context

def get_context_form(mode, source, section):
    context = {}

    if section == "booking_page":
        data = source if mode == "create" else {
            "name": source.name,
            "location": source.location,
        }
        initial = {
            "name": data.get("name", ""),
            "location": data.get("location", ""),
        }
        context["form"] = BookingPageForm(initial=initial)
        
    elif section == "courts":
        context["form"] = CourtForm()

    elif section == "slot_definition":
        data = source.get("slot_definition", {}) if mode == "create" else {
            "slot_size": source.slot_definition.slot_size,
            "price": source.slot_definition.price,
        }
        initial = {
            "slot_size": data.get("slot_size", ""),
            "price": data.get("price", ""),
        }
        context["form"] = SlotDefinitionForm(initial=initial)

    elif section == "equipment_options":
        context["form"] = EquipmentOptionForm()

    elif section == "opening_hour_rules":
        if mode == "create":
            rules_dict = {r["weekday"]: r for r in source.get("opening_hour_rules", [])}
        elif mode == "edit":
            rules_dict = {r.weekday: r for r in source.opening_hour_rules.all()}

        initial = []
        for weekday, _ in OpeningHourRule.WEEKDAYS:
            rule = rules_dict.get(weekday)
            if mode == "create":
                start = rule.get("start_time", "") if rule else ""
                end = rule.get("end_time", "") if rule else ""
            else:
                start = rule.start_time if rule else ""
                end = rule.end_time if rule else ""
            initial.append({
                "weekday": weekday,
                "start_time": start,
                "end_time": end,
            })

        context["formset"] = OpeningHourRuleFormSet(initial=initial)
        context["weekday_choices"] = dict(OpeningHourRule.WEEKDAYS)

    elif section == "holiday_exceptions":
        context["form"] = HolidayExceptionForm()

    elif section == "special_exceptions":
        courts = source.get("courts", []) if mode == "create" else source.courts.all()
        context["form"] = SpecialExceptionForm(courts=courts)

    return context

@login_required
def save_setting_edit(request, booking_page_id, section):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    
    booking_page = get_object_or_404(BookingPage, id=booking_page_id)
    source = booking_page

    save_setting(request, "edit", source, section)

    context = {
        "mode": "edit",
        "section": section,
        "booking_page": booking_page
    }
    context.update(get_context_setting("edit", source, section))
    context.update(get_context_form("edit", source, section))

    return render(request, f"partials/_settings_{section}.html", context)

def save_setting(request, mode, source, section):
    if section == "booking_page":
        form = BookingPageForm(request.POST)
        if form.is_valid():
            if mode == "create":
                source.update(form.cleaned_data)
            else:
                source.name = form.cleaned_data["name"]
                source.location = form.cleaned_data["location"]
                source.save()
    
    elif section == "slot_definition":
        form = SlotDefinitionForm(request.POST)
        if form.is_valid():
            slot_size = int(form.cleaned_data["slot_size"])
            price = float(form.cleaned_data["price"])

            if mode == "create":
                source["slot_definition"] = {
                    "slot_size": slot_size,
                    "price": price,
                }
            else:
                source.slot_definition.slot_size = slot_size
                source.slot_definition.price = price
                source.slot_definition.save()
    
    elif section == "opening_hour_rules":
        formset = OpeningHourRuleFormSet(request.POST)
        if formset.is_valid():
            opening_hour_rules = []
            for form in formset:
                data = form.cleaned_data
                if not data.get("start_time") or not data.get("end_time"):
                    continue
                opening_hour_rules.append({
                    "weekday": data["weekday"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                })

                if mode == "edit":
                    obj, created = OpeningHourRule.objects.get_or_create(
                        booking_page=source,
                        weekday=data["weekday"],
                        defaults={
                            "start_time": data["start_time"],
                            "end_time": data["end_time"],
                        }
                    )
                    if not created:
                        obj.start_time = data["start_time"]
                        obj.end_time = data["end_time"]
                        obj.save()

            if mode == "create":
                source["opening_hour_rules"] = opening_hour_rules

    return source

def create_settings(request, source):
    name = source.get("name", "").strip()
    location = source.get("location", "").strip()
    courts = source.get("courts", [])
    slot_definition = source.get("slot_definition", {})
    equipment_options = source.get("equipment_options", [])
    opening_hour_rules = source.get("opening_hour_rules", [])

    if not name or not location or not courts or not slot_definition or not opening_hour_rules:
        raise ValueError("Missing required fields for saving booking page")

    public_url = secrets.token_urlsafe(8)
    while BookingPage.objects.filter(public_url=public_url).exists():
        public_url = secrets.token_urlsafe(8)

    with transaction.atomic():
        booking_page = BookingPage.objects.create(
            organiser=request.user,
            name=name,
            location=location,
            public_url=public_url,
            is_active=False
        )

        for court in courts:
            Court.objects.create(
                booking_page=booking_page,
                name=court["name"]
            )

        SlotDefinition.objects.create(
            booking_page=booking_page,
            slot_size=slot_definition["slot_size"],
            price=slot_definition["price"]
        )

        for option in equipment_options:
            EquipmentOption.objects.create(
                booking_page=booking_page,
                name=option["name"],
                price=option["price"]
            )

        for rule in opening_hour_rules:
            OpeningHourRule.objects.create(
                booking_page=booking_page,
                weekday=rule["weekday"],
                start_time=rule["start_time"],
                end_time=rule["end_time"]
            )
    
    del request.session["setting"]

    return booking_page

@login_required
def add_setting_item(request, mode, section, booking_page_id=None):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    config = SETTING_CONFIG.get(section)
    if not config:
        return HttpResponseBadRequest("Invalid section")

    form_class = config["form"]

    if mode == "create":
        form = form_class(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest("Invalid input")
        
        cleaned_data = {
            k: float(v) if isinstance(v, Decimal) else v
            for k, v in form.cleaned_data.items()
        }
        
        setting = request.session.get("setting", {})
        items = setting.get(config["session_key"], [])
        items.append(cleaned_data)
        setting[config["session_key"]] = items
        request.session["setting"] = setting

        return render(request, config["template"], {
            "mode": "create",
            "section": section,
            "setting": setting,
            "form": form_class()
        })
    
    else:
        booking_page = get_object_or_404(BookingPage, id=booking_page_id)

        if section == "special_exceptions":
            form = form_class(request.POST, courts=booking_page.courts.all())
            if not form.is_valid():
                return HttpResponseBadRequest("Invalid input")
            
            court = get_object_or_404(BookingPage, id=form.cleaned_data["court"])
            
            config["model"].objects.create(court=court, **{k: v for k, v in form.cleaned_data.items() if k != "court"})
            items = []
            for court in booking_page.courts.all():
                items.extend(court.special_exceptions.all())

        else:
            form = form_class(request.POST)
            if not form.is_valid():
                return HttpResponseBadRequest("Invalid input")

            cleaned_data = {
                k: float(v) if isinstance(v, Decimal) else v
                for k, v in form.cleaned_data.items()
            }
            
            config["model"].objects.create(booking_page=booking_page, **cleaned_data)
            items = getattr(booking_page, config["db_field"]).all()
        
        return render(request, config["template"], {
            "mode": "edit",
            "section": section,
            "setting": {section: items},
            "form": form_class(),
            "booking_page": booking_page
        })

@login_required
def delete_setting_item(request, mode, section, index=None, booking_page_id=None, object_id=None):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    
    config = SETTING_CONFIG.get(section)
    if not config:
        return HttpResponseBadRequest("Invalid setting type")

    if mode == "create":
        setting = request.session.get("setting", {})
        items = setting.get(config["session_key"], [])

        if index is not None and 0 <= index < len(items):
            items.pop(index)
            setting[config["session_key"]] = items
            request.session["setting"] = setting

        return render(request, config["template"], {
            "mode": "create",
            "section": section,
            "setting": setting
        })

    else:
        booking_page = get_object_or_404(BookingPage, id=booking_page_id)

        if section == "special_exceptions":
            obj = SpecialException.objects.filter(id=object_id).first()
            if not obj:
                return HttpResponseBadRequest("Item not found")
            obj.delete()
            items = []
            for court in booking_page.courts.all():
                items.extend(court.special_exceptions.all())
        else:
            obj = getattr(booking_page, config["db_field"]).filter(id=object_id).first()
            if not obj:
                return HttpResponseBadRequest("Item not found")
            obj.delete()
            items = getattr(booking_page, config["db_field"]).all()

        return render(request, config["template"], {
            "mode": "edit",
            "booking_page": booking_page,
            "section": section,
            "setting": {section: items}
        })