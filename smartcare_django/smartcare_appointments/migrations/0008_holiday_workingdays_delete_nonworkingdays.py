# Generated by Django 5.0.2 on 2024-03-29 11:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartcare_appointments', '0007_prescription_patient_prescription_staff_and_more'),
        ('smartcare_auth', '0011_staff_remove_user_employment_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holidays', to='smartcare_auth.staff')),
            ],
        ),
        migrations.CreateModel(
            name='WorkingDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=9)),
                ('is_active', models.BooleanField(default=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_days', to='smartcare_auth.staff')),
            ],
            options={
                'unique_together': {('staff', 'day')},
            },
        ),
        migrations.DeleteModel(
            name='NonWorkingDays',
        ),
    ]
