from django.shortcuts import get_object_or_404
# from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdminOrReadOnly, IsAdminOrOwnStudentProfile

from .models import Student, Teacher, SchoolClass, Subject, Enrollment, Attendance

from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, StudentSerializer, TeacherSerializer, SchoolClassSerializer, SubjectSerializer, EnrollmentSerializer, AttendanceSerializer

'''
@api_view(["GET"])
def greet(request):
  return Response({"message": "Hello world!!"})
'''

class RegisterView(APIView):

  def post(self, request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()

      return Response({"message": "Registeration successful. Check your email for verification code"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
class VerifyEmailView(APIView):
  def post(self, request):
    serializer = VerifyEmailSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()

      return Response({"message": "Email verified successfully. You can now log in."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
  def post(self, request):
    serializer = ResendOTPSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()

      return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''

class LoginView(APIView):

  def post(self, request):
    serializer = LoginSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
      user = serializer.validated_data["user"]
      return Response({
        "message": "Login successful",
        "access": serializer.validated_data["access"],
        "refresh": serializer.validated_data["refresh"],
        "user": {
          "id": user.id,
          "email": user.email,
          "first_name": user.first_name,
          "last_name": user.last_name,
          "role": user.role,
        }
      }, 
        status=status.HTTP_200_OK,
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class StudentListCreateView(APIView):
  permission_classes = [IsAdminOrReadOnly]

  def get(self, request):
    if request.user.role == 'student':
      students= Student.objects.filter(user=request.user)
    else:
      students = Student.objects.select_related("user").all()

    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data, status=200)

  def post(self, request):
    serializer = StudentSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

class StudentDetailView(APIView):
  permission_classes = [IsAdminOrOwnStudentProfile, IsAdminOrReadOnly]

  def get_object(self, pk):
    student = get_object_or_404(Student, pk=pk)

    self.check_object_permissions(self.request, student)

    return student

  # def get_student(self, pk):
  #   return get_object_or_404(Student.objects.select_related("user"), pk=pk)

  def get(self, request, pk):
    student = self.get_object(pk)
    serializer = StudentSerializer(student)
    return Response(serializer.data)

  def put(self, request, pk):
    student = self.get_object(pk)
    serializer = StudentSerializer(student, data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=400)

  def delete(self, request, pk):
    student = self.get_student(pk)
    student.delete()
    return Response(status=204)

class TeacherListCreateView(APIView):

  permission_classes = [IsAdminOrReadOnly]
  
  def get(self, request):
    teachers = Teacher.objects.select_related("user").all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data, status=200)

  def post(self, request):
    serializer = TeacherSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

class TeacherDetailView(APIView):
  permission_classes = [IsAdminOrReadOnly]

  def get_teacher(self, pk):
    return get_object_or_404(Teacher.objects.select_related("user"), pk=pk)

  def get(self, request, pk):
    teacher = self.get_teacher(pk)
    serializer = TeacherSerializer(teacher)
    return Response(serializer.data)

  def put(self, request, pk):
    teacher = self.get_teacher(pk)
    serializer = TeacherSerializer(teacher, data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=400)

  def delete(self, request, pk):
    teacher = self.get_teacher(pk)
    teacher.delete()
    return Response(status=204)

class SchoolClassListCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

  def get(self, request):
    classes = SchoolClass.objects.select_related("class_teacher").all()

    serializer = SchoolClassSerializer(classes, many=True)
    return Response(serializer.data)

  def post(self, request):
    serializer = SchoolClassSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

class SubjectListCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

  def get(self, request):
    subjects = Subject.objects.select_related("school_class").prefetch_related("teachers").all()

    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data);

  def post(self, request):
    serializer = SubjectSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


class EnrollmentListCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

  def get(self, request):
    enrollments = Enrollment.objects.select_related("student__user", "school_user")

    if request.user.role == "student":
      enrollments = enrollments.filter(student__user=request.user)
    elif request.user.role == "teacher":
      enrollments = enrollments.filter(school_class__class_teacher__user=request.user)

    serializer = EnrollmentSerializer(enrollments, many=True)

    return Response(serializer.data)

  def post(self, request):
    serializer = EnrollmentSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

class AttendanceListCreateView(APIView):
  permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

  def get(self, request):
    records = Attendance.objects.select_related("student__user", "school_class",)

    if request.user.role == "student":
      records = records.filter(student__user=request.user)
    elif request.user.role == "teacher":
      records = records.filter(school_class__class_teacher__user=request.user)

    serializer = AttendanceSerializer(records, many=True)
    return Response(serializer.data)

  def post(self, request):
    if request.user.role not in ["admin", "teacher"]:
      return Response({"detail": "You do not have permission to record attendance"}, status=403)
    
    serializer = AttendanceSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400) 

    school_class = serializer.validated_data["school_class"]

    if request.user.role == "teacher":
      if school_class.class_teacher is None:
        return Response({"detail": "This class has no assigned class teacher"}, status=403)

      if school_class.class_teacher.user_id != request.user.id:
        return Response({"detail": "You can only record attendance for your own class"}, status=403)

    attendance = serializer.save()
    return Response(AttendanceSerializer(attendance).data, status=201)
      
