from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.home,               name='home'),
    path('add/',                  views.add_application,    name='add'),
    path('app/<int:pk>/',         views.detail,             name='detail'),
    path('app/<int:pk>/edit/',    views.edit_application,   name='edit'),
    path('app/<int:pk>/delete/',  views.delete_application, name='delete'),
    path('app/<int:pk>/ai-insight/', views.get_ai_insight, name='ai_insight'),
    path('app/<int:pk>/ask-ai/',     views.ask_ai,         name='ask_ai'),
    path('dashboard/',            views.dashboard,          name='dashboard'),
]
