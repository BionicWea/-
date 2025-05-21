from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.classroom import Classroom
from models.college import College
from models.student import Student
from models.score import Score
from models.course import Course
from bson.objectid import ObjectId

classrooms_bp = Blueprint('classrooms', __name__, url_prefix='/classrooms')

@classrooms_bp.route('/')
def list_classrooms():
    classroom_model = Classroom()
    classrooms = classroom_model.get_all_classrooms()
    college_model = College()
    student_model = Student()
    course_model = Course()
    # 获取所有学院信息，用于在列表中显示学院名称
    colleges = {str(c['_id']): c['college_name'] for c in college_model.get_all_colleges()}
    
    # 获取每个班级的学生数量和课程数量
    for classroom in classrooms:
        classroom['_id'] = str(classroom['_id']) # 确保ID是字符串以便在模板中使用
        classroom['student_count'] = student_model.count_students_by_classroom_id(classroom['_id'])
        classroom['course_count'] = course_model.count_courses_by_classroom_id(classroom['_id'])

    return render_template('classrooms/list.html', classrooms=classrooms, colleges=colleges)

@classrooms_bp.route('/college/<college_id>')
def list_classrooms_by_college(college_id):
    classroom_model = Classroom()
    classrooms = classroom_model.get_all_classrooms(college_id=college_id)
    college_model = College()
    student_model = Student()
    course_model = Course()
    # 获取所有学院信息，用于在列表中显示学院名称
    colleges = {str(c['_id']): c['college_name'] for c in college_model.get_all_colleges()}
    # 获取当前学院信息用于页面标题等
    current_college = college_model.get_college(college_id)

    # 获取每个班级的学生数量和课程数量
    for classroom in classrooms:
        classroom['_id'] = str(classroom['_id']) # 确保ID是字符串以便在模板中使用
        classroom['student_count'] = student_model.count_students_by_classroom_id(classroom['_id'])
        classroom['course_count'] = course_model.count_courses_by_classroom_id(classroom['_id'])

    return render_template('classrooms/list.html', classrooms=classrooms, colleges=colleges, current_college=current_college)

@classrooms_bp.route('/add', methods=['GET', 'POST'])
def add_classroom():
    college_model = College()
    colleges = college_model.get_all_colleges()
    if request.method == 'POST':
        classroom_id = request.form.get('classroom_id')
        classroom_name = request.form.get('classroom_name')
        college_id = request.form.get('college_id')
        entry_year = request.form.get('entry_year')

        if not classroom_id or not classroom_name or not college_id:
            flash('班级编号、班级名称和所属学院不能为空', 'danger')
            return render_template('classrooms/add.html', colleges=colleges)

        classroom_model = Classroom()
        existing_classroom = classroom_model.find_classroom_by_id(classroom_id)
        if existing_classroom:
            flash('班级编号已存在', 'danger')
            return render_template('classrooms/add.html', colleges=colleges)

        data = {
            'classroom_id': classroom_id,
            'classroom_name': classroom_name,
            'college_id': college_id,
            'entry_year': int(entry_year) if entry_year else None
        }
        classroom_model.create_classroom(data)
        flash('班级添加成功', 'success')
        return redirect(url_for('classrooms.list_classrooms'))

    return render_template('classrooms/add.html', colleges=colleges)

@classrooms_bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_classroom(id):
    classroom_model = Classroom()
    classroom = classroom_model.get_classroom(id)
    if not classroom:
        flash('找不到该班级信息', 'danger')
        return redirect(url_for('classrooms.list_classrooms'))

    college_model = College()
    colleges = college_model.get_all_colleges()

    if request.method == 'POST':
        classroom_name = request.form.get('classroom_name')
        college_id = request.form.get('college_id')
        entry_year = request.form.get('entry_year')

        if not classroom_name or not college_id:
            flash('班级名称和所属学院不能为空', 'danger')
            return render_template('classrooms/edit.html', classroom=classroom, colleges=colleges)

        data = {
            'classroom_name': classroom_name,
            'college_id': college_id,
            'entry_year': int(entry_year) if entry_year else None
        }
        if classroom_model.update_classroom(id, data):
            flash('班级更新成功', 'success')
            return redirect(url_for('classrooms.list_classrooms'))
        else:
            flash('班级更新失败', 'danger')
            return render_template('classrooms/edit.html', classroom=classroom, colleges=colleges)

    return render_template('classrooms/edit.html', classroom=classroom, colleges=colleges)

