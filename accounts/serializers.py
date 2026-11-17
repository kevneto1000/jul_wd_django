from datetime import timedelta
import secrets

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import serializers
from .models import User, Student, Teacher, SchoolClass, Subject, Enrollment, Attendance

class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8)

  class Meta:
    model = User
    fields = [
      "email",
      "password",
      "first_name",
      "last_name",
      "role",
    ]

  def create(self, validated_data):
    # verification_code = str(secrets.randbelow(900000) + 100000)

    user = User.objects.create_user(
      email=validated_data["email"],
      password=validated_data["password"],
      first_name=validated_data["first_name"],
      last_name=validated_data["last_name"],
      role=validated_data["role"],
    )

    # user.is_active = False

    # user.verification_code = verification_code

    # user.verification_code_expires = (
    #   timezone.now() + timedelta(minutes=10)
    # )

    user.save()

    '''
    html_content = render_to_string(
      "emails/verification_email.html",
      {
        "user": user,
        "verification_code": verification_code,
      }
    )

    email = EmailMultiAlternatives(
      subject="Verify your account",
      body=(
        f"Hello {user.first_name},"
        f"your verification code is {verification_code}."
        "It expires in 10 minutes"
      ),
      from_email=settings.DEFAULT_FROM_EMAIL,
      to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
    '''

    return user
  
'''
class VerifyEmailSerializer(serializers.Serializer):
  email = serializers.EmailField()

  verification_code = serializers.CharField(max_length=6, min_length=6)

  def validate(self, attrs):
    email = attrs["email"]
    verification_code = attrs["verification_code"]

    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      raise serializers.ValidationError("User not found")

    if user.is_active:
      raise serializers.ValidationError("Email is already verified")

    if verification_code != user.verification_code:
      raise serializers.ValidationError("Invalid verification code")

    if (not user.verification_code_expires or timezone.now() > user.verification_code_expires):
      raise serializers.ValidationError("Verification code has expired")

    attrs["user"] = user

    return attrs

  def save(self):
    user = self.validated_data["user"]

    user.is_active = True

    user.verification_code = None
    user.verification_code_expires = None

    user.save()

    return user

class ResendOTPSerializer(serializers.Serializer):
  email = serializers.EmailField()

  def validate_email(self, value):
    try:
      user = User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User not found")

    if user.is_active:
      raise serializers.ValidationError("Email is already verified")

    self.user = user
    return value

  def save(self):
    user = self.user

    verification_code = str(secrets.randbelow(900000) + 100000)

    user.verification_code = verification_code
    user.verification_code_expires = (
      timezone.now() + timedelta(minutes=10)
    )

    user.save()

    html_content = render_to_string(
      "emails/verification_email.html",
      {
        "user": user,
        "verification_code": verification_code,
      }
    )

    email = EmailMultiAlternatives(
      subject="Your new verificattion code",
      body=(
        f"Hello {user.first_name},"
        f"your new verification code is {verification_code}."
        "It expires in 10 minutes"
      ),
      from_email=settings.DEFAULT_FROM_EMAIL,
      to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

    return user
'''

class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)

  def validate(self, attrs):
    email = attrs["email"]
    password = attrs["password"]

    user = authenticate(
      request=self.context.get("request"),
      username=email,
      password=password,
    )

    if not user:
      raise serializers.ValidationError("Invalid email or password.")

    refresh = RefreshToken.for_user(user)

    attrs["user"] = user
    attrs["refresh"] = str(refresh)
    attrs["access"] = str(refresh.access_token)

    return attrs


class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = [
      "id",
      "email",
      "first_name",
      "last_name",
      "role",
    ]
    read_only_fields = fields

class StudentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Student
    fields = [
      "id",
      "user",
      "admission_number",
      "date_of_birth",
      "phone_number",
      "address",
    ]
    read_only_fields = ["id", "admission_number"]

class TeacherSerializer(serializers.ModelSerializer):
  class Meta:
    model = Teacher
    fields = "__all__"
    read_only_fields = ["id", "employee_number", "date_joined"]

class SchoolClassSerializer(serializers.ModelSerializer):
  class Meta:
    model = SchoolClass
    fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Subject
    fields = [
      "id",
      "name",
      "code",
      "school_class",
      "teachers",
    ]

class EnrollmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Enrollment
    fields = "__all__"
    read_only_fields = ["id", "date_enrolled"]

class AttendanceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Attendance
    fields = "__all__"
    read_only_fields = ["id"]

  def validate(self, attrs):
    student = attrs.get("student")
    school_class = attrs.get("school_class")
    date = attrs.get("date")

    if student and school_class:
      enrolled = Enrollment.objects.filter(student=student, school_class=school_class).exists()

      if not enrolled:
        raise serializers.ValidationError({
          "student": ("This student is not enrolled in the selected class")
        })

    if student and date:
      duplicate = Attendance.objects.filter(student=student, date=date)

      if self.instance:
        duplicate = duplicate.exclude(pk=self.instance.pk)

      if duplicate.exists():
        raise serializers.ValidationError({
          "date": (
            "Attendance has already been recorded for this student on this date."
          )
        })

    return attrs

