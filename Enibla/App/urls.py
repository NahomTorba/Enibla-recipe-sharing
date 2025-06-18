from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/confirm/', views.logout_view, name='logout_confirm'),

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),

    # sample url for home page
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),

    # URLs for profile
    path('profile/create/', views.profile_create, name='create_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    path('my-profile/', views.my_profile, name='my_profile'),

    # URLs for recipes
    path('recipes/create/', views.create_recipe, name='create_recipe'),
    # URLs for recipe editing
    path('', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipes/<str:slug>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipes/<str:slug>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<str:slug>/delete/', views.delete_recipe, name='delete_recipe')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
