import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from judger.forms import ProblemForm
from judger.models import Problem, Submission
from judger.tasks import test_code_async
from judger.utils import read_code_file, test_code

@login_required
def home(request):
    return redirect('problem_list')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('problem_list') 
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    else:
        if request.user.is_authenticated:
            return redirect('problem_list')
        return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('problem_list')

@staff_member_required
def upload_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('problem_list')
    else:
        form = ProblemForm()
    return render(request, 'upload_problem.html', {'form': form})

@login_required
def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'problems.html', {'problems': problems})

@login_required
def view_problem(request, problem_id):
    problem = Problem.objects.get(pk=problem_id)
    return render(request, 'problem.html', {'problem': problem})

@login_required
def submit_solution(request, problem_id):
    if request.method == 'POST':
        code_file = request.FILES.get('code_file')
        problem = Problem.objects.get(pk=problem_id)
        if code_file and problem.can_send:
            submission = Submission.objects.create(user=request.user, problem=problem, code_file=code_file)
            test_code_async.delay(submission.id)
            return redirect('submission_detail', submission_id=submission.id)
    return redirect('view_problem', problem_id=problem_id)

@login_required
def view_submissions(request):
    user = request.user
    problem_id = request.GET.get('problem_id')

    if user.is_staff:
        submissions = Submission.objects.all()
    else:
        submissions = Submission.objects.filter(user_id=user.id)

    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)

    user_id = request.GET.get('user_id')

    if user_id:
        submissions = submissions.filter(user_id=user_id)

    if request.GET.get('download_csv'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="submissions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Submission ID', 'Status', 'Score', 'User', 'Problem', 'Submitted'])

        for submission in submissions:
            writer.writerow([submission.id, submission.get_status_display(), submission.score, submission.user.username, submission.problem.name, submission.created_at])

        return response
    
    return render(request, 'submissions.html', {'submissions': submissions})

@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to view this submission.")
    code_content = read_code_file(submission.code_file)

    return render(request, 'submission.html', {'submission': submission, 'code_content': code_content})

@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if submission.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this submission.")
    
    if request.method == 'POST':
        submission.delete()
        
    return redirect('view_submissions', problem_id=submission.problem_id)