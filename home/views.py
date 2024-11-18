from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .models import *
from django.contrib import messages
from .forms import CourseForm
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseForbidden


def home(request):
    return render(request, 'index.html')

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})


def student_register(request):
    courses = Course.objects.all()  
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        phone = request.POST['phone']
        selected_course_id = request.POST['course'] 
        user = User.objects.create_user(username=username, email=email, password=password)
        student_profile = StudentProfile.objects.create(
            user=user,
            status='pending',
            address=address,
            phone=phone,
            assigned_course_id=selected_course_id,
            payment_status='paid'  
        )

        messages.success(request, "Registration successful! Your payment has been received, and your account is pending approval.")
        return redirect('student_login')

    return render(request, 'student_register.html', {'courses': courses})
    

def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                student_profile = user.studentprofile 
                if student_profile.is_approved:  
                    login(request, user)
                    messages.success(request, "You have successfully logged in!")
                    return redirect('student_dashboard')  
                else:
                    messages.error(request, "Your account is not approved yet  Or Contact the Admin")
            except StudentProfile.DoesNotExist:
                messages.error(request, "You do not have a student profile.")
        else:
            messages.error(request, "Invalid username or password.")
        return redirect('student_login')  
    return render(request, 'student_login.html')


def student_dashboard(request):
    # Get the student's profile and assigned course
    student_profile = StudentProfile.objects.get(user=request.user)
    assigned_course = student_profile.assigned_course

    if assigned_course:
        # Retrieve exams that are started and match the assigned course
        exams = Exam.objects.filter(staff_profile__assigned_course=assigned_course, is_started=True)
    else:
        exams = []  # No exams if no course is assigned

    return render(request, 'student_dashboard.html', {
        'student_profile': student_profile,
        'exams': exams
    })

def start_student_exam(request, exam_id):
    # Get the exam by its ID
    exam = get_object_or_404(Exam, id=exam_id)
    exam.is_started = True
    exam.save()
    
    # Get the questions associated with the exam
    questions = Question.objects.filter(exam=exam)
    
    return render(request, 'take_exam.html', {
        'exam': exam,
        'questions': questions  # Pass the questions to the template
    })


def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Check what data is being submitted

        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            print(f"Question ID: {question.id}, Selected Answer: {selected_answer}")  # Debug output
            
            if not selected_answer:
                # Redirect back to the exam with an error message if any question is unanswered
                messages.error(request, "Please answer all questions before submitting.")
                return redirect('take_exam', exam_id=exam.id)

        # Save answers if all questions are answered
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer:  # Only save if there's a selected answer
                Answer.objects.create(
                    student=request.user,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=(selected_answer == question.correct_answer)
                )
        
        return redirect('exam_results', exam_id=exam.id)
    
    return redirect('take_exam', exam_id=exam.id)

