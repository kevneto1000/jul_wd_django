from django.db import models
from django.conf import settings

from accounts.models import Student, Subject

class Assessment(models.Model):
  ASSESSMENT_TYPES = [
    ("test", "Test"),
    ("assignment", "Assignment"),
    ("exam", "Examination"),
  ]

  title = models.CharField(max_length=150)
  assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
  subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="assessments")
  academic_year = models.CharField(max_length=9)
  term = models.PositiveSmallIntegerField()
  date = models.DateField()
  max_score = models.DecimalField(max_digits=6, decimal_places=2)
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_assessments")
  is_published = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-date", "subject"]

  def __str__(self):
    return f"{self.title} - {self.subject}"

class StudentResult(models.Model):
  assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="student_results")
  student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
  score = models.DecimalField(max_digits=6, decimal_places=2)
  remarks = models.CharField(max_length=255, blank=True)

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["assessment", "student"],
        name="unique_student_assessment_result"
      )
    ]
    ordering = ["student"]

  def __str__(self):
    return f"{self.student} - {self.assessment.title}"

  @property
  def percentage(self):
    if self.assessment.max_score <= 0:
      return 0
    return round(
      (self.score / self.assessment.max_score) * 100, 2,
    )

  @property
  def grade(self):
    percentage = self.percentage

    if percentage >= 70:
      return "A"
    elif percentage >= 60:
      return "B"
    elif percentage >= 50:
      return "C"
    elif percentage >= 45:
      return "D"
    elif percentage >= 40:
      return "E"
    return "F"


