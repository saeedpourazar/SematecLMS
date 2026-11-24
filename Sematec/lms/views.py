
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Instructor, Category
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from django.contrib.auth.models import Group, User
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, CourseForm, InstructorForm
from datetime import datetime
from django.db.models import Count
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.db.models import Count, Q

# Home View
def home_view(request):
    courses = Course.objects.all()

    context = {
        'courses': courses,
        'total_courses': Course.objects.count(),
        'total_instructors': Instructor.objects.count(),
        'total_students': User.objects.filter(
            groups__name='Student'
        ).distinct().count(),
    }

    return render(request, 'lms/home.html', context)


# Course Detail View
def course_detail_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    enrolled = False
    back_url = 'course_list'

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()

    if request.GET.get('from') == 'my_courses':
        back_url = 'my_courses'

    return render(
        request,
        'lms/course_detail.html',
        {
            'course': course,
            'enrolled': enrolled,
            'back_url': back_url
        }
    )


# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            student_group = Group.objects.get(name='Student')
            user.groups.add(student_group)

            login(request, user)
            return redirect('home')

    else:
        form = SignUpForm()

    return render(
        request,
        'lms/signup.html',
        {'form': form}
    )


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')

            elif user.groups.filter(name='Sematec Staff').exists():
                return redirect('staff_dashboard')

            else:
                return redirect('dashboard')

        else:
            return render(
                request,
                'lms/login.html',
                {'error': 'Username or password is incorrect.'}
            )

    return render(request, 'lms/login.html')


# Logout View
def logout_view(request):
    logout(request)

    return render(request, 'lms/logout.html')


# Enroll Course View
@login_required
@require_POST
def enroll_course_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        return redirect('my_courses')

    return redirect('course_detail', pk=course.pk)


# My Courses View
def my_courses_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    enrollments = Enrollment.objects.filter(
        student=request.user
    )

    return render(
        request,
        'lms/my_courses.html',
        {'enrollments': enrollments}
    )


# Course List View
def course_list_view(request):
    search = request.GET.get('q')
    sort = request.GET.get('sort')
    category_id = request.GET.get('category')

    if search:
        courses = Course.objects.filter(
            title__icontains=search
        )
    else:
        courses = Course.objects.all()

    if category_id:
        courses = courses.filter(
            categories__id=category_id
        )

    if sort == 'price_low':
        courses = courses.order_by('price')

    elif sort == 'price_high':
        courses = courses.order_by('-price')

    elif sort == 'duration_low':
        courses = courses.order_by('duration')

    elif sort == 'duration_high':
        courses = courses.order_by('-duration')

    enrolled_course_ids = []

    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)

    course_count = courses.count()

    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'lms/course_list.html',
        {
            'courses': page_obj,
            'page_obj': page_obj,
            'search': search,
            'sort': sort,
            'category_id': category_id,
            'course_count': course_count,
            'categories': Category.objects.all(),
            'enrolled_course_ids': enrolled_course_ids,
        }
    )


# Instructor List View
def instructor_list_view(request):
    instructors = Instructor.objects.all()

    return render(
        request,
        'lms/instructor_list.html',
        {'instructors': instructors}
    )


# Dashboard View
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    enrollments = Enrollment.objects.filter(
        student=request.user
    )

    instructor_count = enrollments.values(
        'course__instructor'
    ).distinct().count()

    last_enrollment = enrollments.order_by(
        '-date_enrolled'
    ).first()

    return render(
        request,
        'lms/dashboard.html',
        {
            'enrollments': enrollments,
            'instructor_count': instructor_count,
            'last_enrollment': last_enrollment
        }
    )


# Staff Dashboard View

