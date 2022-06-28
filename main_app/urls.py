from django.urls import path

from . import hod_views, staff_views, student_views, views


urlpatterns = [
    path("", views.login_page, name="login_page"),
    path("get_attendance", views.get_attendance, name="get_attendance"),
    path("doLogin/", views.doLogin, name="user_login"),
    path("logout_user/", views.logout_user, name="user_logout"),
    path("admin/home/", hod_views.admin_home, name="admin_home"),
    path("admin/tolovlar/", hod_views.all_payments, name='all_payments'),
    path("admin/oylik-daromadlar/", hod_views.manage_profits, name="manage_profits"),
    path("admin/oylik-daromadlar/<str:payment_slug>/", hod_views.manage_profits_detail, name="manage_profits_detail"),
    path("admin/oylik-vaqt-qoshish/", hod_views.add_date, name="add_date"),
    path("staff/add", hod_views.add_staff, name="add_staff"),
    path("add_session/", hod_views.add_session, name="add_session"),
    path("check_email_availability",hod_views.check_email_availability,name="check_email_availability",),
    path("session/manage/", hod_views.manage_session, name="manage_session"),
    path("session/edit/<int:session_id>", hod_views.edit_session, name="edit_session"),
    path("attendance/view/",hod_views.admin_view_attendance,name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance, name="get_admin_attendance"),
    path("student/add/", hod_views.add_student, name="add_student"),
    path("subject/add/", hod_views.add_subject, name="add_subject"),
    path("staff/manage/", hod_views.manage_staff, name="manage_staff"),
    path("student/manage/", hod_views.manage_student, name="manage_student"),
    path("student/manage/in-queue/", hod_views.manage_student_in_queue, name="manage_student_in_queue"),
    path("subject/manage/", hod_views.manage_subject, name="manage_subject"),
    path("guruh-haqida/<int:subject_id>/", hod_views.subject_detail, name="subject_detail"),
    path("guruh/barcha-tolovlar/<int:subject_id>", hod_views.subjects_last_payments, name="subjects_last_payments"),
    path("staff/edit/<int:staff_id>/", hod_views.edit_staff, name="edit_staff"),
    path("staff/delete/<int:staff_id>", hod_views.delete_staff, name="delete_staff"),
    path("subject/delete/<int:subject_id>",hod_views.delete_subject,name="delete_subject",),
    path("session/delete/<int:session_id>",hod_views.delete_session,name="delete_session",),
    path("student/delete/<int:student_id>",hod_views.delete_student,name="delete_student",),
    path("student/payment/<int:student_id>", hod_views.student_payment,name="student_payment",),
    path("student/delete/<int:student_id>", hod_views.delete_student_in_queue,name="delete_student_in_queue",),
    path("student/edit/<int:student_id>", hod_views.edit_student, name="edit_student"),
    path("student/queue/<int:student_id>", hod_views.edit_student_in_queue, name="edit_student_in_queue"),
    path("subject/edit/<int:subject_id>", hod_views.edit_subject, name="edit_subject"),
    # Staff
    path("staff/home/", staff_views.staff_home, name="staff_home"),
    path("staff/view/profile/", staff_views.staff_view_profile, name="staff_view_profile"),
    path("staff/attendance/take/",staff_views.staff_take_attendance,name="staff_take_attendance",),
    path("staff/attendance/update/",staff_views.staff_update_attendance,name="staff_update_attendance",),
    path("staff/get_students/", staff_views.get_students, name="get_students"),
    path("staff/attendance/fetch/",staff_views.get_student_attendance,name="get_student_attendance",),
    path("staff/attendance/save/", staff_views.save_attendance, name="save_attendance"),
    path("staff/attendance/update/",staff_views.update_attendance,name="update_attendance",),


    # Student
    path("student/home/", student_views.student_home, name="student_home"),
    path("student/view/attendance/",student_views.student_view_attendance,name="student_view_attendance",),
]

