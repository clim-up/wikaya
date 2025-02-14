from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Allergy, HealthProblem, Medication, LabReport, Imaging, Vaccination, UserFiles, BaseMedicalModel, Medication2, MedicationReminder, Conversation, Message
from .serializers import AllergySerializer, HealthProblemSerializer, MedicationSerializer, LabReportSerializer, ImagingSerializer, VaccinationSerializer, UserFilesSerializer, Medication2Serializer, MedicationReminderSerializer, ConversationSerializer, MessageSerializer

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
    
class MedicationViewSet(viewsets.ModelViewSet):
    serializer_class = Medication2Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Medication2.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MedicationReminderViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MedicationReminder.objects.filter(
            medication__user=self.request.user
        )

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(patient=user) | Q(doctor=user)
        ).distinct()

    def perform_create(self, serializer):
        # Add validation to ensure user is creating conversation as patient
        serializer.save(patient=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__id=self.kwargs['conversation_id'],
            conversation__patient=self.request.user  # Or doctor
        )

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(id=self.kwargs['conversation_id'])
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )

