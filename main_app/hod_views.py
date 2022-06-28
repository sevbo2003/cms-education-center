import json
from re import sub
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from datetime import date
from django.db.models import Sum, Avg

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.filter(in_queue=False).count()
    in_queue_students = Student.objects.filter(in_queue=True).count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    payment_dates = PaymentDate.objects.all()[:4]
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)
    context = {
        'page_title': "Administorlar uchun",
        'total_students': total_students,
        'in_queue_students': in_queue_students,
        'total_staff': total_staff,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'payment_dates': payment_dates

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'O\'qituvchi qo\'shish'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            passport = request.FILES.get('profile_pic')
            working_percentage = form.cleaned_data.get('working_percentage')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.address = address
                user.phone_number = phone_number
                user.staff.working_percentage = working_percentage
                user.save()
                messages.success(request, "Muvaffaqiyatli qo'shildi")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Iltimos barcha ma'lumotlarni to'ldiring")

    return render(request, 'hod_template/add_staff_template.html', context)


def all_payments(request):
    last_payments = StudentPayment.objects.all().order_by('-created_at')
    context = {
        'last_payments': last_payments,
        'page_title': 'Barcha to\'lovlar'
    }
    return render(request, 'hod_template/all_payments.html', context)

def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'O\'quvchi qo\'shish'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            phone_number = student_form.cleaned_data.get('phone_number')
            email = student_form.cleaned_data.get('email')
            first_lesson_day = student_form.cleaned_data.get('first_lesson_day')
            password = student_form.cleaned_data.get('password')
            subject= student_form.cleaned_data.get('subject')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.address = address
                user.phone_number = phone_number
                user.student.session = session
                user.student.subject = subject
                user.student.in_queue = True
                user.student.first_lesson_day = first_lesson_day
                user.student.should_pay = Subject.objects.get(id=subject.id).price
                user.save()
                messages.success(request, "O'quvchi qo'shildi")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Xatolik: " + str(e))
        else:
            messages.error(request, "Xatolik: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Guruh qo\'shish'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            staff = form.cleaned_data.get('staff')
            price = form.cleaned_data.get('price')
            lessons_per_month = form.cleaned_data.get('lessons_per_month')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.price = price
                subject.lessons_per_month = lessons_per_month
                subject.save()
                messages.success(request, "Guruh qo'shildi")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Xatolik " + str(e))
        else:
            messages.error(request, "Barcha ma'lumotlarni to'ldiring")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': "O'qituvchilar"
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3).filter(student__in_queue=False).order_by('-updated_at')
    context = {
        'students': students,
        'page_title': 'O\'quvchilar'
    }
    return render(request, "hod_template/manage_student.html", context)

def manage_student_in_queue(request):
    students = CustomUser.objects.filter(user_type=3).filter(student__in_queue=True).order_by('student__first_lesson_day')
    context = {
        'students': students,
        'page_title': 'Darsga yozilganlar'
    }
    return render(request, "hod_template/manage_student_in_queue.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Guruhlar'
    }
    return render(request, "hod_template/manage_subject.html", context)

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(subject=subject).filter(in_queue=False).order_by('-updated_at')
    last_payments = StudentPayment.objects.filter(student__subject=subject).order_by('-created_at')[:4]
    total_payment = StudentPayment.objects.filter(payment_month__slug='2022iyun').filter(student__subject=subject_id).aggregate(Sum('payment_amount'))['payment_amount__sum']
    try:
        for_teacher = total_payment * subject.staff.working_percentage / 100
    except:
        for_teacher = 0
    context = {
        'subject': subject,
        'page_title': 'Guruh: ' + subject.name,
        'students': students,
        'total_payment': total_payment,
        'for_teacher': for_teacher,
        'last_payments': last_payments
    }
    return render(request, "hod_template/subject_detail.html", context)

def manage_profits(request):
    payment_dates = PaymentDate.objects.all()
    context = {
        'payment_dates': payment_dates,
        'page_title': 'Daromadlar'
    }
    return render(request, "hod_template/manage_profits.html", context)

def manage_profits_detail(request, payment_slug):
    payment_date = get_object_or_404(PaymentDate, slug=payment_slug)
    subjects = Subject.objects.all().order_by('-updated_at')
    total_month_profit = StudentPayment.objects.filter(payment_month__slug=payment_slug).aggregate(Sum('payment_amount'))['payment_amount__sum']

    context = {
        'payment_date': payment_date,
        'page_title': payment_date,
        'groups': subjects,
        'total_month_profit': total_month_profit,
    }
    return render(request, "hod_template/manage_profit_detail.html", context)


def subjects_last_payments(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    last_payments = StudentPayment.objects.filter(student__subject=subject).order_by('-created_at')
    context = {
        'last_payments': last_payments,
        'subject': subject,
        'page_title': f"Barcha to'lovlar: {subject.name}"
    }
    return render(request, 'hod_template/subject_last_payments.html', context)


def student_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payment_form = StudentPaymentForm(request.POST or None)
    context = {
        'student': student,
        'page_title': 'O\'quvchi: ' + student.admin.first_name + ' ' + student.admin.last_name + f', to\'lashi kerak: {student.should_pay} ',
        'form': payment_form
    }
    if request.method == 'POST':
        if payment_form.is_valid():
            price = student.should_pay - payment_form.cleaned_data.get('payment_amount')
            student.should_pay = price
            student.save()
            payment = StudentPayment()
            payment.student = student
            payment.payment_amount = payment_form.cleaned_data.get('payment_amount')
            payment.payment_month = payment_form.cleaned_data.get('payment_month')
            payment.save()
            messages.success(request, "Muvaffaqiyatli to'landi")
            return redirect(reverse('subject_detail', args=(student.subject.id,)))
        else:
            messages.error(request, "Xatolik yuz berdi")
            return redirect(reverse('student_payment', args=(student.id,)))
    
    return render(request, "hod_template/student_payment.html", context)

def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'O\'zgartirish'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            working_percentage = form.cleaned_data.get('working_percentage')
            password = form.cleaned_data.get('password') or None
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name

                user.last_name = last_name
                user.address = address
                user.phone_number = phone_number
                staff.working_percentage = working_percentage
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'O\'zgartirish'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password') or None
            subject = form.cleaned_data.get('subject')
            first_lesson_day = form.cleaned_data.get('first_lesson_day')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.address = address
                user.phone_number = phone_number
                student.subject = subject
                student.first_lesson_day = first_lesson_day
                student.in_queue = False
                user.save()
                student.save()
                messages.success(request, "Muvaffaqiyatli o'zgartirildi")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Xatolik yuz berdi " + str(e))
        else:
            messages.error(request, "Xatolik yuz berdi!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_student_in_queue(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.in_queue = False
    student.save()
    messages.success(request, "O'quvchi darsga keldi")
    return redirect(reverse('manage_student_in_queue'))

def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Guruhni yangilash'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            staff = form.cleaned_data.get('staff')
            price = form.cleaned_data.get('price')
            lessons_per_month = form.cleaned_data.get('lessons_per_month')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.price = price
                subject.lessons_per_month = lessons_per_month
                subject.save()
                messages.success(request, "Muvaffaqiyatli o'zgartirildi")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Xatolik " + str(e))
        else:
            messages.error(request, "Xatolik")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Dars vaqtini qo\'shish'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Muvaffaqiyatli yaratildi")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Xatolik ' + str(e))
        else:
            messages.error(request, 'Xatolik ')
    return render(request, "hod_template/add_session_template.html", context)


def add_date(request):
    form = PaymentDateForm(request.POST or None)
    context = {'form': form, 'page_title': 'Oylik vaqt qo\'shish'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                year = form.cleaned_data.get('year')
                month = int(form.cleaned_data.get('month'))
                print(type(year), type(month))
                payment = PaymentDate()
                payment.year = year
                payment.month = MonthChoices.choices[month-1][1]
                payment.save()
                messages.success(request, "Muvaffaqiyatli yaratildi")
                return redirect(reverse('admin_home'))
            except Exception as e:
                messages.error(request, 'Xatolik ' + str(e))
        else:
            messages.error(request, 'Xatolik ')
    return render(request, "hod_template/add_date_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Barcha dars vaqtlari'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Dars vaqtini o\'zgartirish'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)






def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Davomatni ko\'rish'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "O'qituvchi ro'yxatdan o'chirildi!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "O'quvchi ro'yxatdan olib tashlandi")
    return redirect(reverse('manage_student'))

def delete_student_in_queue(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "O'quvchi o'chirildi!")
    return redirect(reverse('manage_student_in_queue'))

def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Guruh yopildi!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Dars vaqti o'chirildi!")
    except Exception:
        messages.error(
            request, "Bu vaqtga yozilgan o'quvchilar mavjud. Iltimos o'quvchilarni boshqa vaqtga ko'chiring")
    return redirect(reverse('manage_session'))
