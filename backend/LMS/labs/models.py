from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


# ------------------------------
# 1) Custom User (with Roles)
# ------------------------------

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users_permissions',
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ------------------------------
# 2) Lab Model
# ------------------------------
class Lab(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


# -------------------------------
# 3) PC model (Main Table)
# -------------------------------
class PC(models.Model):
    STATUS_CHOICES = (
        ('working', 'Working'),
        ('not_working', 'Not Working'),
    )

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='pcs')
    device_name = models.CharField(max_length=100, help_text="Institution label for the PC")
    product_id = models.CharField(max_length=100, blank=True, null=True, help_text="Manufacturer identifier")
    processor = models.CharField(max_length=200, blank=True, null=True, help_text="Basic processor description")
    ram = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 8GB")
    storage = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 512GB SSD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    connected = models.BooleanField(default=True, help_text="Is the PC connected to network")
    gpu = models.BooleanField(default=False, help_text="Dedicated GPU present")
    peripherals = models.BooleanField(default=False, help_text="Peripherals tracked")
    brand = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['lab']),
            models.Index(fields=['status']),
            models.Index(fields=['device_name']),
        ]
        unique_together = ('lab', 'device_name')
        ordering = ['device_name']

    def __str__(self):
        return self.device_name


# -------------------------------
# 4) CPU Subtable (OneToOne with PC)
# -------------------------------
class CPU(models.Model):
    pc = models.OneToOneField(
        PC,
        on_delete=models.CASCADE,
        related_name='cpu'
    )
    model = models.CharField(max_length=200, help_text="CPU model name")
    clock_speed = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 3.6 GHz")
    core_count = models.IntegerField(blank=True, null=True, help_text="Number of cores")
    integrated_graphics = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['pc']),
        ]

    def __str__(self):
        return f"{self.model} ({self.pc.device_name})"


# -------------------------------
# 5) OS Subtable (OneToOne with PC)
# -------------------------------
class OS(models.Model):
    ARCHITECTURE_CHOICES = (
        ('32-bit', '32-bit'),
        ('64-bit', '64-bit'),
    )

    pc = models.OneToOneField(
        PC,
        on_delete=models.CASCADE,
        related_name='os'
    )
    name = models.CharField(max_length=100, help_text="OS name e.g., Windows, Ubuntu")
    version = models.CharField(max_length=50, blank=True, null=True, help_text="OS version e.g., 11 Pro, 22.04")
    install_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True, help_text="License expiration date")
    architecture = models.CharField(max_length=20, choices=ARCHITECTURE_CHOICES, default='64-bit')
    product_key = models.CharField(max_length=200, blank=True, null=True, help_text="License key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['pc']),
        ]

    def __str__(self):
        return f"{self.name} {self.version} ({self.pc.device_name})"


# -------------------------------
# 6) Peripherals Subtable (linked to PC)
# -------------------------------
class Peripheral(models.Model):
    TYPE_CHOICES = (
        ('monitor', 'Monitor'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('headset', 'Headset'),
        ('webcam', 'Webcam'),
        ('printer', 'Printer'),
        ('speaker', 'Speaker'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('working', 'Working'),
        ('not_working', 'Not Working'),
    )

    pc = models.ForeignKey(PC, on_delete=models.CASCADE, related_name='peripheral_devices')
    peripheral_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['pc']),
            models.Index(fields=['peripheral_type']),
            models.Index(fields=['status']),
        ]
        ordering = ['pc', 'peripheral_type']

    def __str__(self):
        return f"{self.peripheral_type} - {self.model_name or 'Unknown'} ({self.pc.device_name})"


# ------------------------------
# 7) Software installed on PCs
# ------------------------------
class Software(models.Model):
    pc = models.ForeignKey(
        PC,
        on_delete=models.CASCADE,
        related_name="installed_software"
    )
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, blank=True, null=True)
    license_key = models.CharField(max_length=200, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['pc']),
        ]
        unique_together = ('pc', 'name', 'version')

    def __str__(self):
        return f"{self.name} ({self.version}) - PC: {self.pc.device_name}"


