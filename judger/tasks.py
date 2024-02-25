from celery import shared_task
from .models import Submission
from .utils import test_code

@shared_task
def test_code_async(submission_id):
    try:
        submission = Submission.objects.get(pk=submission_id)
        submission.status = 'Testing'
        submission.save()

        try:
            submission.result = test_code(submission.code_file, submission.problem)
            submission.status = 'Completed'
        except Exception as e:
            submission.status = 'Failed'
            print(f"Error testing submission {submission_id}: {str(e)}")

        submission.save()

    except Submission.DoesNotExist:
        pass
