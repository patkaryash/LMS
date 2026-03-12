from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import (
    User, Lab, PC, CPU, OS, Peripheral, Software,
    LabEquipment, NetworkEquipmentDetails, ServerDetails,
    ProjectorDetails, ElectricalApplianceDetails, MaintenanceLog
)
from .serializers import (
    UserSerializer, LabSerializer, PCSerializer, CPUSerializer, OSSerializer,
    PeripheralSerializer, SoftwareSerializer,
    LabEquipmentSerializer, LabEquipmentListSerializer,
    NetworkEquipmentDetailsSerializer, ServerDetailsSerializer,
    ProjectorDetailsSerializer, ElectricalApplianceDetailsSerializer,
    MaintenanceLogSerializer
)
from .permissions import IsAdminOrReadOnly, AllowAuthenticatedReadAndCreateElseAdmin
from .importers import import_labs, import_pcs, import_lab_equipment


# ===============================
# User & Lab Views
# ===============================

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]


class LabList(generics.ListCreateAPIView):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [IsAdminOrReadOnly]


class LabDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [IsAdminOrReadOnly]


# ===============================
# PC Views
# ===============================

class PCList(generics.ListCreateAPIView):
    queryset = PC.objects.all()
    serializer_class = PCSerializer
    permission_classes = [IsAdminOrReadOnly]


class PCDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PC.objects.all()
    serializer_class = PCSerializer
    permission_classes = [IsAdminOrReadOnly]


class LabPCList(generics.ListCreateAPIView):
    serializer_class = PCSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        lab_id = self.kwargs['lab_id']
        return PC.objects.filter(lab=lab_id)

    def perform_create(self, serializer):
        lab_id = self.kwargs['lab_id']
        try:
            lab = Lab.objects.get(id=lab_id)
            serializer.save(lab=lab)
        except Lab.DoesNotExist:
            raise ValidationError({'lab': 'Lab not found'})


# ===============================
# CPU Views (OneToOne with PC)
# ===============================

class CPUList(generics.ListCreateAPIView):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    permission_classes = [IsAdminOrReadOnly]


class CPUDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    permission_classes = [IsAdminOrReadOnly]


# ===============================
# OS Views (OneToOne with PC)
# ===============================

class OSList(generics.ListCreateAPIView):
    queryset = OS.objects.all()
    serializer_class = OSSerializer
    permission_classes = [IsAdminOrReadOnly]


class OSDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OS.objects.all()
    serializer_class = OSSerializer
    permission_classes = [IsAdminOrReadOnly]


# ===============================
# Peripheral Views (OneToMany with PC)
# ===============================

class PeripheralList(generics.ListCreateAPIView):
    queryset = Peripheral.objects.all()
    serializer_class = PeripheralSerializer
    permission_classes = [IsAdminOrReadOnly]


class PeripheralDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Peripheral.objects.all()
    serializer_class = PeripheralSerializer
    permission_classes = [IsAdminOrReadOnly]


class PCPeripheralList(generics.ListCreateAPIView):
    serializer_class = PeripheralSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        pc_id = self.kwargs['pc_id']
        return Peripheral.objects.filter(pc_id=pc_id)

    def perform_create(self, serializer):
        pc_id = self.kwargs['pc_id']
        try:
            pc = PC.objects.get(id=pc_id)
            serializer.save(pc=pc)
        except PC.DoesNotExist:
            raise ValidationError({'pc': 'PC not found'})


# ===============================
# Software Views
# ===============================

class SoftwareList(generics.ListCreateAPIView):
    queryset = Software.objects.all()
    serializer_class = SoftwareSerializer
    permission_classes = [IsAdminOrReadOnly]


class SoftwareDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Software.objects.all()
    serializer_class = SoftwareSerializer
    permission_classes = [IsAdminOrReadOnly]


# ===============================
# Lab Equipment Views
# ===============================

class LabEquipmentList(generics.ListCreateAPIView):
    queryset = LabEquipment.objects.all()
    serializer_class = LabEquipmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class LabEquipmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LabEquipment.objects.all()
    serializer_class = LabEquipmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class LabLabEquipmentList(generics.ListCreateAPIView):
    serializer_class = LabEquipmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        lab_id = self.kwargs['lab_id']
        return LabEquipment.objects.filter(lab_id=lab_id)

    def perform_create(self, serializer):
        lab_id = self.kwargs['lab_id']
        try:
            lab = Lab.objects.get(id=lab_id)
            serializer.save(lab=lab)
        except Lab.DoesNotExist:
            raise ValidationError({'lab': 'Lab not found'})


# ===============================
# Lab Equipment Detail Subtables
# ===============================

