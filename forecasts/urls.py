from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'forecasts.views.forecast'),
)
