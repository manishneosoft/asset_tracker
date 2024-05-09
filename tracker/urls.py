from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.login_view, name='index'),
    path('seeder/', views.seeder_dashboard, name='seeder'),
    path('seeder/addsysadmin', views.addsysadmin, name='addsysadmin'),
    path('seeder/edit_sysadmin/<int:pk>/', views.update_sysadmin_profile, name='editsysadmin'),

    path('sysadmin_dashboard/', views.sysadmin_dashboard, name='sysadmin_dashboard'),
    
    path('asset_types/', views.manage_asset_types, name='manage_asset_types'),
    path('addassettype/', views.addassettype, name='addassettype'),
    path('edit_assettype/<int:pk>/', views.update_asset_type, name='edit_assettype'),
    path('delete_assettype/<int:pk>/', views.delete_assettype, name='delete_assettype'),



    path('assets/', views.manage_assets, name='manage_assets'),
    path('assets_csv/', views.assets_csv, name='assets_csv'),
    path('addasset/', views.add_asset, name='addasset'),
    path('edit_asset/<int:pk>/', views.edit_asset, name='edit_asset'),
    path('delete_asset/<int:pk>/', views.delete_asset, name='delete_asset'),







    path('logout/', views.logout_user, name='logout'),
]
