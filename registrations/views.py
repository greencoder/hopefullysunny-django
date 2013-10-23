from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect

from registrations.models import Registration
from registrations.forms import RegistrationForm, UpdateForm, UpdateDataForm

#### Initial signup form and handler ####

def signup(request):
    
    if request.method == "POST":

        form = RegistrationForm(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            zip_code = form.cleaned_data['zip_code']
            
            if Registration.validate_email(email):            
                registration = Registration.signup(email, zip_code)            
                if registration:
                    registration.send_signup_email()
                    return redirect('signup-sent')
                else:
                    return redirect('signup-failure')
            else:
                return redirect('signup-failure')

    # Method was not post, so we need to show the form
    else:
        form = RegistrationForm()
    
    return render_to_response('signup_form.tpl.html', RequestContext(request, {
        'form': form,
    }))


def confirm_email(request, uuid):
    registration = Registration.confirm_email_address(uuid)
    if registration:
        registration.geocode_registration()
        return render_to_response("confirmation_success.tpl.html")
    else:
        return render_to_response("confirmation_failure.tpl.html")


#### Handle unsubscribe requests ####

def unsubscribe(request, uuid):
    success = Registration.unsubscribe(uuid=uuid)
    if success:
        return render_to_response('unsubscribe_success.tpl.html')
    else:
        return render_to_response('unsubscribe_failure.tpl.html')


#### Update preferences form and handler ####

def send_update_link(request):

    if request.method == "POST":
        form = UpdateForm(request.POST)        
        if form.is_valid():
            registration = Registration.objects.get(email=form.cleaned_data['email'])
            registration.send_udpate_email()
            return redirect('update-sent')
    else:
        form = UpdateForm()

    return render_to_response('update_link_form.tpl.html', RequestContext(request, {
        'form': form,
    }))

    
def update_registration_data(request, uuid):
    
    try:
        registration = Registration.objects.get(uuid=uuid)
    except Registration.DoesNotExist:
        return redirect('update-failure')

    if request.method == "POST":
        form = UpdateDataForm(request.POST)
        if form.is_valid():
            registration.zip_code = form.cleaned_data['zip_code']
            registration.save()
            registration.fire_geocode_task()
            return redirect('update-success')
    else:
        form = UpdateDataForm()
    
    return render_to_response('update_data_form.tpl.html', RequestContext(request, {
        'form': form,
    }))
