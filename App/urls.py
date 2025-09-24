from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    # sample url for home page
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),

    


    # URLs for reviews
    path('recipe/<slug:slug>/review/add', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # API Endpoints for saved recipes
    path('api/check-saved-recipe/<slug:slug>/', views.check_saved_recipe, name='check_saved_recipe'),
    path('api/save-recipe/<slug:slug>/', views.save_recipe, name='save_recipe'),
    path('api/unsave-recipe/<slug:slug>/', views.unsave_recipe, name='unsave_recipe'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