# ==============================================================
# 🔷 LAB EQUIPMENT SYSTEM (Unified for non-PC hardware)
# ==============================================================

# ------------------------------
# 8) Main Table: LabEquipment
# ------------------------------
class LabEquipment(models.Model):
    CATEGORY_CHOICES = (
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('APPLIANCE', 'Appliance'),
    )
    
    EQUIPMENT_TYPES = (
        ('SERVER', 'Server'),
        ('ROUTER', 'Router'),
        ('SWITCH', 'Switch'),
        ('HUB', 'Hub'),
        ('PROJECTOR', 'Projector'),
        ('E_BOARD', 'E-Board'),
        ('AC', 'Air Conditioner'),
        ('FAN', 'Fan'),
        ('LIGHT', 'Light'),
        ('UPS', 'UPS'),
        ('OTHER', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('working', 'Working'),
        ('not_working', 'Not Working'),
        ('under_repair', 'Under Repair'),
    )

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='lab_equipments')
    equipment_code = models.CharField(max_length=50, help_text="Internal tracking ID (e.g., LAB1-SW-01)")
    name = models.CharField(max_length=200, help_text="Human readable name (e.g., Cisco Core Switch)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='INFRASTRUCTURE')
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES, default='OTHER')
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    is_networked = models.BooleanField(default=False, help_text="Whether connected to network")
    installation_date = models.DateField(blank=True, null=True)
    location_in_lab = models.CharField(max_length=200, blank=True, null=True, help_text="Wall A, Rack 2, Ceiling, etc.")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['lab']),
            models.Index(fields=['category']),
            models.Index(fields=['equipment_type']),
            models.Index(fields=['status']),
            models.Index(fields=['equipment_code']),
        ]
        unique_together = ('lab', 'equipment_code')
        ordering = ['equipment_code']

    def __str__(self):
        return f"{self.equipment_code} - {self.name} ({self.equipment_type})"


