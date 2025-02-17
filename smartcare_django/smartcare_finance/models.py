from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator

from smartcare_auth.models import PatientPayType
from smartcare_appointments.models import Appointment, AppointmentStage

# Hourly rate (move this to an actual table)
NURSE_RATE = 30.0
DOCTOR_RATE = 40.0


class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, null=False, on_delete=models.CASCADE, related_name="invoice_appointment")

    pay_type = models.PositiveSmallIntegerField(choices=PatientPayType.choices(), null=False, default=0)
    duration = models.DurationField(null=False)
    amount = models.FloatField(null=False, validators=[MinValueValidator(0.01)])
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)

    def staff(self):
        return self.appointment.staff

    def patient(self):
        return self.appointment.patient

    def is_paid(self):
        return self.paid_at is not None

    def due_date(self):
        return self.created_at + timedelta(weeks=4)

    def formatted_duration(self):
        return str(self.duration).split(".")[0]

    def fill_extra_fields(self):
        if not hasattr(self, "appointment") or self.appointment.stage != AppointmentStage.COMPLETED:
            raise ValidationError("An completed appointment must be provided")

        duration = self.appointment.actual_end_time - self.appointment.actual_start_time

        if not hasattr(self.appointment.staff, "staff_info") or not hasattr(self.appointment.staff.staff_info, "payrate"):
            raise ValidationError("Cannot create an invoice for a staff member without a payrate")

        if not hasattr(self.appointment.patient, "patient_info"):
            raise ValidationError("Cannot create an invoice for a patient without a payment type (ie private/nhs)")

        self.duration = duration
        self.amount = float(f"{duration.seconds / 3600 * self.appointment.staff.staff_info.payrate.rate:.2f}")
        self.pay_type = self.appointment.patient.patient_info.pay_type

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.fill_extra_fields()

        super(Invoice, self).save(*args, **kwargs)