def staff_dashboard_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    # Statistics
    total_courses = Course.objects.count()
    total_instructors = Instructor.objects.count()

    total_students = User.objects.filter(
        groups__name='Student'
    ).distinct().count()

    total_enrollments = Enrollment.objects.count()

    # Latest Courses
    recent_courses = Course.objects.select_related(
        'instructor'
    ).order_by('-id')[:6]

    # Latest Instructors
    recent_instructors = Instructor.objects.order_by(
        '-id'
    )[:6]

    # Latest Students
    recent_students = User.objects.filter(
        groups__name='Student'
    ).distinct().order_by('-date_joined')[:6]

    # Enrollment Chart - Last 6 Months
    now = timezone.localtime()
    monthly_data = []

    for offset in range(5, -1, -1):

        month_index = now.month - offset
        year = now.year

        while month_index <= 0:
            month_index += 12
            year -= 1

        next_month = month_index + 1
        next_year = year

        if next_month > 12:
            next_month = 1
            next_year += 1

        start_date = timezone.make_aware(
            datetime(year, month_index, 1)
        )

        end_date = timezone.make_aware(
            datetime(next_year, next_month, 1)
        )

        enrollment_count = Enrollment.objects.filter(
            date_enrolled__gte=start_date,
            date_enrolled__lt=end_date
        ).count()

        month_name = datetime(
            year, month_index, 1
        ).strftime('%b')

        monthly_data.append({
            'month': month_name,
            'count': enrollment_count
        })

    max_count = max(
        [item['count'] for item in monthly_data],
        default=0
    )

    for item in monthly_data:
        if max_count > 0:
            item['height'] = max(
                8,
                int(item['count'] / max_count * 100)
            )
        else:
            item['height'] = 8

    return render(
        request,
        'lms/staff_dashboard.html',
        {
            'total_courses': total_courses,
            'total_instructors': total_instructors,
            'total_students': total_students,
            'total_enrollments': total_enrollments,
            'recent_courses': recent_courses,
            'recent_instructors': recent_instructors,
            'recent_students': recent_students,
            'monthly_data': monthly_data,
        }
    )



# Course Management View

def course_management_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    search_query = request.GET.get('q', '').strip()
    selected_instructor = request.GET.get('instructor', '')
    selected_category = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'title')

    courses = Course.objects.select_related(
        'instructor'
    ).prefetch_related(
        'categories'
    )

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(instructor__name__icontains=search_query) |
            Q(instructor__family__icontains=search_query)
        )

    if selected_instructor.isdigit():
        courses = courses.filter(instructor_id=int(selected_instructor))
    else:
        selected_instructor = ''

    if selected_category.isdigit():
        courses = courses.filter(categories__id=int(selected_category))
    else:
        selected_category = ''

    allowed_sort_fields = {
        'title': 'title',
        'price': 'price',
        'duration': 'duration'
    }

    sort_by = sort_by if sort_by in allowed_sort_fields else 'title'
    courses = courses.order_by(allowed_sort_fields[sort_by])

    courses = courses.distinct()

    paginator = Paginator(courses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'lms/course_management.html',
        {
            'courses': page_obj,
            'page_obj': page_obj,
            'instructors': Instructor.objects.all().order_by('name', 'family'),
            'categories': Category.objects.all().order_by('name'),
            'search_query': search_query,
            'selected_instructor': selected_instructor,
            'selected_category': selected_category,
            'sort_by': sort_by,
        }
    )



# Add Course View
def add_course_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('course_management')

    else:
        form = CourseForm()

    return render(
        request,
        'lms/add_course.html',
        {'form': form}
    )


# Edit Course View
def edit_course_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(
            request.POST,
            request.FILES,
            instance=course
        )

        if form.is_valid():
            form.save()
            return redirect('course_management')

    else:
        form = CourseForm(instance=course)

    return render(
        request,
        'lms/edit_course.html',
        {
            'form': form,
            'course': course
        }
    )


# Delete Course View
@login_required
@require_POST
def delete_course_view(request, pk):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    course = get_object_or_404(Course, pk=pk)
    course.delete()

    return redirect('course_management')


# Student Management View

@login_required
def student_management_view(request):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    search_query = request.GET.get('q', '').strip()

    students = User.objects.filter(
        groups__name='Student'
    ).annotate(
        enrollment_count=Count('enrollment', distinct=True)
    ).distinct()

    if search_query:
        students = students.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    students = students.order_by('username')

    paginator = Paginator(students, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'lms/student_management.html',
        {
            'students': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
        }
    )


# Instructor Management View

@login_required
def instructor_management_view(request):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    search_query = request.GET.get('q', '').strip()
    course_filter = request.GET.get('courses', 'all')

    instructors = Instructor.objects.annotate(
        course_count=Count('course')
    )

    if search_query:
        instructors = instructors.filter(
            Q(name__icontains=search_query) |
            Q(family__icontains=search_query)
        )

    if course_filter == 'assigned':
        instructors = instructors.filter(course_count__gt=0)

    elif course_filter == 'unassigned':
        instructors = instructors.filter(course_count=0)

    else:
        course_filter = 'all'

    instructors = instructors.order_by('name', 'family')

    paginator = Paginator(instructors, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'lms/instructor_management.html',
        {
            'instructors': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'course_filter': course_filter,
        }
    )



