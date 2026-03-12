from django.contrib import admin
from .models import (
    User, Lab, PC, LabEquipment, NetworkEquipmentDetails, ServerDetails,
    ProjectorDetails, ElectricalApplianceDetails, Peripheral, Software,
    MaintenanceLog, LabEquipment, CPU, OS
)

### Inline editing for LabEquipment under Lab admin (Lab -> LabEquipment)
class LabEquipmentInline(admin.TabularInline):
    model = LabEquipment
    extra = 0
    fields = ('equipment_code', 'name', 'equipment_type', 'category', 'brand', 'model_name', 'quantity', 'status')

### Inline editing for LabEquipment details (OneToOne) under LabEquipment admin
class NetworkEquipmentDetailsInline(admin.StackedInline):
    model = NetworkEquipmentDetails
    fk_name = 'equipment'
    extra = 0

class ServerDetailsInline(admin.StackedInline):
    model = ServerDetails
    fk_name = 'equipment'
    extra = 0

class ProjectorDetailsInline(admin.StackedInline):
    model = ProjectorDetails
    fk_name = 'equipment'
    extra = 0

class ElectricalApplianceDetailsInline(admin.StackedInline):
    model = ElectricalApplianceDetails
    fk_name = 'equipment'
    extra = 0


# --------------------------
# Custom User Admin
# --------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)


# --------------------------
# Lab Admin
# --------------------------
@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    search_fields = ('name', 'location')
    inlines = [LabEquipmentInline]


# --------------------------
# PC Admin
# --------------------------
@admin.register(PC)
class PCAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'lab', 'brand', 'status', 'connected', 'gpu')
    list_filter = ('lab', 'status', 'connected')
    search_fields = ('device_name', 'lab__name', 'brand', 'serial_number')


# --------------------------
# CPU Admin
# --------------------------
@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ('model', 'pc', 'clock_speed', 'core_count', 'integrated_graphics')
    list_filter = ('integrated_graphics',)
    search_fields = ('model', 'pc__device_name')


# --------------------------
# OS Admin
# --------------------------
@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'pc', 'architecture', 'expiration_date')
    list_filter = ('architecture',)
    search_fields = ('name', 'version', 'pc__device_name')


# --------------------------
# Peripheral Admin
# --------------------------
@admin.register(Peripheral)
class PeripheralAdmin(admin.ModelAdmin):
    list_display = ('peripheral_type', 'brand', 'model_name', 'pc', 'status')
    list_filter = ('peripheral_type', 'status')
    search_fields = ('brand', 'model_name', 'pc__device_name')


# --------------------------
# Software Admin
# --------------------------
@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'pc')
    list_filter = ('pc',)
    search_fields = ('name', 'version', 'pc__device_name')


# --------------------------
# Lab Equipment Admin
# --------------------------
@admin.register(LabEquipment)
class LabEquipmentAdmin(admin.ModelAdmin):
    list_display = ('equipment_code', 'name', 'equipment_type', 'category', 'lab', 'quantity', 'status')
    list_filter = ('category', 'equipment_type', 'status', 'lab')
    search_fields = ('equipment_code', 'name', 'brand', 'model_name', 'lab__name')
    ordering = ('equipment_code',)
    inlines = [NetworkEquipmentDetailsInline, ServerDetailsInline, ProjectorDetailsInline, ElectricalApplianceDetailsInline]


# --------------------------
# Network Equipment Details Admin
# --------------------------
@admin.register(NetworkEquipmentDetails)
class NetworkEquipmentDetailsAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'ip_address', 'mac_address', 'number_of_ports', 'managed_switch')
    search_fields = ('equipment__name', 'ip_address', 'mac_address')


# --------------------------
# Server Details Admin
# --------------------------
@admin.register(ServerDetails)
class ServerDetailsAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'cpu_model', 'total_ram', 'total_storage', 'virtualization_enabled')
    search_fields = ('equipment__name', 'cpu_model')


# --------------------------
# Projector Details Admin
# --------------------------
@admin.register(ProjectorDetails)
class ProjectorDetailsAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'resolution', 'brightness_lumens', 'hdmi_ports')
    search_fields = ('equipment__name', 'resolution')


# --------------------------
# Electrical Appliance Details Admin
# --------------------------
@admin.register(ElectricalApplianceDetails)
class ElectricalApplianceDetailsAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'power_rating', 'voltage', 'inverter_type', 'service_due_date')
    search_fields = ('equipment__name', 'power_rating')


# --------------------------
# Maintenance Log Admin
# --------------------------
@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('get_device', 'status', 'reported_by', 'fixed_by', 'reported_on', 'fixed_on')
    list_filter = ('status', 'lab')
    search_fields = ('reported_by__username', 'fixed_by__username', 'issue_description')

    def get_device(self, obj):
        if obj.pc:
            return f"PC: {obj.pc.device_name}"
        elif obj.peripheral:
            return f"Peripheral: {obj.peripheral.peripheral_type}"
        elif obj.lab_equipment:
            return f"Equipment: {obj.lab_equipment.name}"
        return "Unknown"
    
    get_device.short_description = 'Device'
