from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from datetime import date
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template

from pagos.models import Pago


def obtenerDatos(pagos):

    hoy = date.today()

    total_recaudado = pagos.aggregate(total=Sum("monto"))["total"] or 0

    total_pagos = pagos.count()

    promedio = pagos.aggregate(media=Avg("monto"))["media"] or 0

    recaudado_hoy = pagos.filter(fecha=hoy).aggregate(totalhoy=Sum("monto"))["totalhoy"] or 0

    return {"total_recaudado": total_recaudado,"total_pagos": total_pagos,"promedio": promedio,"recaudado_hoy": recaudado_hoy}


def get_pagos_filtrados(request):
    pagos = Pago.objects.filter(estado="PAGADO")

    fechaInicio = request.GET.get("fechaInicio")
    fechaFin = request.GET.get("fechaFin")

    if fechaInicio and fechaInicio != "None":
        pagos = pagos.filter(fecha__gte=fechaInicio)

    if fechaFin and fechaFin != "None":
        pagos = pagos.filter(fecha__lte=fechaFin)

    return pagos, fechaInicio, fechaFin

def obtenerDatosXdia(pagos):

    pagosFecha = (pagos.values("fecha").annotate(total=Sum("monto")).order_by("fecha"))

    labelsDia = [d["fecha"].strftime("%d/%m")for d in pagosFecha]

    valuesDia = [d["total"]for d in pagosFecha]

    return labelsDia, valuesDia

def montoPorOrigen(pagos):
    

    pagosOrigenMonto= pagos.values("origen_pago").annotate(total=Sum("monto"))

    labelMonto = [d["origen_pago"].replace("_", " ").title() for d in pagosOrigenMonto]
    valuesMonto=[d["total"]for d in pagosOrigenMonto]


    return labelMonto,valuesMonto



def reporte_ingresos(request):
    pagos, fechaInicio, fechaFin = get_pagos_filtrados(request)
    
    datos = obtenerDatos(pagos)

    pagosOrigen = pagos.values("origen_pago").annotate(total=Count("id"))

    labels = [d["origen_pago"].replace("_"," ").title() for d in pagosOrigen]
    values = [d["total"] for d in pagosOrigen]

    labelsDia, valuesDia = obtenerDatosXdia(pagos)
    labelsmonto, valuesMonto = montoPorOrigen(pagos)
    
    return render(request,"reportes/reporte_ingresos.html",{"pagos":pagos,**datos,"fechaInicio":fechaInicio,"fechaFin":fechaFin,"labels":labels,
    "values":values,"labelsDia":labelsDia,"valuesDia":valuesDia,"labelsmonto":labelsmonto,"valuesMonto":valuesMonto})




def exportar_pdf(request):
    pagos, fechaInicio, fechaFin = get_pagos_filtrados(request)

    if not fechaInicio:
        fechaInicio = "Inicio"

    if not fechaFin:
        fechaFin = "Actual"

    datos = obtenerDatos(pagos)

    template = get_template("reportes/reporte_pdf.html")
    html = template.render({
        "pagos": pagos,
        **datos,
        "fechaInicio": fechaInicio,
        "fechaFin": fechaFin
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reporte_ingresos.pdf"'
    pisa.CreatePDF(html, dest=response)

    return response