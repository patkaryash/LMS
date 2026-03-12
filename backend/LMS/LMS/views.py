from rest_framework import generics, permissions
from .serializers import UserSerializer
from labs.models import User

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows anyone to create a new user account.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from labs.importers import import_labs, import_pcs, import_lab_equipment


class BulkImportAPIView(APIView):
    """
    POST multipart/form-data:
      - file: CSV or XLSX
      - entity: labs | pcs | equipment

    Requires JWT auth.
    Only admin users can import.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Role check (your custom User model)
        if not hasattr(user, "role") or user.role != "admin":
            return Response(
                {"detail": "Only admin users can perform bulk import."},
                status=status.HTTP_403_FORBIDDEN,
            )

        file = request.FILES.get("file")
        entity = request.data.get("entity")

        if not file or not entity:
            return Response(
                {"detail": "Both 'file' and 'entity' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if entity == "labs":
                created, skipped, errors = import_labs(file)
            elif entity == "pcs":
                created, skipped, errors = import_pcs(file)
            elif entity == "lab-equipment":
                created, skipped, errors = import_lab_equipment(file)
            else:
                return Response(
                    {"detail": "Invalid entity. Use labs | pcs | lab-equipment."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "status": "success",
                    "entity": entity,
                    "created": created,
                    "skipped": skipped,
                    "errors": errors,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
# TEMPORARY browser test UI (no DRF)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from labs.importers import import_pcs
from labs.models import Lab
@login_required
def bulk_import_test_ui(request):
    result = None
    labs = Lab.objects.all()

    if request.method == "POST":
        file = request.FILES.get("file")
        entity = request.POST.get("entity")
        lab_id = request.POST.get("lab_id") or None

        if not file or not entity:
            result = {"error": "File and entity are required"}
        else:
            try:
                if entity == "pcs":
                    result = import_pcs(file, lab_id=lab_id)
                else:
                    result = {"error": "Only PCs import supported for this Excel"}
            except Exception as e:
                result = {"error": str(e)}

    return render(request, "labs/bulk_import_test.html", {"result": result, "labs": labs})

