from rest_framework import serializers
from .models import (
    User, Lab, PC, CPU, OS, Peripheral, Software,
    LabEquipment, NetworkEquipmentDetails, ServerDetails, 
    ProjectorDetails, ElectricalApplianceDetails, MaintenanceLog
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'


class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = '__all__'


class OSSerializer(serializers.ModelSerializer):
    class Meta:
        model = OS
        fields = '__all__'


class PeripheralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peripheral
        fields = '__all__'


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = '__all__'


class PCSerializer(serializers.ModelSerializer):
    cpu = CPUSerializer(read_only=True)
    os = OSSerializer(read_only=True)
    peripheral_devices = PeripheralSerializer(many=True, read_only=True)
    installed_software = SoftwareSerializer(many=True, read_only=True)

    class Meta:
        model = PC
        fields = '__all__'


# ===============================
# Lab Equipment Serializers
# ===============================

class NetworkEquipmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkEquipmentDetails
        fields = '__all__'


class ServerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerDetails
        fields = '__all__'


class ProjectorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectorDetails
        fields = '__all__'


class ElectricalApplianceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricalApplianceDetails
        fields = '__all__'


class LabEquipmentSerializer(serializers.ModelSerializer):
    network_details = NetworkEquipmentDetailsSerializer(read_only=True)
    server_details = ServerDetailsSerializer(read_only=True)
    projector_details = ProjectorDetailsSerializer(read_only=True)
    electrical_details = ElectricalApplianceDetailsSerializer(read_only=True)

    class Meta:
        model = LabEquipment
        fields = '__all__'


class LabEquipmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabEquipment
        fields = '__all__'


class MaintenanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceLog
        fields = '__all__'

    def validate(self, data):
        # Validate that exactly one target is set
        pc = data.get('pc')
        lab_equipment = data.get('lab_equipment')
        peripheral = data.get('peripheral')
        
        targets = [pc, lab_equipment, peripheral]
        filled = [t for t in targets if t is not None]
        
        if len(filled) != 1:
            raise serializers.ValidationError(
                "Exactly one of pc, lab_equipment, or peripheral must be set."
            )
        
        return data
