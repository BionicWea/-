from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import get_db
from bson.objectid import ObjectId
from models.student import Student
from models.score import Score
from models.college import College
from models.classroom import Classroom
from models.course import Course

students_bp = Blueprint('students', __name__, url_prefix='/students')

@students_bp.route('/')
def list_students():
    student_model = Student()
    students = student_model.get_all_students()
    
    # 获取所有学院和班级信息，用于显示名称
    college_model = College()
    classroom_model = Classroom()
    colleges = {str(c['_id']): c['college_name'] for c in college_model.get_all_colleges()}
    classrooms = {str(c['_id']): c['classroom_name'] for c in classroom_model.get_all_classrooms()}
    
    # 获取每个学生的课程数量和平均成绩
    score_model = Score()
    for student in students:
        student['_id'] = str(student['_id'])
        scores = score_model.get_scores_by_student_id(student['_id'])
        student['course_count'] = len(scores)
        if scores:
            student['average_score'] = sum(score['score'] for score in scores) / len(scores)
        else:
            student['average_score'] = 0
    
    return render_template('students/list.html', students=students, colleges=colleges, classrooms=classrooms)

@students_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    college_model = College()
    classroom_model = Classroom()
    colleges = college_model.get_all_colleges()
    classrooms = classroom_model.get_all_classrooms()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        college_id = request.form.get('college_id')
        classroom_id = request.form.get('classroom_id')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        
        if not all([student_id, student_name, college_id, classroom_id]):
            flash('学号、姓名、学院和班级不能为空', 'danger')
            return render_template('students/add.html', colleges=colleges, classrooms=classrooms)
        
        student_model = Student()
        existing_student = student_model.find_student_by_id(student_id)
        if existing_student:
            flash('学号已存在', 'danger')
            return render_template('students/add.html', colleges=colleges, classrooms=classrooms)
        
        data = {
            'student_id': student_id,
            'student_name': student_name,
            'college_id': college_id,
            'classroom_id': classroom_id,
            'gender': gender,
            'birth_date': birth_date
        }
        student_model.create_student(data)
        flash('学生添加成功', 'success')
        return redirect(url_for('students.list_students'))
    
    return render_template('students/add.html', colleges=colleges, classrooms=classrooms)

@students_bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_student(id):
    student_model = Student()
    student = student_model.get_student(id)
    if not student:
        flash('找不到该学生信息', 'danger')
        return redirect(url_for('students.list_students'))
    
    college_model = College()
    classroom_model = Classroom()
    colleges = college_model.get_all_colleges()
    classrooms = classroom_model.get_all_classrooms()
    
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        college_id = request.form.get('college_id')
        classroom_id = request.form.get('classroom_id')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        
        if not all([student_name, college_id, classroom_id]):
            flash('姓名、学院和班级不能为空', 'danger')
            return render_template('students/edit.html', student=student, colleges=colleges, classrooms=classrooms)
        
        data = {
            'student_name': student_name,
            'college_id': college_id,
            'classroom_id': classroom_id,
            'gender': gender,
            'birth_date': birth_date
        }
        if student_model.update_student(id, data):
            flash('学生信息更新成功', 'success')
            return redirect(url_for('students.list_students'))
        else:
            flash('学生信息更新失败', 'danger')
            return render_template('students/edit.html', student=student, colleges=colleges, classrooms=classrooms)
    
    return render_template('students/edit.html', student=student, colleges=colleges, classrooms=classrooms)

@students_bp.route('/<id>/detail')
def student_detail(id):
    student_model = Student()
    student = student_model.get_student(id)
    if not student:
        flash('找不到该学生信息', 'danger')
        return redirect(url_for('students.list_students'))
    
    # 获取学生所属的学院和班级信息
    college_model = College()
    classroom_model = Classroom()
    college = college_model.get_college(student['college_id'])
    classroom = classroom_model.get_classroom(student['classroom_id'])
    
    # 获取学生的所有课程成绩
    score_model = Score()
    course_model = Course()
    scores = score_model.get_scores_by_student_id(str(student['_id']))
    
    # 获取课程信息
    for score in scores:
        course = course_model.get_course(score['course_id'])
        if course:
            score['course_name'] = course['course_name']
            score['teacher_name'] = course.get('teacher_name', '未知')
    
    return render_template('students/detail.html', 
                           student=student, 
                           college=college, 
                           classroom=classroom, 
                           scores=scores)

@students_bp.route('/delete/<id>', methods=['POST'])
def delete_student(id):
    student_model = Student()
    score_model = Score()
    
    # 删除学生的所有成绩记录
    deleted_count = score_model.delete_scores_by_student_id(id)
    
    # 删除学生记录
    if student_model.soft_delete(id):
        flash(f'学生及其 {deleted_count} 条成绩记录已删除', 'success')
    else:
        flash('学生删除失败', 'danger')
    return redirect(url_for('students.list_students'))

@students_bp.route('/restore/<id>', methods=['POST'])
def restore_student(id):
    student_model = Student()
    if student_model.restore_student(id):
        flash('学生恢复成功', 'success')
    else:
        flash('学生恢复失败', 'danger')
    return redirect(url_for('students.list_students'))

@students_bp.route('/trash')
def trash_students():
    student_model = Student()
    deleted_students = student_model.get_deleted_students()
    
    # 获取所有学院和班级信息，用于显示名称
    college_model = College()
    classroom_model = Classroom()
    colleges = {str(c['_id']): c['college_name'] for c in college_model.get_all_colleges()}
    classrooms = {str(c['_id']): c['classroom_name'] for c in classroom_model.get_all_classrooms()}
    
    return render_template('students/trash.html', students=deleted_students, colleges=colleges, classrooms=classrooms)