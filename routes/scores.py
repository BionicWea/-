from flask import Blueprint, render_template, request, jsonify, send_file
from models.score import Score
from datetime import datetime
import pandas as pd
import io

scores_bp = Blueprint('scores', __name__, url_prefix='/scores')


@scores_bp.route('/list')
def list_scores():
    """显示成绩列表页面"""
    return render_template('scores/list.html')


@scores_bp.route('/search')
def search_scores():
    """搜索成绩记录"""
    score_model = Score()

    query_params = {
        'student_id': request.args.get('student_id'),
        'student_name': request.args.get('student_name'),
        'subject': request.args.get('subject'),
        'exam_type': request.args.get('exam_type'),
        'status': request.args.get('status')
    }

    score_min = request.args.get('score_min')
    score_max = request.args.get('score_max')
    if score_min is not None and score_max is not None:
        query_params['score_range'] = {'min': score_min, 'max': score_max}

    scores = list(score_model.search_scores(query_params))
    return jsonify(scores)


@scores_bp.route('/add', methods=['POST'])
def add_score():
    """添加成绩记录"""
    try:
        score_model = Score()
        score_id = score_model.create_score(request.form)
        return jsonify({'success': True, 'score_id': score_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@scores_bp.route('/update/<score_id>', methods=['POST'])
def update_score(score_id):
    """更新成绩记录"""
    try:
        score_model = Score()
        success = score_model.update_score(score_id, request.form)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@scores_bp.route('/delete/<score_id>', methods=['POST'])
def delete_score(score_id):
    """删除成绩记录（软删除）"""
    try:
        score_model = Score()
        success = score_model.soft_delete(score_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@scores_bp.route('/restore/<score_id>', methods=['POST'])
def restore_score(score_id):
    """恢复已删除的成绩记录"""
    try:
        score_model = Score()
        success = score_model.restore_score(score_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@scores_bp.route('/trash')
def trash_scores():
    """显示回收站页面"""
    return render_template('scores/trash.html')


@scores_bp.route('/export')
def export_scores():
    """导出成绩数据"""
    try:
        score_model = Score()
        query_params = {
            'student_id': request.args.get('student_id'),
            'student_name': request.args.get('student_name'),
            'subject': request.args.get('subject'),
            'exam_type': request.args.get('exam_type')
        }

        scores = list(score_model.search_scores(query_params))
        df = pd.DataFrame(scores)

        columns = ['student_id', 'student_name', 'subject', 'score',
                  'exam_type', 'status', 'note', 'created_at']
        df = df[columns]

        column_names = {
            'student_id': '学号',
            'student_name': '姓名',
            'subject': '科目',
            'score': '成绩',
            'exam_type': '考试类型',
            'status': '状态',
            'note': '备注',
            'created_at': '创建时间'
        }
        df = df.rename(columns=column_names)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='成绩数据')
        output.seek(0)

        filename = f'成绩数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'导出成绩数据时发生错误: {e}', 'danger')
        return redirect(url_for('scores.list_scores'))

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@scores_bp.route('/import', methods=['POST'])
def import_scores():
    """导入成绩数据"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未找到文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400

        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'error': '文件格式错误，请上传 .xlsx 或 .xls 文件'}), 400

        df = pd.read_excel(file)

        required_columns = ['学号', '姓名', '科目', '成绩', '考试类型', '状态', '备注']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'success': False, 'error': f"文件缺少必要列，请确保包含: {', '.join(required_columns)}"}), 400

        score_model = Score()
        imported_count = 0

        for index, row in df.iterrows():
            try:
                score_data = {
                    'student_id': str(row['学号']),
                    'student_name': str(row['姓名']),
                    'subject': str(row['科目']),
                    'score': float(row['成绩']),
                    'exam_type': str(row['考试类型']),
                    'status': str(row['状态']),
                    'note': str(row.get('备注', '')),
                }
                score_model.create_score(score_data)
                imported_count += 1
            except Exception as row_e:
                print(f"导入第 {index + 2} 行数据时出错: {row_e}")
                continue

        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'message': f'成功导入 {imported_count} 条成绩记录。'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500