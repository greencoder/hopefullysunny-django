from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from registrations.models import Registration
from forecasts.lib.forecast import Forecast

def forecast(request):
    
    email = request.GET.get('email', None)
    reg = get_object_or_404(Registration, email=email)
        
    forecasts_list = Forecast.get_forecast(reg.latitude, reg.longitude)

    return render_to_response('email.html', {
        "forecasts": forecasts_list,
        "registration": reg,
    })