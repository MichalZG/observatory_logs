from django.urls import path
from objects_log import views

urlpatterns = [
    path('targets/', views.target_list),
    path('targets/<int:pk>/', views.target_detail),
    path('stats/targets/', views.targets_stats),
    path('stats/targets/<str:tname>', views.targets_stats_telescope),
]