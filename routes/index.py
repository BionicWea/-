from flask import Blueprint, redirect, url_for, render_template

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    """根路由重定向到管理员仪表盘页面"""
    return redirect(url_for('index.admin_dashboard'))

from models.student import Student
from models.classroom import Classroom
from models.course import Course
# from ..utils import get_pending_tasks # 假设存在获取待办事项的函数

@index_bp.route('/admin')
def admin_dashboard():
    """管理员仪表盘页面"""
    # 获取数据统计
    student_model = Student()
    classroom_model = Classroom()
    course_model = Course()

    student_count = len(list(student_model.get_all_students()))
    classroom_count = len(classroom_model.get_all_classrooms())
    course_count = len(course_model.get_all_courses())

    # 获取待办事项 (示例，需要根据实际业务逻辑实现)
    # pending_tasks = get_pending_tasks() 
    pending_tasks = [] # 暂时使用空列表

    return render_template('admin_dashboard.html', 
                           student_count=student_count,
                           classroom_count=classroom_count,
                           course_count=course_count,
                           pending_tasks=pending_tasks)