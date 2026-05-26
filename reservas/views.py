from django.shortcuts import render, redirect
from .models import Reserva
from .forms import ReservaForm

def gestion_reservas(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_reservas') # Te redirige a la lista al guardar
    else:
        form = ReservaForm()
        
    reservas = Reserva.objects.all()
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas, 'form': form})
