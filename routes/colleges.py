from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.college import College
from models.classroom import Classroom # Import Classroom model
from bson.objectid import ObjectId

colleges_bp = Blueprint('colleges', __name__, url_prefix='/colleges')

@colleges_bp.route('/')
def list_colleges():
    college_model = College()
    classroom_model = Classroom() # Import and instantiate Classroom model
    colleges = college_model.get_all_colleges()
    # 获取每个学院的班级数量
    for college in colleges:
        college['classroom_count'] = classroom_model.count_classrooms_by_college_id(college['_id'])
    return render_template('colleges/list.html', colleges=colleges)

@colleges_bp.route('/add', methods=['GET', 'POST'])
def add_college():
    if request.method == 'POST':
        college_id = request.form.get('college_id')
        college_name = request.form.get('college_name')
        if not college_id or not college_name:
            flash('学院编号和学院名称不能为空', 'danger')
            return render_template('colleges/add.html')
        
        college_model = College()
        existing_college = college_model.find_college_by_id(college_id)
        if existing_college:
            flash('学院编号已存在', 'danger')
            return render_template('colleges/add.html')

        data = {'college_id': college_id, 'college_name': college_name}
        college_model.create_college(data)
        flash('学院添加成功', 'success')
        return redirect(url_for('colleges.list_colleges'))
    return render_template('colleges/add.html')

@colleges_bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit_college(id):
    college_model = College()
    college = college_model.get_college(id)
    if not college:
        flash('找不到该学院信息', 'danger')
        return redirect(url_for('colleges.list_colleges'))

    if request.method == 'POST':
        college_name = request.form.get('college_name')
        if not college_name:
            flash('学院名称不能为空', 'danger')
            return render_template('colleges/edit.html', college=college)

        data = {'college_name': college_name}
        if college_model.update_college(id, data):
            flash('学院更新成功', 'success')
            return redirect(url_for('colleges.list_colleges'))
        else:
            flash('学院更新失败', 'danger')
            return render_template('colleges/edit.html', college=college)

    return render_template('colleges/edit.html', college=college)

@colleges_bp.route('/delete/<id>', methods=['POST'])
def delete_college(id):
    college_model = College()
    if college_model.soft_delete(id):
        flash('学院删除成功', 'success')
    else:
        flash('学院删除失败', 'danger')
    return redirect(url_for('colleges.list_colleges'))

@colleges_bp.route('/restore/<id>', methods=['POST'])
def restore_college(id):
    college_model = College()
    if college_model.restore_college(id):
        flash('学院恢复成功', 'success')
    else:
        flash('学院恢复失败', 'danger')
    return redirect(url_for('colleges.list_colleges'))