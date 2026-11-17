from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager

class User(AbstractUser):

  ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
  )
    
  username = None

  email = models.EmailField(unique=True)
  role = models.CharField(max_length=10, choices=ROLE_CHOICES)

  verification_code = models.CharField(max_length=6, blank=True, null=True)
  verification_code_expires = models.DateTimeField(blank=True, null=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ["first_name", "last_name"]

  objects = CustomUserManager()

  def __str__(self):
    return self.email

class Student(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")

  admission_number = models.CharField(max_length=20, unique=True, blank=True)
  date_of_birth = models.DateField(null=True, blank=True)
  phone_number = models.CharField(max_length=20, blank=True)
  address = models.TextField(blank=True)

  def save(self, *args, **kwargs):
    if not self.admission_number:
      year = timezone.now().year
      prefix = f"LASOP{year}"

      last_student = (
        Student.objects.filter(admission_number__startswith=prefix).order_by("-admission_number").first()
      )

      if last_student:
        last_number = int(last_student.admission_number[len(prefix):])
        next_number = last_number + 1
      else:
        next_number = 1

      self.admission_number = f"{prefix}{next_number:04d}"

    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.user.first_name} {self.user.last_name} - {self.admission_number}"

class Teacher(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
  employee_number = models.CharField(max_length=20, unique=True, blank=True)
  phone_number = models.CharField(max_length=20, blank=True)
  address = models.TextField(blank=True)
  qualification = models.CharField(max_length=100, blank=True)
  date_joined = models.DateField(auto_now_add=True)

  def save(self, *args, **kwargs):
    if not self.employee_number:
      year = timezone.now().year
      prefix = f"TEACH{year}"

      last_teacher = (
        Teacher.objects.filter(employee_number__startswith=prefix).order_by("-employee_number").first()
      )

      if last_teacher:
        last_number = int(last_teacher.employee_number[len(prefix):])
        next_number = last_number + 1
      else:
        next_number = 1

      self.employee_number = f"{prefix}{next_number:04d}"

    super().save(*args, **kwargs)

  def __str__(self):
    return (
      f"{self.user.first_name}{self.user.last_name}"
      f" - {self.employee_number}"
    )

class SchoolClass(models.Model):
  name = models.CharField(max_length=50, unique=True)
  description = models.TextField(blank=True)
  class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="classled_led")

  def __str__(self):
    return self.name

class Subject(models.Model):
  name = models.CharField(max_length=100, unique=True)
  code = models.CharField(max_length=20, unique=True)
  school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
  teachers = models.ManyToManyField(Teacher, blank=True, related_name="subjects_taught")

  def __str__(self):
    return f"{self.name} - {self.school_class.name}"


class Enrollment(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
  school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="enrollments")
  academic_year = models.CharField(max_length=9)
  date_enrolled = models.DateField(auto_now_add=True)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["student", "academic_year"],
        name="unique_student_enrollment_per_year"
      )
    ]

  def __str__(self):
    return(
      f"{self.student.admission_number} - "
      f"{self.school_class.name} - {self.academic_year}"
    )


class Attendance(models.Model):
  STATUS_CHOICES = [
    ("present", "Present"),
    ("absent", "Absent"),
    ("late", "Late"),
  ]

  student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
  school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="attendance_records")
  date = models.DateField()
  status = models.CharField(max_length=10, choices=STATUS_CHOICES)
  remarks = models.CharField(max_length=255, blank=True)

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=["student", "date"], name="unique_student_attendance_per_day")
    ] 
    ordering = ["-date", "student"]

  def __str__(self):
    return f"{self.student} - {self.date} - {self.status}"

    
