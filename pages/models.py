from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

class UserFiles(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='user_file'
    )
    heart_rate = models.PositiveIntegerField(
        default=72,  # Average resting heart rate
        verbose_name='Heart Rate'
    )
    blood_pressure = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name='Blood Pressure'
    )  # Stores values like "120/80"
    weight = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Weight (kg)'
    )
    height = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Height (cm)'
    )
    blood_sugar_level = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Blood Sugar Level (mg/dL)',
        default=90  # Typical fasting blood sugar level
    )
    oxygen_saturation = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=98,
        verbose_name='Oxygen Saturation (%)'
    )
    respiratory_rate = models.PositiveIntegerField(
        default=16,  # Normal adult respiratory rate
        verbose_name='Respiratory Rate (breaths/min)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def body_mass_index(self):
        """Calculate BMI using weight (kg) and height (m)"""
        if self.height and self.weight:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 1)
        return None

    @property
    def body_surface_area(self):
        """Calculate BSA using Mosteller formula (m²)"""
        if self.height and self.weight:
            return round(((self.height * self.weight) / 3600) ** 0.5, 2)
        return None

    class Meta:
        db_table = 'user_files'
        ordering = ['-created_at']
        verbose_name = 'User Health File'
        verbose_name_plural = 'User Health Files'

    def __str__(self):
        return f"Health Data for {self.user.email} - {self.created_at}"
    
class BaseMedicalModel(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)s_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Allergy(BaseMedicalModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Manual override to mark as past. Leave empty for auto-calculation"
    )

    @property
    def calculated_is_passed(self):
        """Auto-determine status based on end date"""
        if self.end_date:
            from django.utils import timezone
            return self.end_date < timezone.now().date()
        return False

    @property
    def effective_is_passed(self):
        """Use manual setting if exists, else auto-calculation"""
        return self.is_passed if self.is_passed is not None else self.calculated_is_passed

    def __str__(self):
        status = "Past" if self.effective_is_passed else "Current"
        return f"{status} Allergy: {self.title}"

class Medication(BaseMedicalModel):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    is_passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Manual override to mark as past. Leave empty for auto-calculation"
    )

    @property
    def calculated_is_passed(self):
        """Auto-determine status based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.end_date and self.end_date < today:
            return True
        if self.start_date and self.start_date > today:
            return True
        return False

    @property
    def effective_is_passed(self):
        return self.is_passed if self.is_passed is not None else self.calculated_is_passed

    def __str__(self):
        status = "Past" if self.effective_is_passed else "Current"
        return f"{status} Medication: {self.name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='end_after_start'
            )
        ]

class HealthProblem(BaseMedicalModel):
    title = models.CharField(max_length=100)
    diagnosis_date = models.DateField(blank=True, null=True)
    resolved = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class LabReport(BaseMedicalModel):
    file = models.FileField(
        upload_to='lab_reports/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']),
            # Add file size validator in your settings
        ]
    )
    report_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Lab Report - {self.report_date}"

class Imaging(BaseMedicalModel):
    file = models.FileField(
        upload_to='imaging/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['dicom', 'pdf', 'jpg', 'jpeg', 'png']),
            # Add file size validator
        ]
    )
    imaging_date = models.DateField()
    imaging_type = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Imaging - {self.imaging_type} ({self.imaging_date})"

class Vaccination(BaseMedicalModel):
    name = models.CharField(max_length=100)
    date_administered = models.DateField()
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    lot_number = models.CharField(max_length=50, blank=True, null=True)
    next_dose_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.date_administered}"

