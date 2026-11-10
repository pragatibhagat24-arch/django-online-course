
from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Instructor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'

    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin'),
    ]

    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username + ", " + self.occupation


class Course(models.Model):
    name = models.CharField(max_length=100, default='online course')
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    pub_date = models.DateField(null=True, blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrollment',
        blank=True
    )
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200, default='title')
    order = models.IntegerField(default=0)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    content = models.TextField()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'

    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


class Question(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    questionText = models.CharField(max_length=200)
    gradePoints = models.IntegerField(default=50)

    def __str__(self):
        return 'Question: {}'.format(self.questionText)

    def is_get_score(self, selected_ids):
        all_answers = self.choices.filter(is_correct=True).count()
        selected_correct = self.choices.filter(
            is_correct=True,
            id__in=selected_ids
        ).count()
        return all_answers == selected_correct

    @property
    def question_text(self):
        return self.questionText

    @property
    def grade_points(self):
        return self.gradePoints

    @property
    def course_name(self):
        return self.course.name


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choiceText = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choiceText

    @property
    def choice_text(self):
        return self.choiceText


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return 'Submission {}'.format(self.id)
