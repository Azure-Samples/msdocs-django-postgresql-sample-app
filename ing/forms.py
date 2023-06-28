from django import forms
from datetime import datetime

# from django.core import validators
from .models import Persona, Equipo

# def check_for_z(value):
#    if value[0].lower() != 'z':
#        raise forms.ValidationError("NAME MUST START WITH Z")

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def is_datetime(string):
    try:
        datetime.strptime(string, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


class FormName(forms.Form):
    # name = forms.CharField(validators = [check_for_z])
    name = forms.CharField()
    email = forms.EmailField()
    verify_email = forms.EmailField(label="Enter email again")
    text = forms.CharField(widget=forms.Textarea)
    # botcatcher = forms.CharField(required = False, widget = forms.HiddenInput, validators = [validators.MaxLengthValidator(0)])

    def clean(self):
        all_clean_data = super().clean()
        email = all_clean_data["email"]
        vmail = all_clean_data["verify_email"]

        if vmail != email:
            raise forms.ValidationError("EMAILS MUST MATCH!")


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = "__all__"


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = "__all__"


class RegEquipoForm(forms.Form):
    sede = forms.CharField(required=False, label="Sede")
    portador = forms.CharField(required=True, label="Portador (presione + para portador nuevo)")
    equipo = forms.CharField(required=True, label="Equipo (presione + para equipo nuevo)")
    ts_ing = forms.CharField(required=True, label="Fecha-hora ingreso")
    ts_sal = forms.CharField(required=False, label="Fecha-hora salida")

    def clean(self):
        all_clean_data = super().clean()
        sede = all_clean_data["sede"]
        portador = all_clean_data["portador"]
        equipo = all_clean_data["equipo"]
        ts_ing = all_clean_data["ts_ing"]
        ts_sal = all_clean_data["ts_sal"]

        if sede == "":
            raise forms.ValidationError("Sede errada")

        list_portador = portador.split("-")
        if len(list_portador) < 2:
            raise forms.ValidationError("Portador errado (" + str(len(list_portador)) + ")")
        else:
            id_tipo = list_portador[1]
            id_num = list_portador[0]
            try:
                portador = Persona.objects.get(id_tipo=id_tipo, id_num=id_num)
            except Persona.DoesNotExist:
                raise forms.ValidationError(f"Portador: {id_tipo} {id_num} no existe")

        list_equipo = equipo.split("-")
        if len(list_equipo) != 3:
            raise forms.ValidationError("Equipo errado")
        else:
            eq_tipo = list_equipo[2]
            eq_marca = list_equipo[1]
            eq_serie = list_equipo[0]
            try:
                equipo = Equipo.objects.get(eq_tipo=eq_tipo, eq_marca=eq_marca, eq_serie=eq_serie)
            except Equipo.DoesNotExist:
                raise forms.ValidationError(f"Equipo: {eq_tipo} {eq_marca} {eq_serie} no existe")

        if is_datetime(ts_ing):
            ts_ing = datetime.strptime(ts_ing, DATETIME_FORMAT)
        else:
            raise forms.ValidationError("Time-stamp de ingreso debe estar en formato AAAA-MM-DD hh:mm")

        if ts_sal != "":
            if is_datetime(ts_sal):
                ts_sal = datetime.strptime(ts_sal, DATETIME_FORMAT)
                if ts_sal < ts_ing:
                    raise forms.ValidationError("Time-stamp de salida debe ser >= time-stamp de ingreso")
            else:
                raise forms.ValidationError("Time-stamp de salida debe estar en formato AAAA-MM-DD hh:mm")

        return all_clean_data