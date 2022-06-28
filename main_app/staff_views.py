import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(subject__staff=staff).count()
    students_in_queue = Student.objects.filter(in_queue=True).filter(subject__staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'O\'qituvchi - ' + str(staff.admin.first_name),
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_subject': total_subject,
        'students_in_queue': students_in_queue,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Davomat olish'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            subject_id=subject.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        attendance = Attendance(session=session, subject=subject, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            student.coming_days_count += 1
            student.save()
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Davomatni yangilash'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")



def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'Profilni yangilash'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                phone_number = form.cleaned_data.get('phone_number')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.phone_number = phone_number
                admin.address = address
                admin.save()
                staff.save()
                messages.success(request, "Profil yangilandi!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Xato ma'lumot kiritildi")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Profilni yangilashda xatolik yuz berdi " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


