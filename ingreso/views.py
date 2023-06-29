import json

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.views.generic import TemplateView, ListView

from . import forms
from . import models
from .models import Sede, Equipo, Persona, RegEquipo

import pytz
from datetime import datetime

from django.contrib import messages

# Create your views here.

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def get_messages_count(request):
    count = messages.get_messages(request).__len__()
    return count


class IndexView(TemplateView):
    template_name = "ingreso/index.html"


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse("ingreso:sedes"))
            else:
                return HttpResponse("Usuario no activo!")
        else:
            print("Alguien trató de logearse sin éxito")
            print("Usuario: '{}', password: '{}'".format(username, password))
            return HttpResponse("Usuario/password inválido!")
    else:
        return render(request, "ingreso/login.html", {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


class SedeListView(LoginRequiredMixin, ListView):
    context_object_name = "sedes"
    model = models.Sede


def sede(request, sede_id):
    sede = Sede.objects.get(id=sede_id)
    request.session["sede_id"] = sede_id
    request.session["sede_nombre"] = str(sede)

    return HttpResponseRedirect(reverse("ingreso:req_hoy"))

@login_required
def req_hoy(request):
    if not request.session.get("sede_id", None):
        return HttpResponseRedirect(reverse("ingreso:sedes"))

    xdt = datetime.now() #timezone.now().date() #
    wdt = datetime(xdt.year, xdt.month, xdt.day, 0, 0, 0, 0) #datetime.combine(xdt, time.min) #

    sede_id = request.session["sede_id"]
    sede_nombre = request.session["sede_nombre"]

    req_list = RegEquipo.objects.filter(sede=sede_id, ts_ing__gte=wdt).order_by("-ts_ing")

    return render(request,"ingreso/req_hoy.html", {"req_list": req_list, "sede_nombre": sede_nombre},)


@login_required
def crear_persona(request):
    form = forms.PersonaForm()

    if request.method == "POST":
        form = forms.PersonaForm(request.POST)

        if form.is_valid():
            # DO SOMETHING
            form.save()
            messages.success(request, "Persona creada")
        else:
            messages.error(request, "Forma con errores: muy probablemente ya existe una persona con ese documento(id)")

    return render(request, "ingreso/persona_form.html", {"form": form})


@login_required
def crear_equipo(request):
    form =  forms.EquipoForm()

    if request.method == "POST":
        form = forms.EquipoForm(request.POST)

        if form.is_valid():
            # DO SOMETHING
            form.save()
            messages.success(request, "Equipo creado")
        else:
            messages.error(request, "Forma con errores: muy probablemente ya existe un equipo con esa marca, tipo y # de serie")

    return render(request, "ingreso/equipo_form.html", {"form": form})


@login_required
def registrar_salida_equipo(request, req_id):
    req = RegEquipo.objects.get(id=req_id)
    req.ts_sal = datetime.now()
    req.save()

    messages.success(request, "Registro actualizado exitosamente")
    return HttpResponseRedirect(reverse("ingreso:req_hoy"))


def is_datetime(string):
    try:
        datetime.strptime(string, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


@login_required
def borrar_req(request, req_id):
    try:
        req = RegEquipo.objects.get(id=req_id)
    except:
        messages.error(request, "Registro no existe")

    if request.method == "POST":
        if get_messages_count(request) == 0:
            req.delete()
            messages.success(request, "Registro borrado exitosamente")
            return HttpResponseRedirect(reverse("ingreso:req_hoy"))

    return render(request, "ingreso/borrar_req.html", {"req": req})


def autocomplete_portador(request):
    if is_ajax(request=request):
        query = request.GET.get("term", "").capitalize()
        # print(f"query: {query}")
        query_set = Persona.objects.filter(id_num__startswith=query)
        results = []
        for per in query_set:
            results.append(per.id_num + "-" + per.id_tipo + "-" + per.nom_persona)
        data = json.dumps(results)
    else:
        data = "fail"

    mimetype = "application/json"
    return HttpResponse(data, mimetype)


def autocomplete_equipo(request):
    if is_ajax(request=request):
        query = request.GET.get("term", "").capitalize()
        # print(f"query: {query}")
        query_set = Equipo.objects.filter(eq_serie__startswith=query)
        results = []
        for eq in query_set:
            results.append(eq.eq_serie + "-" + eq.eq_marca + "-" + eq.eq_tipo)
        data = json.dumps(results)
    else:
        data = "fail"

    mimetype = "application/json"
    return HttpResponse(data, mimetype)


def is_ajax(request):
    """
    The HttpRequest.is_ajax() method is deprecated as it relied on a jQuery-specific way of signifying AJAX calls,
    while current usage tends to use the JavaScript Fetch API.
    Depending on your use case, you can either write your own AJAX detection method,
    or use the new HttpRequest.accepts() method if your code depends on the client Accept HTTP header.
    Even though it has been deprecated, you can create a custom function to check the request type as ...
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

from .forms import PersonaForm, EquipoForm, RegEquipoForm
from django.shortcuts import redirect

@login_required
def crear_req(request):
    wdt = datetime.now().strftime("%Y-%m-%d %H:%M")
    formRegEquipo = RegEquipoForm(initial={'sede': request.session['sede_nombre'], 'ts_ing': wdt})
    formPersona = PersonaForm
    formEquipo = EquipoForm
    
    if request.method == "POST":
        formRegEquipo = RegEquipoForm(request.POST)
        if formRegEquipo.is_valid():
            error_count = 0
            regeq = RegEquipo()
            sede_id = request.session["sede_id"]
            try:
                regeq.sede = Sede.objects.get(id=sede_id)
            except Sede.DoesNotExist:
                messages.error(request, f"Sede: {sede_id} no existe")
                error_count += 1

            str_portador = formRegEquipo.cleaned_data['portador']
            list_portador = str_portador.split("-")
            id_tipo = list_portador[1]
            id_num = list_portador[0]
            try:
                regeq.portador = Persona.objects.get(id_tipo=id_tipo, id_num=id_num)
            except Persona.DoesNotExist:
                messages.error(request, f"Portador: {id_tipo} {id_num} no existe")
                error_count += 1
    
            str_equipo = formRegEquipo.cleaned_data['equipo']
            list_equipo = str_equipo.split("-")
            eq_tipo = list_equipo[2]
            eq_marca = list_equipo[1]
            eq_serie = list_equipo[0]
            try:
                regeq.equipo = Equipo.objects.get(eq_tipo=eq_tipo, eq_marca=eq_marca, eq_serie=eq_serie)
            except Equipo.DoesNotExist:
                messages.error(request, f"Equipo: {eq_tipo} {eq_marca} {eq_serie} no existe")
                error_count += 1

            regeq.ts_ing = formRegEquipo.cleaned_data['ts_ing']
            wts_sal = formRegEquipo.cleaned_data['ts_sal']
            
            if wts_sal == "":
                regeq.ts_sal = None
            else:
                regeq.ts_sal = wts_sal
            
            if error_count == 0:
                regeq.save()
                messages.success(request, "Registro creado satisfactoriamente")
                return redirect('ingreso:req_hoy')

    return render(request, 'ingreso/req_form.html', {'is_update': False, 'formRegEquipo': formRegEquipo, 'formPersona': formPersona, 'formEquipo': formEquipo})

from django.conf import settings

@login_required
def mod_req(request, req_id):
    regeq = RegEquipo.objects.get(id=req_id)
    local_tz = pytz.timezone(settings.TIME_ZONE)
    formRegEquipo = RegEquipoForm(
        initial={'sede': request.session['sede_nombre'], 
                 'portador': str(regeq.portador),
                 'equipo': str(regeq.equipo),
                 'ts_ing': regeq.ts_ing.astimezone(local_tz).strftime("%Y-%m-%d %H:%M"),
                 'ts_sal': "" if regeq.ts_sal is None else regeq.ts_sal.astimezone(local_tz).strftime("%Y-%m-%d %H:%M"),
                 })
    formPersona = PersonaForm
    formEquipo = EquipoForm
    
    if request.method == "POST":
        formRegEquipo = RegEquipoForm(request.POST)
        if formRegEquipo.is_valid():
            error_count = 0
            str_portador = formRegEquipo.cleaned_data['portador']
            list_portador = str_portador.split("-")
            id_tipo = list_portador[1]
            id_num = list_portador[0]
            try:
                regeq.portador = Persona.objects.get(id_tipo=id_tipo, id_num=id_num)
            except Persona.DoesNotExist:
                messages.error(request, f"Portador: {id_tipo} {id_num} no existe")
                error_count += 1
    
            str_equipo = formRegEquipo.cleaned_data['equipo']
            list_equipo = str_equipo.split("-")
            eq_tipo = list_equipo[2]
            eq_marca = list_equipo[1]
            eq_serie = list_equipo[0]
            try:
                regeq.equipo = Equipo.objects.get(eq_tipo=eq_tipo, eq_marca=eq_marca, eq_serie=eq_serie)
            except Equipo.DoesNotExist:
                messages.error(request, f"Equipo: {eq_tipo} {eq_marca} {eq_serie} no existe")
                error_count += 1

            regeq.ts_ing = formRegEquipo.cleaned_data['ts_ing']
            wts_sal = formRegEquipo.cleaned_data['ts_sal']
            
            if wts_sal == "":
                regeq.ts_sal = None
            else:
                regeq.ts_sal = wts_sal
            
            if error_count == 0:
                regeq.save()
                messages.success(request, "Registro modificado satisfactoriamente")
                return redirect('ingreso:req_hoy')

    return render(request, 'ingreso/req_form.html', {'is_update': True, 'formRegEquipo': formRegEquipo, 'formPersona': formPersona, 'formEquipo': formEquipo})


from django.http import JsonResponse

@login_required
def ajax_query_view_persona(request):
    # Get the query parameters sent via Ajax
    err = ""
    form = PersonaForm(request.POST)

    if form.is_valid():
        id_tipo = form.cleaned_data['id_tipo']
        id_num = form.cleaned_data['id_num']
        nom_persona = form.cleaned_data['nom_persona']
        try:
            form.save()
            wresult = f"{id_num}-{id_tipo}-{nom_persona}"
        except Exception as e:
            err = str(e)
    else:
        err = "Forma con errores: muy posiblemente persona(id) ya existe"

    # Create a response data in JSON format
    if err == "":
        return JsonResponse({'result': wresult})
    else:
        return JsonResponse({'error': err}, status=400)

@login_required
def ajax_query_view_equipo(request):
    # Get the query parameters sent via Ajax
    err = ""
    form = EquipoForm(request.POST)

    if form.is_valid():
        eq_tipo = form.cleaned_data['eq_tipo']
        eq_marca = form.cleaned_data['eq_marca']
        eq_serie = form.cleaned_data['eq_serie']
        try:
            form.save()
            wresult = f"{eq_serie}-{eq_marca}-{eq_tipo}"
        except Exception as e:
            err = str(e)
    else:
        err = "Forma con errores: muy posiblemente equipo ya existe"

    # Create a response data in JSON format
    if err == "":
        return JsonResponse({'result': wresult})
    else:
        return JsonResponse({'error': err}, status=400)
