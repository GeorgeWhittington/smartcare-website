# Generated by Django 5.0.2 on 2024-02-28 14:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True)),
                ('time_slot', models.IntegerField(choices=[(0, 'EARLY_MORNING'), (1, 'LATE_MORNING'), (2, 'EARLY_AFTERNOON'), (3, 'LATE_AFTERNOON')])),
                ('assigned_start_time', models.DateTimeField(null=True)),
                ('actual_start_time', models.DateTimeField(null=True)),
                ('actual_end_time', models.DateTimeField(null=True)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_patient', to=settings.AUTH_USER_MODEL)),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_staff', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_repeating', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='smartcare_appointments.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_time', models.DateTimeField(null=True)),
                ('approved_time', models.DateTimeField(null=True)),
                ('collected', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('prescription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='smartcare_appointments.prescription')),
            ],
        ),
    ]
