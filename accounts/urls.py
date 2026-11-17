from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, StudentListCreateView, StudentDetailView, TeacherListCreateView, TeacherDetailView, SchoolClassListCreateView, SubjectListCreateView, EnrollmentListCreateView, AttendanceListCreateView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
  path("register/", RegisterView.as_view(), name="register"),
  # path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
  # path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
  path("profile/", UserProfileView.as_view(), name="profile"),
  path("students/", StudentListCreateView.as_view(), name="student-list-create"),
  path("students/<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
  path("teachers/", TeacherListCreateView.as_view(), name="teacher-list-create"),
  path("teachers/<int:pk>/", TeacherDetailView.as_view(), name="teacher-detail"),
  path("classes/", SchoolClassListCreateView.as_view(), name="class-list-create"),
  path("subjects/", SubjectListCreateView.as_view(), name="subject-list-create"),
  path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
  path("attendance/", AttendanceListCreateView.as_view(), name="attendance-list-create"),
  path("login/", LoginView.as_view(), name="login"),
  path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]