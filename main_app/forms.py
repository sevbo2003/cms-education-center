from django import forms
from django.forms.widgets import DateInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Ism")
    last_name = forms.CharField(required=True, label='Familiya')
    address = forms.CharField(required=True, label="Manzil")
    phone_number = forms.CharField(max_length=9, required=True, label="Telefon raqami")
    password = forms.CharField(widget=forms.PasswordInput, label='Parol')
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField(label="Rasm")

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password','profile_pic', 'address', 'phone_number' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        
    first_lesson_day = forms.DateField(widget=DateInput(attrs={'type': 'date' }), label="Birinchi dars kuni")
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Guruhi")
    session = forms.ModelChoiceField(queryset=Session.objects.all(), label="Dars kunlari")

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['subject', 'session','first_lesson_day']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    working_percentage = forms.IntegerField(label='Ishlash foizi')

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['working_percentage' ]


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    name = forms.CharField(required=True, label="Guruh nomi")
    staff = forms.ModelChoiceField(label="O'qituvchi", queryset=Staff.objects.all())
    price = forms.IntegerField(label="Kurs narxi")
    lessons_per_month = forms.IntegerField(label="1 oydagi darslar soni")

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'price', 'lessons_per_month']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    start_year = forms.DateField(widget=DateInput(attrs={'type': 'date' }), label="Boshlanish vaqti")
    end_year = forms.DateField(widget=DateInput(attrs={'type': 'date' }), label="Tugash vaqti")

    class Meta:
        model = Session
        fields = ['start_year', 'end_year']


class StudentPaymentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(StudentPaymentForm, self).__init__(*args, **kwargs)
    
    payment_amount = forms.IntegerField(label="To'lov summasi")
    payment_month = forms.ModelChoiceField(label="Ushbu oy uchun to'lov", queryset=PaymentDate.objects.all())
    class Meta:
        model = StudentPayment
        fields = ['payment_amount', 'payment_month']


class PaymentDateForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(PaymentDateForm, self).__init__(*args, **kwargs)
    
    year = forms.IntegerField(label="Yil")
    month = forms.ChoiceField(label="Oy", choices=MonthChoices.choices)
    class Meta:
        model = PaymentDate
        fields = ['year', 'month']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields
