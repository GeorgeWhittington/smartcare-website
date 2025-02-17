from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from datetime import datetime,date,timedelta
from django.db.models import Q

from smartcare_auth.models import StaffInfo
from smartcare_appointments.models import Appointment, TimeOff, AppointmentStage

def scheduler(appointment, user_override=None, date_override=None, time_override=None):
    # try to do prefered staff first first
    if not user_override and appointment.staff_preference:
        res = False
        si = StaffInfo.objects.filter(user=appointment.staff_preference).first()
        if si:
            res = scheduler(appointment, si, date_override, time_override)
            if res:
                return True

        
    print("STARTED SCHEDULING")
    dateRequested = appointment.date_requested

    if date_override:
        dateRequested = date_override

    timeRequested = appointment.time_preference

    if time_override:
        timeRequested = time_override

    
    #returns the staff available on the requested date
    availableStaff = []

    if user_override is not None:
        availableStaff = [user_override]
    else:
        availableStaff = get_staff_working_on_date(dateRequested)
    
    print("AVAILABLE STAFF",availableStaff)
    print("DATE Requested", dateRequested)
    for staff in availableStaff:
        availableSlot = staff_get_available_slot(staff,dateRequested,timeRequested,True)

        if availableSlot is not None:
            print("CHOSEN DETAILS: ", staff, availableSlot)
            appointmentScheduled = schedule_appointment(staff, availableSlot,appointment,dateRequested)
            if appointmentScheduled:
                ("APPOINTMENT SCHEDULED")
                return True

    return False


# schedule the appointment using the chosen staff and slot
def schedule_appointment(staff, slot, appointment,dateRequested):
    try:
        slot_start_str = settings.SLOTS[slot]['start']
        slot_start_time = datetime.strptime(slot_start_str, '%H:%M:%S').time()
        slot_start_datetime_local = datetime.combine(dateRequested, slot_start_time, ZoneInfo(settings.CLINIC_TIME_ZONE))

        appointment.slot_number = slot
        appointment.staff = staff.user
        appointment.stage = AppointmentStage.SCHEDULED
        appointment.assigned_start_time = slot_start_datetime_local
        appointment.save()
        return True
    except Exception as e:
        print(e)
        return False


# handles appointments affected by unplanned leave: tries to reschedule
def handle_affected_appointments(affected_appointments):
    for appointment in affected_appointments:
        rescheduled = scheduler(appointment)
        if not rescheduled:
            print("APPOINTMENT ", appointment, " CANCELLED")
            appointment.stage = 3
            appointment.staff = None
            appointment.slot_number = -1
            appointment.assigned_start_time = None
            appointment.save()

# find the staff who are working on the chosen day and are not on time off
def get_staff_working_on_date(date):
    dateToDay = date.strftime("%A")
    print("Query Date:", date)
    print("Day of Week:", dateToDay)

    conflicting_holidays = TimeOff.objects.filter(start_date__lte=date, end_date__gte=date).only("id").all()
    print(f"conflicting holiday: {conflicting_holidays}")

    availableStaff = StaffInfo.objects.filter(
        working_days__day=dateToDay,
        user__is_active=True
    ).exclude(
        timeOff__id__in=conflicting_holidays,
        user__is_active=False
    )
    print("AVAILABLE STAFF: ", availableStaff)
    return availableStaff

def staff_get_available_slot(staff,date,timePreference,timeCheck):
    # gets the appointments a doctor already has for date
    appointmentSlotNumbers = staff_get_appointments(staff,date)

    #stores available slots
    availableSlotNumbers = []

    print("THE APP DAY", date)
    if len(appointmentSlotNumbers) >= len(settings.SLOTS)-4:
        return False
    else:
        for slot in settings.SLOTS:
            if slot in settings.BREAK_SLOTS:
                continue
            elif slot in appointmentSlotNumbers:
                continue
            else:
                availableSlotNumbers.append(slot)

    if timePreference != 0:
        availableSlotNumbers = list(reversed(availableSlotNumbers))

    if timeCheck:
        now = datetime.now(tz=ZoneInfo(settings.CLINIC_TIME_ZONE))

        if now.date() == date:
            convertedTime = datetime.strptime(now.strftime("%H:%M:%S"), '%H:%M:%S').time()
            for availableSlot in availableSlotNumbers:
                slotStartTime = settings.SLOTS[availableSlot]['start']
                convertedSlotTime = datetime.strptime(slotStartTime, '%H:%M:%S').time()
                if convertedTime < convertedSlotTime:
                    return availableSlot
    else:
        return availableSlotNumbers[0] if availableSlotNumbers else False


# gets a staff member's appointments
def staff_get_appointments(staff,date):

    staffHasAppointments = Appointment.objects.filter(
        staff = staff.user,
        assigned_start_time__date = date
    )

    appointmentSlotNumbers = {appointment.slot_number for appointment in staffHasAppointments}

    return appointmentSlotNumbers



def checkSlotsInRange(startDate,endDate):
    
    result = {}
    while startDate <= endDate:
        morningAvailable = False
        eveningAvailable = False
        availableStaff = get_staff_working_on_date(startDate)

        for staff in availableStaff:
            slots =[]
            morningSlot = staff_get_available_slot(staff,startDate,0,False)
            eveningSlot = staff_get_available_slot(staff,startDate,1,False)
            if morningSlot is not None and eveningSlot is not None:
                
                slots.append(morningSlot)
                slots.append(eveningSlot)
                for slot in slots:
                    slotStartTime = settings.SLOTS[slot]['start']
                    convertedSlotTime = datetime.strptime(slotStartTime, '%H:%M:%S').time()
                    eveningCutoffTime = datetime.strptime('12:00:00', '%H:%M:%S').time()
                    if convertedSlotTime <= eveningCutoffTime:
                        morningAvailable = True
                        
                    else:
                        eveningAvailable = True
                    date = startDate.strftime("%Y-%m-%d")
                    result[date] = [morningAvailable,eveningAvailable]

        
        startDate = startDate + timedelta(days=1)

    return result    