
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course, Choice, Enrollment, Submission


@login_required
def submit(request, course_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    course = get_object_or_404(Course, pk=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    selected_ids = []

    for key in request.POST:
        if key.startswith('choice'):
            for value in request.POST.getlist(key):
                try:
                    selected_ids.append(int(value))
                except ValueError:
                    continue

    selected_choices = Choice.objects.filter(
        pk__in=selected_ids,
        question__course=course
    )

    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(selected_choices)

    return redirect(
        'onlinecourse:show_exam_result',
        course_id=course.id,
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    selected_choices = submission.choices.all()

    total_score = 0
    total_grade = 0
    exam_results = []

    for question in course.question_set.prefetch_related('choices').all():
        correct_ids = set(
            question.choices.filter(is_correct=True)
            .values_list('id', flat=True)
        )

        selected_question_ids = set(
            selected_choices.filter(question=question)
            .values_list('id', flat=True)
        )

        is_correct = bool(correct_ids) and correct_ids == selected_question_ids
        grade = question.gradePoints

        total_grade += grade

        if is_correct:
            total_score += grade

        exam_results.append({
            'question': question,
            'selected_choices': selected_choices.filter(
                question=question
            ),
            'correct_choices': question.choices.filter(
                is_correct=True
            ),
            'is_correct': is_correct
        })

    percentage = (
        round((total_score / total_grade) * 100, 2)
        if total_grade > 0 else 0
    )

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': list(
            selected_choices.values_list('id', flat=True)
        ),
        'grade': percentage,
        'total_score': total_score,
        'total_grade': total_grade,
        'percentage': percentage,
        'exam_results': exam_results
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )
