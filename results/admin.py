from django.contrib import admin
from .models import Assessment, StudentResult

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "assessment_type",
        "academic_year",
        "term",
        "max_score",
        "is_published",
    )
    list_filter = (
        "assessment_type",
        "academic_year",
        "term",
        "is_published",
    )
    search_fields = ("title", "subject__name")

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = (
        "assessment",
        "student",
        "score",
        "get_percentage",
        "get_grade",
    )
    list_filter = ("assessment__academic_year", "assessment__term")
    search_fields = ("student__admission_number", "student__user__first_name", "student__user__last_name", "assessment__title")

    @admin.display(description="Percentage")
    def get_percentage(self, obj):
        return f"{obj.percentage}%"

    @admin.display(description="Grade")
    def get_grade(self, obj):
        return obj.grade 
