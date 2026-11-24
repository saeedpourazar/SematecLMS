from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):

    def __str__(self):
        return self.name + ' ' + self.family

    name = models.CharField(max_length=50)
    family = models.CharField(max_length=50)
    bio = models.TextField()
    image = models.ImageField(upload_to='instructors/')


class Category(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)


class Course(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        Category,
        blank=True
    )
    duration = models.IntegerField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='courses/')


class Enrollment(models.Model):

    def __str__(self):
        return self.student.username + ' - ' + self.course.title

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    date_enrolled = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('student', 'course')