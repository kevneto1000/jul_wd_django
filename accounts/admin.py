from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher, SchoolClass, Subject, Enrollment, Attendance

@admin.register(User)
class CustomUserAdmin(UserAdmin):
  list_display = (
    'email',
    'role',
    'is_active',
    'is_staff',
    'date_joined',
  )

  list_filter = (
    'role',
    'is_active',
    'is_staff',
  )

  search_fields = (
    'email',
    'first_name',
    'last_name',
  )

  ordering = ('-date_joined',)

  fieldsets = (
    ("Login Information", {
      "fields": (
        "email",
        "password",
      )
    }),
    ("Personal Information", {
      "fields": (
        "first_name",
        "last_name",
      )
    }),
    ("School Role", {
      "fields": (
        "role",
      )
    }),
    ("Permissions", {
      "fields": (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
      )
    }),
    ("Important Dates", {
      "fields": (
        "last_login",
        "date_joined",
      )
    }),
  )

  add_fieldsets = (
    (None, {
      "classes": ("wide",),
      "fields": (
        "email",
        "password1",
        "password2",
        "role",
        "is_active",
        "is_staff",
      ),
    }),
  )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
  list_display = (
    "admission_number",
    "user",
    "phone_number",
  )

  search_fields = (
    "admission_number",
    "user__first_name",
    "user__last_name",
    "user__email",
  )

  list_filter = ("date_of_birth",)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
  list_display = (
    "employee_number",
    "user",
    "qualification",
    "date_joined",
  )

  search_fields = (
    "employee_number",
    "user__first_name",
    "user__last_name",
    "user__email",
  )

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
  list_display = ("name", "class_teacher")
  search_fields = ("name",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
  list_display = ("name", "code", "school_class")
  list_filter = ("school_class",)
  search_fields = ("name", "code")
  filter_horizontal = ("teachers",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
  list_display = (
    "student",
    "school_class",
    "academic_year",
    "date_enrolled",
  )
  list_filter = ("academic_year", "school_class")
  search_fields = (
    "student__admission_year",
    "student__user__first_name",
    "student__user__last_name",
  )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
  list_display = (
    "student",
    "school_class",
    "date",
    "status",
  )
  list_filter = ("date", "status", "school_class")
  search_fields = (
    "student__admission_number",
    "student__user__first_name",
    "student__user__last_name",
  )
  date_hierarchy = "date"
  