@classrooms_bp.route('/delete/<id>', methods=['POST'])
def delete_classroom(id):
    classroom_model = Classroom()
    if classroom_model.soft_delete(id):
        flash('班级删除成功', 'success')
    else:
        flash('班级删除失败', 'danger')
    return redirect(url_for('classrooms.list_classrooms'))

@classrooms_bp.route('/restore/<id>', methods=['POST'])
def restore_classroom(id):
    classroom_model = Classroom()
    if classroom_model.restore_classroom(id):
        flash('班级恢复成功', 'success')
    else:
        flash('班级恢复失败', 'danger')
    return redirect(url_for('classrooms.list_classrooms'))

@classrooms_bp.route('/<id>/detail')
def classroom_detail(id):
    classroom_model = Classroom()
    classroom = classroom_model.get_classroom(id)
    if not classroom:
        flash('找不到该班级信息', 'danger')
        return redirect(url_for('classrooms.list_classrooms'))

    student_model = Student()
    # 查找属于该班级的所有学生
    students = student_model.find_students_by_classroom(str(classroom['_id']))

    # Add this print statement to inspect the students data
    print(f"Debug: Students found for classroom {id}: {list(students)}")

    # 对于每个学生，获取他们的成绩
    score_model = Score()
    for student in students:
        student['scores'] = score_model.get_scores_by_student_id(str(student['_id']))

    # 查找该班级开设的所有课程
    course_model = Course()
    courses = course_model.find_courses_by_classroom_id(str(classroom['_id']))

    # 获取所有学院信息，用于显示学院名称
    college_model = College()
    colleges = college_model.get_all_colleges()
    colleges_dict = {str(c['_id']): c['college_name'] for c in colleges}

    return render_template('classrooms/detail.html', 
                          classroom=classroom, 
                          students=students, 
                          courses=courses, 
                          colleges=colleges_dict,
                          all_colleges=colleges)

@classrooms_bp.route('/<id>/add_student', methods=['GET', 'POST'])
def add_classroom_student(id):
    classroom_model = Classroom()
    classroom = classroom_model.get_classroom(id)
    if not classroom:
        flash('找不到该班级信息', 'danger')
        return redirect(url_for('classrooms.list_classrooms'))
    
    college_model = College()
    colleges = college_model.get_all_colleges()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        
        if not all([student_id, student_name]):
            flash('学号和姓名不能为空', 'danger')
            return render_template('classrooms/add_student.html', classroom=classroom, colleges=colleges)
        
        student_model = Student()
        # 检查学号是否已存在
        existing_student = student_model.find_student_by_sno(student_id)
        if existing_student:
            flash('学号已存在', 'danger')
            return render_template('classrooms/add_student.html', classroom=classroom, colleges=colleges)
        
        data = {
            'Sno': student_id,
            'Sname': student_name,
            'classroom_id': id, # 使用路由参数中的班级ID
        }
        student_model.create_student(data)
        flash('学生添加成功', 'success')
        return redirect(url_for('classrooms.classroom_detail', id=id))
    
    return render_template('classrooms/add_student.html', classroom=classroom, colleges=colleges)

@classrooms_bp.route('/trash')
def trash_classrooms():
    classroom_model = Classroom()
    deleted_classrooms = classroom_model.get_deleted_classrooms()
    college_model = College()
    # 获取所有学院信息，用于在列表中显示学院名称
    colleges = {str(c['_id']): c['college_name'] for c in college_model.get_all_colleges()}

    return render_template('classrooms/trash.html', classrooms=deleted_classrooms, colleges=colleges)