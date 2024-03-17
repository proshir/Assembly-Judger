from copy import deepcopy
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Max, Subquery, OuterRef

from judger.utils import delete_file, delete_folder, delete_tests, extract_zip, problem_test_folder_path, problem_test_file_path, submission_file_path
    
class Problem(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    test_file = models.FileField(upload_to=problem_test_file_path)
    can_send = models.BooleanField(default=True)
    timeout = models.IntegerField(default=1)  # Timeout in seconds
    new_test_file_uploaded = False
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            input_zip = self.test_file.path
            input_extract_to = problem_test_folder_path(self)
            extract_zip(input_zip, input_extract_to)
            delete_file(input_zip)
        else:
            super().save(*args, **kwargs)
            if self.new_test_file_uploaded:
                folder_path = problem_test_folder_path(self)
                delete_tests(folder_path)
                input_zip = self.test_file.path
                extract_zip(input_zip, folder_path)
                delete_file(input_zip)

    def delete(self, *args, **kwargs):
        folder_path = problem_test_folder_path(self)
        delete_folder(folder_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

class Submission(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code_file = models.FileField(upload_to=submission_file_path)
    result = models.JSONField(blank=True, null=True)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')

    def save(self, *args, **kwargs):
        self.score = (self.result.count(0) / len(self.result)) * 100 if self.result else 0
        super().save(*args, **kwargs)

    def get_result_meanings(self):
        result_descriptions = {
            0: "Correct",
            1: "Incorrect",
            2: "Timeout Limit",
            3: "Fail"
        }
        
        return list(zip(range(1, len(self.result) + 1), [result_descriptions.get(result, "Unknown") for result in self.result])) if self.result else []
    
    @staticmethod
    def get_final_submissions(queryset):
        max_scores = Submission.objects.filter(
            user=OuterRef('user'),
            problem=OuterRef('problem')
        ).values('user', 'problem').annotate(
            max_score=Max('score'),
            oldest_created_at=Max('created_at')
        )

        return queryset.filter(
            user_id__in=Subquery(max_scores.values('user')),
            problem_id__in=Subquery(max_scores.values('problem')),
            score__in=Subquery(max_scores.values('max_score')),
            created_at=Subquery(max_scores.values('oldest_created_at'))  # Filter by earliest created_at
        )
    
    def delete(self, *args, **kwargs):
        delete_file(self.code_file.path)
        super().delete(*args, **kwargs)