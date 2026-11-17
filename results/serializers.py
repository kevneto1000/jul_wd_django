from rest_framework import serializers

from .models import Assessment, StudentResult
from accounts.models import Enrollment

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at", "is_published"]

    def validate(self, attrs):
        max_score = attrs.get("max_score", self.instance.max_score if self.instance else None)
        term = attrs.get("term", self.instance.term if self.instance else None)

        if max_score is not None and max_score <= 0:
            raise serializers.ValidationError({"max_score": "Max score must be greater than zero."})

        if term is not None and term not in [1, 2, 3]:
            raise serializers.ValidationError({"term": "Term must be either 1, 2, or 3."})

        return attrs

class StudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentResult
        fields = "__all__"
        read_only_fields = ["id", "percentage", "grade"]

    def validate(self, attrs):
        assessment = attrs.get("assessment", self.instance.assessment if self.instance else None)
        student = attrs.get("student", self.instance.student if self.instance else None)
        score = attrs.get("score", self.instance.score if self.instance else None)

        if assessment and student:
            enrolled = Enrollment.objects.filter(
                student=student,
                school_class=assessment.subject.school_class,
            ).exists()

            if not enrolled:
                raise serializers.ValidationError({"student": "This student is not enrolled in the class for this assessment."})

        if assessment and score is not None:
            if score < 0:
                raise serializers.ValidationError({"score": "Score cannot be negative."})

            if score > assessment.max_score:
                raise serializers.ValidationError({"score": (f"Score cannot exceed {assessment.max_score}.")})

        return attrs