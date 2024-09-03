from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload_images, name='resize_image'),
    # path('success/', image_resize_success, name='image_resize_success'),
     path('download/', views.download_images, name='download_images'),
]
