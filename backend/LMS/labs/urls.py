from django.urls import path
from . import views

urlpatterns = [
    # Users
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    
    # Labs
    path('labs/', views.LabList.as_view(), name='lab-list'),
    path('labs/<int:pk>/', views.LabDetail.as_view(), name='lab-detail'),
    path('labs/<int:lab_id>/pcs/', views.LabPCList.as_view(), name='lab-pc-list'),
    path('labs/<int:lab_id>/lab-equipment/', views.LabLabEquipmentList.as_view(), name='lab-lab-equipment-list'),
    
    # PCs
    path('pcs/', views.PCList.as_view(), name='pc-list'),
    path('pcs/<int:pk>/', views.PCDetail.as_view(), name='pc-detail'),
    path('pcs/<int:pc_id>/peripherals/', views.PCPeripheralList.as_view(), name='pc-peripheral-list'),
    
    # CPU (OneToOne with PC)
    path('cpu/', views.CPUList.as_view(), name='cpu-list'),
    path('cpu/<int:pk>/', views.CPUDetail.as_view(), name='cpu-detail'),
    
    # OS (OneToOne with PC)
    path('os/', views.OSList.as_view(), name='os-list'),
    path('os/<int:pk>/', views.OSDetail.as_view(), name='os-detail'),
    
    # Peripherals
    path('peripherals/', views.PeripheralList.as_view(), name='peripheral-list'),
    path('peripherals/<int:pk>/', views.PeripheralDetail.as_view(), name='peripheral-detail'),
    
    # Software
    path('software/', views.SoftwareList.as_view(), name='software-list'),
    path('software/<int:pk>/', views.SoftwareDetail.as_view(), name='software-detail'),
    
    # Lab Equipment (unified for non-PC hardware)
    path('lab-equipment/', views.LabEquipmentList.as_view(), name='lab-equipment-list'),
    path('lab-equipment/<int:pk>/', views.LabEquipmentDetail.as_view(), name='lab-equipment-detail'),
    
    # Lab Equipment Detail Subtables
    path('network-details/', views.NetworkEquipmentDetailsList.as_view(), name='network-details-list'),
    path('network-details/<int:pk>/', views.NetworkEquipmentDetailsDetail.as_view(), name='network-details-detail'),
    path('server-details/', views.ServerDetailsList.as_view(), name='server-details-list'),
    path('server-details/<int:pk>/', views.ServerDetailsDetail.as_view(), name='server-details-detail'),
    path('projector-details/', views.ProjectorDetailsList.as_view(), name='projector-details-list'),
    path('projector-details/<int:pk>/', views.ProjectorDetailsDetail.as_view(), name='projector-details-detail'),
    path('electrical-details/', views.ElectricalApplianceDetailsList.as_view(), name='electrical-details-list'),
    path('electrical-details/<int:pk>/', views.ElectricalApplianceDetailsDetail.as_view(), name='electrical-details-detail'),
    
    # Maintenance
    path('maintenance/', views.MaintenanceLogList.as_view(), name='maintenance-log-list'),
    path('maintenance/<int:pk>/', views.MaintenanceLogDetail.as_view(), name='maintenance-log-detail'),
    
    # Inventory (dynamic calculation)
    path('inventory/', views.inventory_list, name='inventory-list'),
    
    # Utility endpoints
    path('redirect-after-login/', views.redirect_after_login, name='redirect-after-login'),
    path('labs/import/', views.import_data_api, name='labs-import'),
]