# Reports View
@login_required
def reports_view(request):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    context = {
        'total_courses': Course.objects.count(),
        'total_students': User.objects.filter(
            groups__name='Student'
        ).distinct().count(),
        'total_instructors': Instructor.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
    }

    return render(
        request,
        'lms/reports.html',
        context
    )


# Add Instructor View
@login_required
def add_instructor_view(request):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    if request.method == 'POST':
        form = InstructorForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('instructor_management')

    else:
        form = InstructorForm()

    return render(
        request,
        'lms/add_instructor.html',
        {'form': form}
    )


# Edit Instructor View
@login_required
def edit_instructor_view(request, pk):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    instructor = get_object_or_404(Instructor, pk=pk)

    if request.method == 'POST':
        form = InstructorForm(
            request.POST,
            request.FILES,
            instance=instructor
        )

        if form.is_valid():
            form.save()
            return redirect('instructor_management')

    else:
        form = InstructorForm(instance=instructor)

    return render(
        request,
        'lms/edit_instructor.html',
        {
            'form': form,
            'instructor': instructor
        }
    )


# Delete Instructor View
@login_required
@require_POST
def delete_instructor_view(request, pk):
    if not request.user.groups.filter(name='Sematec Staff').exists():
        return redirect('dashboard')

    instructor = get_object_or_404(Instructor, pk=pk)

    # Prevent deleting instructors who have assigned courses
    if instructor.course_set.exists():
        return redirect('instructor_management')

    instructor.delete()
    return redirect('instructor_management')
# Check Staff Access
def staff_access(request):
    return request.user.groups.filter(name='Sematec Staff').exists()


# Prepare CSV Response
def create_csv_response(filename, headers):
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(headers)

    return response, writer


# Export All Instructors
@login_required
def export_instructors_view(request):
    if not staff_access(request):
        return redirect('dashboard')

    instructors = Instructor.objects.annotate(
        course_count=Count('course')
    ).order_by('name', 'family')

    response, writer = create_csv_response(
        'instructors.csv',
        ['Name', 'Family', 'Bio', 'Courses']
    )

    for instructor in instructors:
        writer.writerow([
            instructor.name,
            instructor.family,
            instructor.bio,
            instructor.course_count
        ])

    return response


# Export Courses Assigned to an Instructor
@login_required
def export_instructor_courses_view(request, pk):
    if not staff_access(request):
        return redirect('dashboard')

    instructor = get_object_or_404(Instructor, pk=pk)
    courses = Course.objects.filter(
        instructor=instructor
    ).prefetch_related('categories').order_by('title')

    response, writer = create_csv_response(
        f'instructor_{instructor.pk}_courses.csv',
        ['Course', 'Instructor', 'Categories', 'Duration', 'Price']
    )

    for course in courses:
        categories = ', '.join(
            course.categories.values_list('name', flat=True)
        )

        writer.writerow([
            course.title,
            str(instructor),
            categories,
            course.duration,
            course.price
        ])

    return response


# Export All Courses
@login_required
def export_courses_view(request):
    if not staff_access(request):
        return redirect('dashboard')

    courses = Course.objects.select_related(
        'instructor'
    ).prefetch_related(
        'categories'
    ).order_by('title')

    response, writer = create_csv_response(
        'courses.csv',
        ['Course', 'Instructor', 'Categories', 'Duration', 'Price']
    )

    for course in courses:
        categories = ', '.join(
            course.categories.values_list('name', flat=True)
        )

        writer.writerow([
            course.title,
            str(course.instructor),
            categories,
            course.duration,
            course.price
        ])

    return response


# Export All Students
@login_required
def export_students_view(request):
    if not staff_access(request):
        return redirect('dashboard')

    students = User.objects.filter(
        groups__name='Student'
    ).annotate(
        enrollment_count=Count('enrollment', distinct=True)
    ).distinct().order_by('username')

    response, writer = create_csv_response(
        'students.csv',
        ['Username', 'First Name', 'Last Name', 'Email',
         'Date Joined', 'Enrolled Courses']
    )

    for student in students:
        writer.writerow([
            student.username,
            student.first_name,
            student.last_name,
            student.email,
            timezone.localtime(student.date_joined).strftime('%Y-%m-%d %H:%M'),
            student.enrollment_count
        ])

    return response