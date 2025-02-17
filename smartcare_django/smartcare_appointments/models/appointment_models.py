from django.conf import settings
from django.db import models
from django.utils import timezone

from enum import IntEnum

class TimeSlot(IntEnum):
    # 8:00 - 9:59
    EARLY_MORNING = 0
    # 10:00 - 11:59
    LATE_MORNING = 1
    # 12:00 - 14:59
    EARLY_AFTERNOON = 2
    # 15:00 - 18:00
    LATE_AFTERNOON = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class AppointmentStage(IntEnum):
    REQUESTED = 0
    APPROVED = 1
    SCHEDULED = 2
    COMPLETED = 3
    CANCELLED = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class AppointmentPayee(IntEnum):
    PATIENT = 0
    NHS = 1

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='appointment_patient')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='appointment_staff')
    date_created = models.DateTimeField(null=False, auto_now=True)

     # stage of the appointment
    stage = models.IntegerField(choices=AppointmentStage.choices(), null=False, default=AppointmentStage.REQUESTED)

    date_requested = models.DateField(null=False, default=timezone.now)

    # symptoms - reason for appointment, filled out by patient
    symptoms = models.TextField(blank=True, null=False, default='')

    # symptom duration (measured in days) - filled out by patient
    symptom_duration = models.IntegerField(null=False, default=1)

    # preferred time that the patient would like this appointment e.g morning / afternoon
    time_preference = models.IntegerField(choices=TimeSlot.choices(), null=False)

    # preferred staff member for appointment, if null there is no preference
    staff_preference = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="appointment_preferred_staff")

    # actual appointment slot
    slot_number = models.IntegerField(default=-1)

    # time that the staff has assigned based on time slot
    assigned_start_time = models.DateTimeField(null=True)

    # time that the appointment actually took place
    actual_start_time = models.DateTimeField(null=True)
    actual_end_time = models.DateTimeField(null=True)

    # TODO: can be removed
    paid_by = models.IntegerField(choices=AppointmentPayee.choices(), null=True, default=None)

    def __str__(self):
        return f"Appointment {self.id}"

class AppointmentComment(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now=True)
    text = models.TextField(max_length=1024)
    appointment = models.ForeignKey(Appointment, null=False, on_delete=models.CASCADE, related_name='appointment_comments')