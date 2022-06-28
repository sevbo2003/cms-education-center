import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        #Google recaptcha
        captcha_token = request.POST.get('g-recaptcha-response')
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        data = {
            'secret': captcha_key,
            'response': captcha_token
        }
        # Make request
        try:
            captcha_server = requests.post(url=captcha_url, data=data)
            response = json.loads(captcha_server.text)
            if response['success'] == False:
                messages.error(request, "Iltimos captchani tering")
                return redirect('/')
        except:
            messages.error(request, "Boshqatdan urinib ko'ring")
            return redirect('/')
        
        #Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "email yoki parol xato")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None
