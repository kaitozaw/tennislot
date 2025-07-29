from allauth.account.forms import LoginForm, ResetPasswordForm, ResetPasswordKeyForm, SignupForm
from django import forms
from django.forms import formset_factory

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update({
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
        self.fields["password"].widget.attrs.update({
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })

class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            })

class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            })

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            })

class BookingPageForm(forms.Form):
    name = forms.CharField(
        label="Page Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "name",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )
    location = forms.CharField(
        label="Location",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "location",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )

class CourtForm(forms.Form):
    name = forms.CharField(
        label="Court Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "name",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )

class SlotDefinitionForm(forms.Form):
    SLOT_CHOICES = [
        (30, "30 minutes"),
        (60, "60 minutes"),
    ]

    slot_size = forms.ChoiceField(
        label="Slot Size",
        choices=SLOT_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            "id": "slot_size",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )

    price = forms.DecimalField(
        label="Price",
        max_digits=6,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            "id": "price",
            "step": "0.01",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )

class EquipmentOptionForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "id": "name",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )
    price = forms.DecimalField(
        label="Price",
        max_digits=6,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            "id": "price",
            "step": "0.01",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )


class OpeningHourRuleForm(forms.Form):
    weekday = forms.IntegerField(widget=forms.HiddenInput())
    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if (start and end) and start >= end:
            raise forms.ValidationError("Start time must be earlier than end time.")

        return cleaned_data

OpeningHourRuleFormSet = formset_factory(OpeningHourRuleForm, extra=0)

class HolidayExceptionForm(forms.Form):
    date = forms.DateField(
        label="Date",
        required=True,
        widget=forms.DateInput(attrs={
            "id": "date",
            "type": "date",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )
    start_time = forms.TimeField(
        label="Start Time",
        required=True,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "id": "start_time",
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )
    end_time = forms.TimeField(
        label="End Time",
        required=True,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "id": "end_time",
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )
    note = forms.CharField(
        label="Note",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "note",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and start >= end:
            raise forms.ValidationError("Start time must be earlier than end time.")

        return cleaned_data

class SpecialExceptionForm(forms.Form):
    court = forms.ChoiceField(
        label="Court",
        required=True,
        widget=forms.Select(attrs={
            "id": "court",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )
    date = forms.DateField(
        label="Date",
        required=True,
        widget=forms.DateInput(attrs={
            "id": "date",
            "type": "date",
            "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
        })
    )
    start_time = forms.TimeField(
        label="Start Time",
        required=True,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "id": "start_time",
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )
    end_time = forms.TimeField(
        label="End Time",
        required=True,
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "id": "end_time",
                "type": "time",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )
    note = forms.CharField(
        label="Note",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "note",
                "class": "mt-1 w-full border-gray-300 focus:ring-yellow-500 focus:border-yellow-500 rounded-md shadow-sm"
            }
        )
    )

    def __init__(self, *args, **kwargs):
        courts = kwargs.pop("courts", None)
        super().__init__(*args, **kwargs)
        if courts:
            self.fields["court"].choices = [(court.id, court.name) for court in courts]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and start >= end:
            raise forms.ValidationError("Start time must be earlier than end time.")

        return cleaned_data