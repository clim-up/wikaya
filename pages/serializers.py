from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import Allergy, HealthProblem, Medication, LabReport, Imaging, Vaccination, UserFiles, Medication2, MedicationReminder, Conversation, Message
import re

class UserFilesSerializer(serializers.ModelSerializer):
    body_mass_index = serializers.SerializerMethodField()
    body_surface_area = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFiles
        fields = '__all__'
        read_only_fields = (
            'user', 
            'created_at', 
            'body_mass_index', 
            'body_surface_area'
        )
        
    def get_body_mass_index(self, obj):
        return obj.body_mass_index
        
    def get_body_surface_area(self, obj):
        return obj.body_surface_area
        
    def validate_blood_pressure(self, value):
        if value and not re.match(r'^\d{1,3}/\d{1,3}$', value):
            raise serializers.ValidationError(
                "Blood pressure must be in format '120/80'"
            )
        return value
        
    def validate(self, data):
        # Validate height/weight relationship if both provided
        if data.get('height') and data.get('weight'):
            if data['height'] < 50 or data['height'] > 300:
                raise ValidationError("Height must be between 50-300 cm")
            if data['weight'] < 2 or data['weight'] > 500:
                raise ValidationError("Weight must be between 2-500 kg")
        return data


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data

class HealthProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProblem
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
        extra_kwargs = {
            'file': {'required': True}
        }

class ImagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imaging
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
        extra_kwargs = {
            'file': {'required': True}
        }

class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class MedicationReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationReminder
        fields = '__all__'
        read_only_fields = ('created_at',)

class Medication2Serializer(serializers.ModelSerializer):
    reminders = MedicationReminderSerializer(many=True, read_only=True)
    
    class Meta:
        model = Medication2
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    patient = serializers.StringRelatedField()
    doctor = serializers.StringRelatedField()

    class Meta:
        model = Conversation
        fields = ['id', 'patient', 'doctor', 'created_at', 'messages']
        read_only_fields = ['created_at']

