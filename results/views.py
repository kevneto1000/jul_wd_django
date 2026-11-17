from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import Assessment, StudentResult
from .serializers import AssessmentSerializer, StudentResultSerializer

class AssessmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assessments = Assessment.objects.select_related("subject", "created_by")

        if request.user.role == "student":
            assessments = assessments.filter(
                is_published=True,
                subject__school_class__enrollment__student=request.user
            )
        elif request.user.role != "admin":
            return Response(
                {"detail": "You do not have permission to view assessments."},
                status=403
            )

        assessments = assessments.distinct()
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role not in ["admin", "teacher"]:
            return Response(
                {"detail": "You do not have permission to create assessments."},
                status=403
            )

        serializer = AssessmentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        subject = serializer.validated_data["subject"]
        if request.user.role == "teacher":
            if not subject.teachers.filter(user=request.user).exists():
                return Response(
                    {"detail": "You do not have permission to create assessments for this subject."},
                    status=403
                )

        assessment = serializer.save(created_by=request.user)
        return Response(AssessmentSerializer(assessment).data, status=201)

class StudentResultListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = StudentResult.objects.select_related(
            "student__user",
            "assessment__subject",
        )

        if request.user.role == "student":
            results = results.filter(student__user=request.user, assessment__is_published=True)
        elif request.user.role == "teacher":
            results = results.filter(
                assessment__subject__teachers__user=request.user
            )
        elif request.user.role != "admin":
            return Response(
                {"detail": "You do not have permission to view student results."},
                status=403
            )
        results = results.distinct()
        serializer = StudentResultSerializer(results, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role not in ["admin", "teacher"]:
            return Response(
                {"detail": "You do not have permission to create student results."},
                status=403
            )
        serializer = StudentResultSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        assessment = serializer.validated_data["assessment"]

        if assessment.is_published:
            return Response(
                {"detail": "This assessment has already been published."},
                status=400
            )

        if request.user.role == "teacher":
            if not assessment.subject.teachers.filter(user=request.user).exists():
                return Response(
                    {"detail": "You can only record results for your assigned subjects."},
                    status=403
                )
        result = serializer.save()
        return Response(StudentResultSerializer(result).data, status=201)

class StudentResultDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_result(self, pk):
        return get_object_or_404(
            StudentResult.objects.select_related(
                "assessment__subject",
                "student__user",
            ),
            pk=pk,
        )

    def can_manage(self, request, result):
        if request.user.role == "admin":
            return True
        
        if request.user.role == "teacher":
            return result.assessment.subject.teachers.filter(user=request.user).exists()
        
        return False

    def put(self, request, pk):
        result = self.get_result(pk)

        if not self.can_manage(request, result):
            return Response(
                {"detail": "You cannot update this result."},
                status=403
            )

        if (request.user.role == "teacher" and result.assessment.is_published):
            return Response(
                {"detail": "Published results cannot be edited by teachers."},
                status=403
            )

        serializer = StudentResultSerializer(result, data=request.data)

        if serializer.is_valid():
            new_assessment = serializer.validated_data.get("assessment", result.assessment)

            if (request.user.role == "teacher" and not new_assessment.subject.teachers.filter(
                user=request.user
            ).exists()):
                return Response(
                    {"detail": "You are not assigned to this subject."},
                    status=403
                )

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        result = self.get_result(pk)

        if not self.can_manage(request, result):
            return Response(
                {"detail": "You cannot update this result."},
                status=403
            )

        if (request.user.role == "teacher" and result.assessment.is_published):
            return Response(
                {"detail": "Published results cannot be edited by teachers."},
                status=403
            )

        serializer = StudentResultSerializer(result, data=request.data)

        if serializer.is_valid():
            new_assessment = serializer.validated_data.get("assessment", result.assessment)
            
            if (request.user.role == "teacher" and not new_assessment.subject.teachers.filter(
                user=request.user
            ).exists()):
                return Response(
                    {"detail": "You are not assigned to this subject."},
                    status=403
                )
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        result = self.get_result(pk)

        if not self.can_manage(request, result):
            return Response(
                {"detail": "You cannot delete this result."},
                status=403
            )

        if (request.user.role == "teacher" and result.assessment.is_published):
            return Response(
                {"detail": "Published results cannot be deleted by teachers."},
                status=403
            )

        result.delete()

        return Response(
                {"detail": "Result deleted successfully."},
                status=204
            )

class AssessmentPublishView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Only administrators can publish results."},
                status=403
            )

        assessment = get_object_or_404(Assessment, pk=pk)

        is_published = request.data.get("is_published")

        if not isinstance(is_published, bool):
            return Response(
                {"detail": "is_published must be a boolean value (true or false)."},
                status=400
            )

        assessment.is_published = is_published
        assessment.save(update_fields=["is_published"])

        return Response(
            {"message": (
                    "Results published successfully" if is_published else "Results unpublished successfully."
                ), 
                "assessment": AssessmentSerializer(assessment).data
            }
        )