class NetworkEquipmentDetailsList(generics.ListCreateAPIView):
    queryset = NetworkEquipmentDetails.objects.all()
    serializer_class = NetworkEquipmentDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class NetworkEquipmentDetailsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NetworkEquipmentDetails.objects.all()
    serializer_class = NetworkEquipmentDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ServerDetailsList(generics.ListCreateAPIView):
    queryset = ServerDetails.objects.all()
    serializer_class = ServerDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ServerDetailsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServerDetails.objects.all()
    serializer_class = ServerDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProjectorDetailsList(generics.ListCreateAPIView):
    queryset = ProjectorDetails.objects.all()
    serializer_class = ProjectorDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProjectorDetailsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectorDetails.objects.all()
    serializer_class = ProjectorDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ElectricalApplianceDetailsList(generics.ListCreateAPIView):
    queryset = ElectricalApplianceDetails.objects.all()
    serializer_class = ElectricalApplianceDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


class ElectricalApplianceDetailsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ElectricalApplianceDetails.objects.all()
    serializer_class = ElectricalApplianceDetailsSerializer
    permission_classes = [IsAdminOrReadOnly]


# ===============================
# Maintenance Log Views
# ===============================

class MaintenanceLogList(generics.ListCreateAPIView):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [AllowAuthenticatedReadAndCreateElseAdmin]

    def get_queryset(self):
        return MaintenanceLog.objects.all()

    def perform_create(self, serializer):
        pc = serializer.validated_data.get('pc')
        lab_equipment = serializer.validated_data.get('lab_equipment')
        peripheral = serializer.validated_data.get('peripheral')
        
        lab = None
        if pc:
            lab = pc.lab
        elif lab_equipment:
            lab = lab_equipment.lab
        elif peripheral:
            lab = peripheral.pc.lab
            
        # Pass through the validated data along with additional fields
        serializer.save(
            reported_by=self.request.user,
            lab=lab,
            status='pending',
        )


class MaintenanceLogDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    permission_classes = [AllowAuthenticatedReadAndCreateElseAdmin]


# ===============================
# Inventory API (Dynamic calculation)
# ===============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_list(request):
    from rest_framework import serializers as rf_serializers
    
    class InventorySerializer(rf_serializers.Serializer):
        id = rf_serializers.CharField(read_only=True)
        lab = rf_serializers.IntegerField()
        lab_name = rf_serializers.CharField()
        equipment_type = rf_serializers.CharField()
        total_quantity = rf_serializers.IntegerField()
        working_quantity = rf_serializers.IntegerField()
        not_working_quantity = rf_serializers.IntegerField()
        under_repair_quantity = rf_serializers.IntegerField()
    
    labs = Lab.objects.all()
    inventory_data = []

    for lab in labs:
        equipment_in_lab = LabEquipment.objects.filter(lab=lab)
        equipment_types = equipment_in_lab.values_list('equipment_type', flat=True).distinct()

        for eq_type in equipment_types:
            eq_of_type = equipment_in_lab.filter(equipment_type=eq_type)

            inventory_data.append({
                'id': f"{lab.id}_{eq_type}",
                'lab': lab.id,
                'lab_name': lab.name,
                'equipment_type': eq_type,
                'total_quantity': sum(eq_of_type.values_list('quantity', flat=True)),
                'working_quantity': sum(eq_of_type.filter(status='working').values_list('quantity', flat=True)),
                'not_working_quantity': sum(eq_of_type.filter(status='not_working').values_list('quantity', flat=True)),
                'under_repair_quantity': sum(eq_of_type.filter(status='under_repair').values_list('quantity', flat=True)),
            })

    serializer = InventorySerializer(inventory_data, many=True)
    return Response(serializer.data)


# ===============================
# Redirect after login
# ===============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def redirect_after_login(request):
    user = request.user
    if user.role == 'student':
        return Response({'redirect_to': '/api/maintenance/'})
    elif user.role == 'admin':
        return Response({'redirect_to': '/api/lab-equipment/'})
    else:
        return Response({'redirect_to': '/api/'})


# ===============================
# Import API
# ===============================

@csrf_exempt
def import_data_api(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    file = request.FILES.get("file")
    entity = request.POST.get("entity")

    if not file or not entity:
        return JsonResponse(
            {"detail": "file and entity are required (labs | pcs | lab-equipment)"},
            status=400,
        )

    try:
        if entity == "labs":
            created, skipped, errors = import_labs(file)
        elif entity == "pcs":
            result = import_pcs(file)
            created = result['created']
            skipped = result['skipped']
            errors = result['errors']
        elif entity == "lab-equipment":
            created, skipped, errors = import_lab_equipment(file)
        else:
            return JsonResponse({"detail": "Invalid entity"}, status=400)

        return JsonResponse(
            {
                "status": "success",
                "entity": entity,
                "created": created,
                "skipped": skipped,
                "errors": errors,
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=500)
