from django.contrib import admin
from . import models

admin.site.register(models.UserFiles)
admin.site.register(models.Allergy)
admin.site.register(models.Medication)
admin.site.register(models.HealthProblem)
admin.site.register(models.LabReport)
admin.site.register(models.Imaging)
admin.site.register(models.Vaccination)
admin.site.register(models.Medication2)
admin.site.register(models.MedicationReminder)
admin.site.register(models.Conversation)
admin.site.register(models.Message)