# ------------------------------
# 9) Subtable: NetworkEquipmentDetails
# For: ROUTER, SWITCH, HUB, SERVER, E_BOARD
# ------------------------------
class NetworkEquipmentDetails(models.Model):
    NETWORK_TYPES = ('ROUTER', 'SWITCH', 'HUB', 'SERVER', 'E_BOARD')

    equipment = models.OneToOneField(
        LabEquipment,
        on_delete=models.CASCADE,
        related_name='network_details'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=50, blank=True, null=True)
    firmware_version = models.CharField(max_length=100, blank=True, null=True)
    number_of_ports = models.PositiveIntegerField(blank=True, null=True)
    rack_unit_size = models.PositiveIntegerField(blank=True, null=True, help_text="Size in rack units")
    managed_switch = models.BooleanField(default=False, help_text="Is it a managed switch")
    bandwidth_capacity = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1Gbps, 10Gbps")
    power_rating = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 500W")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['equipment']),
        ]

    def clean(self):
        if self.equipment.equipment_type not in self.NETWORK_TYPES:
            raise ValidationError(f"NetworkEquipmentDetails can only be attached to {', '.join(self.NETWORK_TYPES)} type equipment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Network Details - {self.equipment.name}"


# ------------------------------
# 10) Subtable: ServerDetails
# For: SERVER
# ------------------------------
class ServerDetails(models.Model):
    equipment = models.OneToOneField(
        LabEquipment,
        on_delete=models.CASCADE,
        related_name='server_details'
    )
    cpu_model = models.CharField(max_length=200, blank=True, null=True)
    total_ram = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 32GB, 64GB")
    total_storage = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1TB SSD, 2x 500GB")
    raid_config = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., RAID 1, RAID 5")
    virtualization_enabled = models.BooleanField(default=False)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['equipment']),
        ]

    def clean(self):
        if self.equipment.equipment_type != 'SERVER':
            raise ValidationError("ServerDetails can only be attached to SERVER type equipment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Server Details - {self.equipment.name}"


# ------------------------------
# 11) Subtable: ProjectorDetails
# For: PROJECTOR
# ------------------------------
class ProjectorDetails(models.Model):
    equipment = models.OneToOneField(
        LabEquipment,
        on_delete=models.CASCADE,
        related_name='projector_details'
    )
    resolution = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1920x1080, 4K")
    brightness_lumens = models.PositiveIntegerField(blank=True, null=True, help_text="Brightness in lumens")
    throw_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Short throw, Long throw")
    hdmi_ports = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['equipment']),
        ]

    def clean(self):
        if self.equipment.equipment_type != 'PROJECTOR':
            raise ValidationError("ProjectorDetails can only be attached to PROJECTOR type equipment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Projector Details - {self.equipment.name}"


# ------------------------------
# 12) Subtable: ElectricalApplianceDetails
# For: AC, FAN, LIGHT
# ------------------------------
class ElectricalApplianceDetails(models.Model):
    ELECTRICAL_TYPES = ('AC', 'FAN', 'LIGHT')

    equipment = models.OneToOneField(
        LabEquipment,
        on_delete=models.CASCADE,
        related_name='electrical_details'
    )
    power_rating = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1500W, 2HP")
    voltage = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 220V, 110V")
    inverter_type = models.BooleanField(default=False, help_text="Is it an inverter AC")
    energy_rating = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 5 Star, A++")
    service_due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['equipment']),
        ]

    def clean(self):
        if self.equipment.equipment_type not in self.ELECTRICAL_TYPES:
            raise ValidationError(f"ElectricalApplianceDetails can only be attached to {', '.join(self.ELECTRICAL_TYPES)} type equipment.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Electrical Details - {self.equipment.name}"


# ==============================================================
# 🔷 MAINTENANCE LOG (supports PC, LabEquipment, Peripheral)
# ==============================================================

# ------------------------------
# 13) Maintenance Logs
# ------------------------------
class MaintenanceLog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('fixed', 'Fixed'),
    )

    pc = models.ForeignKey(PC, on_delete=models.CASCADE, related_name="maintenance_logs", null=True, blank=True)
    lab_equipment = models.ForeignKey(LabEquipment, on_delete=models.CASCADE, related_name="maintenance_logs", null=True, blank=True)
    peripheral = models.ForeignKey(Peripheral, on_delete=models.CASCADE, related_name="maintenance_logs", null=True, blank=True)
    lab = models.ForeignKey('Lab', on_delete=models.CASCADE, related_name="maintenance_logs", null=True, blank=True)

    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reported_issues")
    fixed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fixed_issues")
    issue_description = models.TextField(blank=True, null=True)
    status_before = models.CharField(max_length=20, blank=True, null=True)
    status_after = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reported_on = models.DateTimeField(auto_now_add=True)
    fixed_on = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['pc']),
            models.Index(fields=['lab_equipment']),
            models.Index(fields=['peripheral']),
            models.Index(fields=['lab']),
            models.Index(fields=['status']),
        ]
        ordering = ['-reported_on']

    def clean(self):
        targets = [self.pc, self.lab_equipment, self.peripheral]
        filled = [t for t in targets if t is not None]

        if len(filled) != 1:
            raise ValidationError("Exactly one of pc, lab_equipment, or peripheral must be set.")

    def save(self, *args, **kwargs):
        self.clean()
        
        if not self.lab:
            if self.pc:
                self.lab = self.pc.lab
            elif self.lab_equipment:
                self.lab = self.lab_equipment.lab
            elif self.peripheral:
                self.lab = self.peripheral.pc.lab
        super().save(*args, **kwargs)

    def __str__(self):
        if self.pc:
            return f"Issue on PC {self.pc.device_name} - {self.status}"
        elif self.peripheral:
            return f"Issue on {self.peripheral.peripheral_type} - {self.status}"
        elif self.lab_equipment:
            return f"Issue on {self.lab_equipment.name} - {self.status}"
        return f"Issue - {self.status}"
