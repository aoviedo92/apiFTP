from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from indexer import views

urlpatterns = [
    url(r'^index-it/$', views.Indexer.as_view()),
    url(r'^search/$', views.Search.as_view()),
    url(r'^remove/$', views.RemoveIndexedFtp.as_view()),
    url(r'^update/$', views.UpdateIndexed.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)