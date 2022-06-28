from atexit import register
from django import template
from main_app.models import PaymentDate, StudentPayment, Staff, Student, Subject
from django.db.models import Sum, Avg

register = template.Library()

@register.filter(name='get_student_payments')
def get_student_payments(slug):
    return StudentPayment.objects.filter(payment_month__slug=slug).aggregate(Sum('payment_amount'))['payment_amount__sum']


@register.simple_tag(name='get_total_group_profit')
def get_total_group_profit(slug, group):
    return StudentPayment.objects.filter(payment_month__slug=slug).filter(student__subject=group).aggregate(Sum('payment_amount'))['payment_amount__sum']

@register.simple_tag(name='get_total_group_teacher_profite')
def get_total_group_teacher_profite(slug, group, percentage):
    try:
        return StudentPayment.objects.filter(payment_month__slug=slug).filter(student__subject=group).aggregate(Sum('payment_amount'))['payment_amount__sum'] * percentage / 100
    except:
        return 0
        
@register.simple_tag(name="get_total_group_center_profite")
def get_total_group_center_profite(slug, group, percentage):
    percent = 100-percentage
    try:
        return StudentPayment.objects.filter(payment_month__slug=slug).filter(student__subject=group).aggregate(Sum('payment_amount'))['payment_amount__sum'] * percent / 100
    except:
        return 0

@register.simple_tag(name='get_total_month_profit')
def get_total_month_profit(slug):
    return StudentPayment.objects.filter(payment_month__slug=slug).aggregate(Sum('payment_amount'))['payment_amount__sum']



@register.filter(name="get_teachers_percentage")
def get_teachers_percentage(slug):
    teachers = list(set([i.student.subject.staff for i in StudentPayment.objects.filter(payment_month__slug=slug)]))
    teachers_percentage = sum([teacher.working_percentage for teacher in teachers])
    if len(teachers) != 0:
        return teachers_percentage / len(teachers) / 100
    return teachers_percentage / len(teachers) / 100

@register.filter(name="get_teachers_percentage2")
def get_teachers_percentage2(slug):
    teachers = list(set([i.student.subject.staff for i in StudentPayment.objects.filter(payment_month__slug=slug)]))
    teachers_percentage = sum([teacher.working_percentage for teacher in teachers])
    return round(teachers_percentage / len(teachers), 2)


@register.filter(name='get_teachers_payments')
def get_teachers_payments(slug):
    total = 0
    for i in Subject.objects.all():
        total_group = StudentPayment.objects.filter(payment_month__slug=slug).filter(student__subject=i.id).aggregate(Sum('payment_amount'))['payment_amount__sum']
        try:
            for_teacher = total_group * i.staff.working_percentage / 100
        except:
            for_teacher = 0
        total += for_teacher
    return total

@register.filter(name='get_center_payments')
def get_center_payments(slug):
    total = 0
    for i in Subject.objects.all():
        try:
            total_group = StudentPayment.objects.filter(payment_month__slug=slug).filter(student__subject=i.id).aggregate(Sum('payment_amount'))['payment_amount__sum']
            try:
                for_teacher = total_group * i.staff.working_percentage / 100
            except:
                for_teacher = 0
            total += total_group - for_teacher
        except:
            total += 0
    return total


@register.filter(name='get_students_count')
def get_students_count(group):
    return group.student_set.filter(in_queue=False).count()