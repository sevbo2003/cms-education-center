from calendar import month
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify



class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return str(self.start_year) + " dan " + str(self.end_year) + " gacha"


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    profile_pic = models.ImageField()
    address = models.TextField()
    phone_number = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @property
    def get_number(self):
        num = self.phone_number
        result = num[:2] + "-" + num[2:5] + "-" + num[5:7] + "-" + num[7:]
        return result

    def __str__(self):
        return self.last_name + " " + self.first_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class MonthChoices(models.TextChoices):
    YANVAR = 1
    FEVRAL = 2
    MART = 3
    APREL = 4
    MAY = 5
    IYUN = 6
    IYUL = 7
    AVGUST = 8
    SENTABR = 9
    OKTABR = 10
    NOYABR = 11
    DEKABR = 12


class PaymentDate(models.Model):
    year = models.IntegerField(validators=[MinValueValidator(2022), MaxValueValidator(2025)])
    month = models.CharField(choices=MonthChoices.choices, max_length=10)
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.year) + self.month)
        super(PaymentDate, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.year) + " " + self.month




class StudentPayment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    payment_amount = models.IntegerField()
    payment_month = models.ForeignKey(PaymentDate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.student.admin.first_name + " " + self.student.admin.last_name + " " + str(self.created_at) + " " + str(self.payment_amount)


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.DO_NOTHING, null=True, blank=False)
    should_pay = models.IntegerField()
    first_lesson_day = models.DateField()
    coming_days_count = models.IntegerField(default=0)
    in_queue = models.BooleanField(default=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        try:
            if self.coming_days_count == self.subject.lessons_per_month:
                self.coming_days_count = 0
                self.should_pay += self.subject.price
        except:
            pass
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey('Staff',on_delete=models.CASCADE,)
    price = models.IntegerField()
    lessons_per_month = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    working_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    has_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_subjects(self):
        subjects = Subject.objects.filter(staff_id = self.id)
        return ', '.join([i.name for i in subjects])
    
    def get_full_name(self):
        return self.admin.first_name + " " + self.admin.last_name

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name

class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance, working_percentage = 0)
        if instance.user_type == 3:
            Student.objects.create(admin=instance, subject=None, should_pay=0, first_lesson_day='2022-09-12', in_queue=True, session=None)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
