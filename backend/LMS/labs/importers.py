import pandas as pd
import os
from datetime import datetime
from django.db import transaction
from labs.models import Lab, PC, LabEquipment, NetworkEquipmentDetails, ServerDetails, ProjectorDetails, ElectricalApplianceDetails


ALLOWED_EQUIPMENT_TYPES = [c[0] for c in LabEquipment.EQUIPMENT_TYPES]
ALLOWED_CATEGORIES = [c[0] for c in LabEquipment.CATEGORY_CHOICES]
ALLOWED_STATUS = [c[0] for c in LabEquipment.STATUS_CHOICES]
NETWORK_TYPES = ('ROUTER', 'SWITCH', 'HUB', 'SERVER', 'E_BOARD')


def load_dataframe(file):
    """Load CSV or Excel file into pandas DataFrame."""
    name = file.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(file, on_bad_lines='skip')
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            return pd.read_excel(file)
        else:
            raise ValueError("Only CSV and XLSX files are supported.")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")


def get_val(row, *keys, default=None):
    """Get value from row, handling NaN and None properly."""
    for key in keys:
        val = row.get(key)
        if val is not None and not pd.isna(val):
            return val
    return default


def parse_bool(val):
    """Parse boolean value from various representations."""
    if val is None or pd.isna(val):
        return False
    val_str = str(val).lower().strip()
    return val_str in ('yes', 'true', '1', 'y', 't')


