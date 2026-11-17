from django.urls import path

from .views import AssessmentListCreateView, StudentResultListCreateView, AssessmentPublishView, StudentResultDetailView

urlpatterns = [
    path("assessments/", AssessmentListCreateView.as_view(), name="assessment-list-create"),
    path("assessments/<int:pk>/publish/", AssessmentPublishView.as_view(), name="assessment-publish"),
    path("scores/", StudentResultListCreateView.as_view(), name="student-result-list-create"),
    path("scores/<int:pk>/", StudentResultDetailView.as_view(), name="student-result-detail"),
]