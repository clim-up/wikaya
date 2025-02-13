from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Allergy, HealthProblem, Medication, LabReport, Imaging, Vaccination, UserFiles, BaseMedicalModel
from .serializers import AllergySerializer, HealthProblemSerializer, MedicationSerializer, LabReportSerializer, ImagingSerializer, VaccinationSerializer, UserFilesSerializer

class BaseMedicalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserFilesViewSet(BaseMedicalViewSet):
    queryset = UserFiles.objects.all()
    serializer_class = UserFilesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class AllergyViewSet(BaseMedicalViewSet):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class HealthProblemViewSet(BaseMedicalViewSet):
    queryset = HealthProblem.objects.all()
    serializer_class = HealthProblemSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class MedicationViewSet(BaseMedicalViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class LabReportViewSet(BaseMedicalViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class ImagingViewSet(BaseMedicalViewSet):
    queryset = Imaging.objects.all()
    serializer_class = ImagingSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

class VaccinationViewSet(BaseMedicalViewSet):
    queryset = Vaccination.objects.all()
    serializer_class = VaccinationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')