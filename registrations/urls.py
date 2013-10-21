from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('',

    url(r'^signup/confirm/(?P<uuid>[-\w\d]{32})/$', 'registrations.views.confirm_email', name='signup-confirm'),
    url(r'^signup/sent/$', TemplateView.as_view(template_name="signup_sent.tpl.html"), name='signup-sent'),
    url(r'^signup/failure/$', TemplateView.as_view(template_name="signup_failure.tpl.html"), name='signup-failure'),
    url(r'^signup/$', 'registrations.views.signup', name='signup'),
    
    url(r'^update/(?P<uuid>[-\w\d]{32})/$', 'registrations.views.update_registration_data', name='update-data'),
    url(r'^update/failure/$', TemplateView.as_view(template_name="update_failure.tpl.html"), name='update-failure'),
    url(r'^update/success/$', TemplateView.as_view(template_name="update_success.tpl.html"), name='update-success'),
    url(r'^update/sent/$', TemplateView.as_view(template_name="update_sent.tpl.html"), name='update-sent'),
    url(r'^update/$', 'registrations.views.send_update_link', name='update'),

    url(r'^unsubscribe/(?P<uuid>[-\w\d]{32})/$', 'registrations.views.unsubscribe', name='unsubscribe'),

    url(r'^$', RedirectView.as_view(url='/registration/signup/')),
)
