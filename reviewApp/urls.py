from django.urls import path
from reviewApp import views   

urlpatterns = [
    # URLs for reviews
    path('recipe/<slug:slug>/review/add', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # API Endpoints for saved recipes
    path('api/check-saved-recipe/<slug:slug>/', views.check_saved_recipe, name='check_saved_recipe'),
    path('api/save-recipe/<slug:slug>/', views.save_recipe, name='save_recipe'),
    path('api/unsave-recipe/<slug:slug>/', views.unsave_recipe, name='unsave_recipe'),
]