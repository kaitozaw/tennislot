"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import dashboard_view, launch_setting, navigate_setting, save_setting_edit, add_setting_item, delete_setting_item

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("booking_page/create/", launch_setting, {'mode': 'create'}, name="launch_setting_create"),
    path("booking_page/<int:booking_page_id>/edit/", launch_setting, {'mode': 'edit'}, name="launch_setting_edit"),
    path("booking_page/navigate/<str:direction>/", navigate_setting, {'mode': 'create'}, name="navigate_setting_create"),
    path('booking_page/<int:booking_page_id>/navigate/<str:section>/', navigate_setting, {'mode': 'edit'}, name='navigate_setting_edit'),
    path('booking_page/<int:booking_page_id>/edit/save/<str:section>/', save_setting_edit, name='save_setting_edit'),
    path("booking_page/add/<str:section>/", add_setting_item, {'mode': 'create'}, name="add_setting_item_create"),
    path("booking_page/<int:booking_page_id>/add/<str:section>/", add_setting_item, {'mode': 'edit'}, name="add_setting_item_edit"),
    path("booking_page/delete/<str:section>/<int:index>/", delete_setting_item, {'mode': 'create'}, name="delete_setting_item_create"),
    path("booking_page/<int:booking_page_id>/delete/<str:section>/<int:object_id>/", delete_setting_item, {'mode': 'edit'}, name="delete_setting_item_edit"),
]