def parse_int(val, default=None):
    """Parse integer value from various representations."""
    if val is None or pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def normalize_columns(df):
    """Normalize column names to lowercase, replace spaces with underscores."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    return df


def get_or_create_lab(file_name=None, lab_name=None, lab_id=None):
    """Helper to get or create a Lab for import."""
    if lab_id:
        try:
            return Lab.objects.get(id=lab_id), None
        except Lab.DoesNotExist:
            return None, f"Lab with id {lab_id} not found"
    
    if lab_name:
        lab, created = Lab.objects.get_or_create(name=lab_name)
        return lab, None
    
    # Auto-create lab from filename
    if file_name:
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        lab_name = f"Imported_{base_name}_{datetime.now().strftime('%Y%m%d')}"
    else:
        lab_name = f"Imported_Lab_{datetime.now().strftime('%Y%m%d')}"
    
    lab, created = Lab.objects.get_or_create(name=lab_name)
    return lab, None


# -----------------------
# LABS IMPORT
# -----------------------
@transaction.atomic
def import_labs(file):
    """
    Import Labs from file.
    Expected columns: name, location
    Returns: (created_count, skipped_count, error_list)
    """
    df = load_dataframe(file)
    df = normalize_columns(df)
    
    created, skipped = 0, 0
    errors = []

    for i, row in df.iterrows():
        try:
            # Try multiple column names for lab name
            lab_name = get_val(row, "name", "lab_name", "labname")
            
            if not lab_name or str(lab_name).strip() == '':
                errors.append(f"Row {i+2}: Lab name is required")
                continue
            
            lab_name = str(lab_name).strip()
            
            # Check for duplicates
            if Lab.objects.filter(name=lab_name).exists():
                skipped += 1
                continue

            # Location - optional
            location = get_val(row, "location", "lab_location")

            Lab.objects.create(name=lab_name, location=location)
            created += 1

        except Exception as e:
            errors.append(f"Row {i+2}: {type(e).__name__}: {e}")

    return created, skipped, errors


# -----------------------
# PCS IMPORT
# -----------------------
@transaction.atomic
def import_pcs(file, lab_id=None):
    """
    Import PCs from file.
    Expected columns: device_name (or name, pc_name), status, brand, etc.
    Returns: dict with lab, created, skipped, errors
    """
    df = load_dataframe(file)
    df = normalize_columns(df)
    
    # Get or create lab
    file_name = getattr(file, 'name', None)
    lab, error = get_or_create_lab(file_name=file_name, lab_id=lab_id)
    if error:
        return {"lab": None, "created": 0, "skipped": 0, "errors": [error]}
    
    created, skipped = 0, 0
    errors = []

    for i, row in df.iterrows():
        try:
            # Try multiple column names for PC name
            device_name = get_val(row, "device_name", "name", "pc_name", "pc_name_comp_id")
            
            if not device_name or str(device_name).strip() == '':
                errors.append(f"Row {i+2}: PC device name is required")
                continue
            
            device_name = str(device_name).strip()
            
            # Check for duplicates in same lab
            if PC.objects.filter(lab=lab, device_name=device_name).exists():
                skipped += 1
                continue
            
            # Status - default to working
            status = get_val(row, "status", default="working")
            if status and status not in ALLOWED_STATUS:
                status = "working"
            
            connected = parse_bool(row.get("connected"))
            gpu = parse_bool(row.get("gpu"))
            peripherals = parse_bool(row.get("peripherals"))

            PC.objects.create(
                lab=lab,
                device_name=device_name,
                product_id=get_val(row, "product_id"),
                processor=get_val(row, "processor"),
                ram=get_val(row, "ram"),
                storage=get_val(row, "storage"),
                status=status,
                connected=connected,
                gpu=gpu,
                peripherals=peripherals,
                brand=get_val(row, "brand"),
                serial_number=get_val(row, "serial_number", "serial")
            )
            created += 1

        except Exception as e:
            errors.append(f"Row {i+2}: {type(e).__name__}: {e}")

    return {
        "lab": lab.name if lab else None,
        "created": created,
        "skipped": skipped,
        "errors": errors
    }


# -----------------------
# LAB EQUIPMENT IMPORT
# -----------------------
@transaction.atomic
def import_lab_equipment(file, lab_id=None):
    """
    Import LabEquipment from file.
    Expected columns: equipment_code, name, equipment_type, category, quantity, status, etc.
    Optional subtable columns: ip_address, mac_address, cpu_model, etc.
    Returns: (created_count, skipped_count, error_list)
    """
    df = load_dataframe(file)
    df = normalize_columns(df)
    
    # Get or create lab
    file_name = getattr(file, 'name', None)
    lab, error = get_or_create_lab(file_name=file_name, lab_id=lab_id)
    if error:
        return {"lab": None, "created": 0, "skipped": 0, "errors": [error]}
    
    created, skipped = 0, 0
    errors = []

    for i, row in df.iterrows():
        try:
            # Equipment code - try multiple column names
            equipment_code = get_val(row, "equipment_code", "code", "eq_code")
            
            # Generate code if missing
            if not equipment_code or str(equipment_code).strip() == '':
                equipment_code = f"EQ-{lab.id}-{i+1:04d}"
            else:
                equipment_code = str(equipment_code).strip()
            
            # Name - fallback to code
            name = get_val(row, "name", "equipment_name", "eq_name") or equipment_code
            name = str(name).strip()
            
            # Category - default to INFRASTRUCTURE
            category = get_val(row, "category", "cat") or "INFRASTRUCTURE"
            if category not in ALLOWED_CATEGORIES:
                category = "INFRASTRUCTURE"
            
            # Equipment type - default to OTHER
            eq_type_raw = get_val(row, "equipment_type", "type", "eq_type")
            if eq_type_raw is not None:
                eq_type = str(eq_type_raw).strip().upper()
            else:
                eq_type = "OTHER"
            if eq_type not in ALLOWED_EQUIPMENT_TYPES:
                errors.append(f"Row {i+2}: Invalid equipment_type '{eq_type}', defaulting to OTHER")
                eq_type = "OTHER"
            
            # Status - default to working
            status = get_val(row, "status", default="working")
            if status and status not in ALLOWED_STATUS:
                status = "working"
            
            # Quantity
            quantity = parse_int(row.get("quantity"), default=1)
            if quantity < 1:
                quantity = 1
            
            is_networked = parse_bool(row.get("is_networked"))
            
            # Check for duplicate in same lab
            if LabEquipment.objects.filter(lab=lab, equipment_code=equipment_code).exists():
                skipped += 1
                continue
            
            # Create LabEquipment
            lab_equipment = LabEquipment.objects.create(
                lab=lab,
                equipment_code=equipment_code,
                name=name,
                category=category,
                equipment_type=eq_type,
                brand=get_val(row, "brand"),
                model_name=get_val(row, "model_name", "model"),
                quantity=quantity,
                status=status,
                is_networked=is_networked,
                installation_date=get_val(row, "installation_date"),
                location_in_lab=get_val(row, "location_in_lab", "location"),
                remarks=get_val(row, "remarks", "notes"),
            )
            created += 1
            
            # ----- SUBTABLES CREATION -----
            
            # NetworkEquipmentDetails (for ROUTER, SWITCH, HUB, SERVER, E_BOARD)
            if eq_type in NETWORK_TYPES:
                ip_address = get_val(row, "ip_address", "ip")
                mac_address = get_val(row, "mac_address", "mac")
                
                if ip_address or mac_address:
                    try:
                        NetworkEquipmentDetails.objects.create(
                            equipment=lab_equipment,
                            ip_address=ip_address,
                            mac_address=mac_address,
                            firmware_version=get_val(row, "firmware_version", "firmware"),
                            number_of_ports=parse_int(row.get("number_of_ports")) or parse_int(row.get("ports")),
                            rack_unit_size=parse_int(row.get("rack_unit_size")) or parse_int(row.get("rack_size")),
                            managed_switch=parse_bool(row.get("managed_switch")),
                            bandwidth_capacity=get_val(row, "bandwidth_capacity", "bandwidth"),
                            power_rating=get_val(row, "power_rating", "power")
                        )
                    except Exception as e:
                        errors.append(f"Row {i+2} (NetworkDetails): {type(e).__name__}: {e}")
            
            # ServerDetails (for SERVER only)
            if eq_type == "SERVER":
                cpu_model = get_val(row, "cpu_model", "cpu")
                total_ram = get_val(row, "total_ram", "ram")
                total_storage = get_val(row, "total_storage", "storage")
                
                if cpu_model or total_ram or total_storage:
                    try:
                        ServerDetails.objects.create(
                            equipment=lab_equipment,
                            cpu_model=cpu_model,
                            total_ram=total_ram,
                            total_storage=total_storage,
                            raid_config=get_val(row, "raid_config", "raid"),
                            virtualization_enabled=parse_bool(row.get("virtualization_enabled")),
                            operating_system=get_val(row, "operating_system", "os")
                        )
                    except Exception as e:
                        errors.append(f"Row {i+2} (ServerDetails): {type(e).__name__}: {e}")
            
            # ProjectorDetails (for PROJECTOR)
            if eq_type == "PROJECTOR":
                resolution = get_val(row, "resolution")
                brightness_lumens = parse_int(row.get("brightness_lumens")) or parse_int(row.get("brightness"))
                
                if resolution or brightness_lumens:
                    try:
                        ProjectorDetails.objects.create(
                            equipment=lab_equipment,
                            resolution=resolution,
                            brightness_lumens=brightness_lumens,
                            throw_type=get_val(row, "throw_type", "throw"),
                            hdmi_ports=parse_int(row.get("hdmi_ports")) or parse_int(row.get("hdmi"))
                        )
                    except Exception as e:
                        errors.append(f"Row {i+2} (ProjectorDetails): {type(e).__name__}: {e}")
            
            # ElectricalApplianceDetails (for AC, FAN, LIGHT)
            if eq_type in ('AC', 'FAN', 'LIGHT'):
                power_rating = get_val(row, "power_rating", "power")
                voltage = get_val(row, "voltage")
                
                if power_rating or voltage:
                    try:
                        ElectricalApplianceDetails.objects.create(
                            equipment=lab_equipment,
                            power_rating=power_rating,
                            voltage=voltage,
                            inverter_type=parse_bool(row.get("inverter_type")),
                            energy_rating=get_val(row, "energy_rating", "energy_star"),
                            service_due_date=get_val(row, "service_due_date", "service_date")
                        )
                    except Exception as e:
                        errors.append(f"Row {i+2} (ElectricalDetails): {type(e).__name__}: {e}")

        except Exception as e:
            errors.append(f"Row {i+2}: {type(e).__name__}: {e}")

    return {
        "lab": lab.name if lab else None,
        "created": created,
        "skipped": skipped,
        "errors": errors
    }
