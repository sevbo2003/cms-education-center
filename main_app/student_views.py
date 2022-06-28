import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    data_present = []
    data_absent = []
    subject = student.subject
    attendance = Attendance.objects.filter(subject__id=subject.id)
    present_count = AttendanceReport.objects.filter(
        attendance__in=attendance, status=True, student=student).count()
    absent_count = AttendanceReport.objects.filter(
        attendance__in=attendance, status=False, student=student).count()
    data_present.append(present_count)
    data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'subjects': subject,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject.name,
        'data_name_price': subject.price,
        'page_title': 'Ota onalar uchun',
        'student': student

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        context = {
            'subject': student.subject,
            'page_title': 'Davomatni ko\'rish'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


