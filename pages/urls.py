from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'allergies', AllergyViewSet, basename='allergy')
router.register(r'health-problems', HealthProblemViewSet, basename='healthproblem')
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'lab-reports', LabReportViewSet, basename='labreport')
router.register(r'imaging', ImagingViewSet, basename='imaging')
router.register(r'vaccinations', VaccinationViewSet, basename='vaccination')
router.register(r'user-files', UserFilesViewSet, basename='userfiles')
router.register(r'medications2', MedicationViewSet, basename='medication2')
router.register(r'medication-reminders', MedicationReminderViewSet, basename='medicationreminder')
router.register(r'conversation', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('api/files/', include(router.urls)),
]