from django.urls import path
from . import views

app_name = 'App'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/create/', views.profile_create, name='create_profile'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('recipes/', views.recipe_list_view, name='recipe_list'),
    path('recipes/create/', views.create_recipe, name='create_recipe'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
]
