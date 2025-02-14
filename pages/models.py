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
    notes = models.TextField(null=True, blank=True)
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

class Medication2(models.Model):
    TIMING_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='medications'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Medication Name'
    )
    dosage = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Capsule'
    )
    duration_days = models.PositiveIntegerField(
        verbose_name='Duration (days)',
        help_text='Treatment duration in days'
    )
    timing = models.CharField(
        max_length=10,
        choices=TIMING_CHOICES,
        verbose_name='Administration Time'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medication2'
        verbose_name_plural = 'Medications2'

    def __str__(self):
        return f"{self.name} - {self.get_timing_display()}"

class MedicationReminder(models.Model):
    medication = models.ForeignKey(
        Medication2,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_time = models.TimeField(
        verbose_name='Reminder Time'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Reminder'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reminder_time']
        verbose_name = 'Medication Reminder'
        verbose_name_plural = 'Medication Reminders'

    def __str__(self):
        return f"{self.medication} at {self.reminder_time.strftime('%H:%M')}"

class Conversation(models.Model):
    patient = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='patient_conversations'
    )
    doctor = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='doctor_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        unique_together = ['patient', 'doctor']  # Prevent duplicate conversations

    def __str__(self):
        return f"Conversation between {self.patient} and {self.doctor}"

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"

