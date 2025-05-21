from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.course import Course
from models.classroom import Classroom
from bson.objectid import ObjectId

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/')
def list_courses():
    course_model = Course()
    courses = course_model.get_all_courses()
    classroom_model = Classroom()
    # 获取所有班级信息，用于在列表中显示班级名称
    classrooms = {str(c['_id']): c['classroom_name'] for c in classroom_model.get_all_classrooms()}
    return render_template('courses/list.html', courses=courses, classrooms=classrooms)

@courses_bp.route('/add', methods=['GET', 'POST'])
def add_course():
    classroom_model = Classroom()
    classrooms = classroom_model.get_all_classrooms()
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        course_name = request.form.get('course_name')
        classroom_id = request.form.get('classroom_id')
        teacher_name = request.form.get('teacher_name')

        if not course_id or not course_name or not classroom_id:
            flash('课程编号、课程名称和所属班级不能为空', 'danger')
            return render_template('courses/add.html', classrooms=classrooms)

        course_model = Course()
        existing_course = course_model.find_course_by_id(course_id)
        if existing_course:
            flash('课程编号已存在', 'danger')
            return render_template('courses/add.html', classrooms=classrooms)

        data = {
            'course_id': course_id,
            'course_name': course_name,
            'classroom_id': classroom_id,
            'teacher_name': teacher_name
        }
        course_model.create_course(data)
        flash('课程添加成功', 'success')
        return redirect(url_for('courses.list_courses'))

    return render_template('courses/add.html', classrooms=classrooms)

@courses_bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_course(id):
    course_model = Course()
    course = course_model.get_course(id)
    if not course:
        flash('找不到该课程信息', 'danger')
        return redirect(url_for('courses.list_courses'))

    classroom_model = Classroom()
    classrooms = classroom_model.get_all_classrooms()

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        classroom_id = request.form.get('classroom_id')
        teacher_name = request.form.get('teacher_name')

        if not course_name or not classroom_id:
            flash('课程名称和所属班级不能为空', 'danger')
            return render_template('courses/edit.html', course=course, classrooms=classrooms)

        data = {
            'course_name': course_name,
            'classroom_id': classroom_id,
            'teacher_name': teacher_name
        }
        if course_model.update_course(id, data):
            flash('课程更新成功', 'success')
            return redirect(url_for('courses.list_courses'))
        else:
            flash('课程更新失败', 'danger')
            return render_template('courses/edit.html', course=course, classrooms=classrooms)

    return render_template('courses/edit.html', course=course, classrooms=classrooms)

@courses_bp.route('/delete/<id>', methods=['POST'])
def delete_course(id):
    course_model = Course()
    if course_model.soft_delete(id):
        flash('课程删除成功', 'success')
    else:
        flash('课程删除失败', 'danger')
    return redirect(url_for('courses.list_courses'))

@courses_bp.route('/restore/<id>', methods=['POST'])
def restore_course(id):
    course_model = Course()
    if course_model.restore_course(id):
        flash('课程恢复成功', 'success')
    else:
        flash('课程恢复失败', 'danger')
    return redirect(url_for('courses.list_courses'))