def exam_results(request, exam_id):
    # Get the specific exam
    exam = get_object_or_404(Exam, id=exam_id)
        # Fetch the student's answers for this exam
    answers = Answer.objects.filter(student=request.user, question__exam=exam)
        # Get all questions in the exam for answer review
    questions = Question.objects.filter(exam=exam)
    # Calculate total questions and correct answers
    total_questions = questions.count()
    correct_answers = answers.filter(is_correct=True).count()
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        # Prepare data for answer review: whether each answer was correct or not
    answer_review = []
    for question in questions:
        # Find the student's answer for this question, if it exists
        student_answer = answers.filter(question=question).first()
        selected_answer = student_answer.selected_answer if student_answer else None
        is_correct = student_answer.is_correct if student_answer else False
        correct_answer = question.correct_answer
        
        # Append the details to the review list
        answer_review.append({
            'question_text': question.question_text,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    # Pass all data to the template
    context = {
        'exam': exam,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'score_percentage': score_percentage,
        'answer_review': answer_review
    }
    return render(request, 'exam_results.html', context)

def staff_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
   
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('staff_register')
        user = User.objects.create_user(username=username, email=email, password=password)
        StaffProfile.objects.create(user=user)  
       
        messages.success(request, "You have successfully registered! You can now log in.")
        return redirect('staff_login') 
    
    return render(request, 'staff_register.html')



def staff_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user:
            try:
                # Check if the staff profile exists
                staff_profile = StaffProfile.objects.get(user=user)
                
                # Check if the staff has been rejected
                if staff_profile.is_rejected:
                    messages.error(request, "Your registration was rejected. Please contact admin.")
                    return redirect('staff_login')
                
                # Check if the staff is approved
                elif not staff_profile.is_approved:
                    messages.info(request, "Your registration is pending approval.")
                    return redirect('staff_login')
                
                else:
                    # If approved, log in the user
                    login(request, user)
                    messages.success(request, "Successfully logged in.")
                    return redirect('staff_dashboard')  # You can change this to wherever you want the staff to go after login
                
            except StaffProfile.DoesNotExist:
                # If the staff profile does not exist for this user
                messages.error(request, "No staff profile found for this user.")
                return redirect('staff_login')
            
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('staff_login')     
        
    return render(request, 'staff_login.html')

def staff_dashboard(request):
    # Check if the logged-in user has a staff profile
    staff_profile, created = StaffProfile.objects.get_or_create(user=request.user)

    if not staff_profile.is_approved:
        return render(request, 'not_approved.html', {
            'message': 'Your profile is pending approval by the admin.',
        })

    # Retrieve exams assigned to the staff's course/subject
    exams = Exam.objects.filter(staff_profile=staff_profile)

    return render(request, 'staff_dashboard.html', {
        'staff_profile': staff_profile,
        'exams': exams,
    })
def approve_staff(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)
    if request.method == 'POST':
        course_id = request.POST.get('course')
        subject_id = request.POST.get('subject')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            subject = get_object_or_404(Subject, id=subject_id)
            staff.assigned_course = course
            staff.assigned_subject = subject
            staff.is_approved = True
            staff.is_rejected = False
            staff.save()
            messages.success(request, f'Staff member {staff.user.username} has been approved and assigned to {course.title}.')
            return redirect('admin_dashboard') 

    courses = Course.objects.all()
    return render(request, 'approve_staff.html', {'staff': staff, 'courses': courses})

def add_question(request):
    exam = get_object_or_404(Exam)

    if request.method == 'POST':
        # Get data from POST request
        question_text = request.POST.get('question_text')
        option_1 = request.POST.get('option_1')
        option_2 = request.POST.get('option_2')
        option_3 = request.POST.get('option_3')
        option_4 = request.POST.get('option_4')
        correct_answer = request.POST.get('correct_answer')

        # Save the question to the database
        Question.objects.create(
            question_text=question_text,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_answer=correct_answer
        )

        messages.success(request, "Question added successfully.")
        return redirect('add_question', exam_id=exam.id)  # Redirect to the same page or another page as desired

    return render(request, 'add_question.html')

def reject_staff(request, staff_id):
    staff = get_object_or_404(StaffProfile, id=staff_id)
    staff.is_rejected = True
    staff.is_approved = False
    staff.save()
    messages.success(request, f"Staff member {staff.user.username} has been rejected.")
    return redirect('admin_dashboard')

def choose_course(request):
    courses = Course.objects.all()
    return render(request, 'choose_course.html', {'courses': courses})

def add_subject(request):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        name = request.POST.get('name')
        code = request.POST.get('code')

        course = Course.objects.get(id=course_id)
        subject = Subject(name=name, course=course, code=code)
        subject.save()

        messages.success(request, f'Subject "{name}" added successfully.')
        return redirect('admin_dashboard')
    
    courses = Course.objects.all()
    return render(request, 'add_subject.html', {'courses': courses})


def create_exam(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        staff_profile_id = request.POST.get('staff_profile')
        
        # Ensure staff_profile_id is passed and valid
        if not staff_profile_id:
            return render(request, 'create_exam.html', {'error': 'Staff profile is required.'})

        try:
            # Retrieve the staff profile using the ID
            staff_profile = StaffProfile.objects.get(id=staff_profile_id)
        except StaffProfile.DoesNotExist:
            return render(request, 'create_exam.html', {'error': 'Invalid staff profile.'})
        
        # Check if the staff profile is approved (optional check based on your requirements)
        if not staff_profile.is_approved:
            return render(request, 'create_exam.html', {'error': 'Staff profile is not approved.'})
        
        # Create the exam with the selected staff profile
        exam = Exam.objects.create(
            staff_profile=staff_profile,
            title=title
        )
        
        # Redirect to the add questions page after creating the exam, passing exam.id
        return redirect(reverse('add_questions', kwargs={'exam_id': exam.id}))
    
    # If GET request, fetch staff profiles to show in the form
    staff_profiles = StaffProfile.objects.all()
    return render(request, 'create_exam.html', {'staff_profiles': staff_profiles})



def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Update the exam status to started
        exam.is_started = True
        exam.save()
        return redirect('staff_dashboard')  # Redirect back to the staff dashboard
    
    return HttpResponseForbidden("You cannot access this page.")

def view_exams(request):
    # Filter exams that are not started yet
    available_exams = Exam.objects.filter(is_started=False)
    
    return render(request, 'available_exams.html', {
        'exams': available_exams
    })

def available_exams(request):
    completed_exam_ids = Answer.objects.filter(student=request.user).values_list('question__exam_id', flat=True).distinct()
    available_exams = Exam.objects.exclude(id__in=completed_exam_ids)
    
    return render(request, 'home/available_exams.html', {
        'exams': available_exams,
    })

def add_questions(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    
    if request.method == 'POST':
        # Loop through each question in the submitted form
        num_questions = len(request.POST.getlist('question_text'))
        for i in range(num_questions):
            question_text = request.POST.getlist('question_text')[i]
            option_1 = request.POST.getlist('option_1')[i]
            option_2 = request.POST.getlist('option_2')[i]
            option_3 = request.POST.getlist('option_3')[i]
            option_4 = request.POST.getlist('option_4')[i]
            correct_answer = request.POST.getlist('correct_answer')[i]
            
            # Create a new question for the exam
            Question.objects.create(
                exam=exam,
                question_text=question_text,
                option_1=option_1,
                option_2=option_2,
                option_3=option_3,
                option_4=option_4,
                correct_answer=correct_answer
            )
        
        # Redirect back to the same page after adding questions
        return redirect('add_questions', exam_id=exam.id)
    
    return render(request, 'add_questions.html', {'exam': exam})


def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)
    if not questions:
        return render(request, 'take_exam.html', {'exam': exam, 'error_message': "No questions available for this exam."})
    return render(request, 'take_exam.html', {'exam': exam, 'questions': questions})

def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        exam.is_started = True
        exam.save()
        messages.success(request, 'Exam started successfully!')
        return redirect('staff_dashboard')
def admin_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('admin_register')
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! You can now log in.")

        return redirect('admin_login')
    
    return render(request, 'admin_register.html')


def admin_dashboard(request):
    pending_students = StudentProfile.objects.filter(status='pending')
    pending_staff = StaffProfile.objects.filter(is_approved=False, is_rejected=False)
    courses = Course.objects.all()  
    subjects = Subject.objects.all()
    context = {
        'pending_students': pending_students,
        'pending_staff': pending_staff,
        'courses': courses,
        'subjects':subjects
    }
    return render(request, 'admin_dashboard.html', context)





def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')  
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in!")  
            return redirect('admin_dashboard') 
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('admin_login') 
            
    return render(request, 'admin_login.html')  

def admin_logout(request):
    logout(request)  
    return redirect('admin_login')  

def approve_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        student.is_approved = True
        student.status = 'approved' 
        student.save()
        messages.success(request, f"Student {student.user.username} has been approved.")
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


def reject_student(request, student_id):
    student_profile = get_object_or_404(StudentProfile, id=student_id)
    student_profile.is_rejected = True
    student_profile.is_approved = False
    student_profile.save()
    messages.error(request, f"{student_profile.user.username} has been rejected as a student.")
    return redirect('admin_dashboard')

def attend_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        messages.error(request, "Exam does not exist.")
        return redirect('home')

    # Check if the student is allowed to take the exam (by checking the course)
    student_profile = StudentProfile.objects.get(user=request.user)
    if exam.staff.assigned_subject not in student_profile.user.studentprofile.courses.all():
        messages.error(request, "You are not eligible to attend this exam.")
        return redirect('home')

    # Get the questions related to the exam
    questions = Question.objects.filter(assigned_subject=exam.staff.assigned_subject)

    if request.method == "POST":
        correct_answers = 0
        total_questions = len(questions)
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer == question.correct_answer:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100
        messages.success(request, f"You scored {score}% in the exam.")
        # Save the result in Student's profile or Exam result model if needed

        return redirect('home')

    return render(request, 'attend_exam.html', {'exam': exam, 'questions': questions})

