from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from models.db import get_db
from datetime import datetime, timedelta

class Student:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.students
        
        # 创建索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保必要的索引存在"""
        # 学号索引，确保唯一性
        self.collection.create_index([('Sno', ASCENDING)], unique=True)
        # 姓名索引
        self.collection.create_index([('Sname', ASCENDING)])
        # 班级ID索引
        self.collection.create_index([('classroom_id', ASCENDING)])
    
    def create_student(self, data):
        """创建新的学生记录"""
        student_doc = {
            'Sno': data['Sno'],  # 学号
            'Sname': data['Sname'],  # 学生姓名
            'entry_year': int(data.get('entry_year')) if data.get('entry_year') else None,  # 入学年份
            'major': data.get('major', ''),  # 专业
            'classroom_id': ObjectId(data.get('classroom_id')) if data.get('classroom_id') else None, # 所属班级ID
            'created_at': datetime.now(),  # 创建时间
            'updated_at': datetime.now(),  # 更新时间
            'is_deleted': False,  # 软删除标记
            'deleted_at': None  # 删除时间
        }
        
        print(f"[DEBUG] Creating student with data: {student_doc}") # 添加调试日志
        result = self.collection.insert_one(student_doc)
        return str(result.inserted_id)
    
    def update_student(self, student_id, data):
        """更新学生记录"""
        update_data = {
            '$set': {
                'Sname': data['Sname'],
                'entry_year': int(data.get('entry_year')) if data.get('entry_year') else None,
                'major': data.get('major', ''),
                'classroom_id': data.get('classroom_id', None),
                'updated_at': datetime.now()
            }
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(student_id)},
            update_data
        )
        return result.modified_count > 0
    
    def soft_delete(self, student_id):
        """软删除学生记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(student_id)},
            {
                '$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def restore_student(self, student_id):
        """恢复被删除的学生记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(student_id)},
            {
                '$set': {
                    'is_deleted': False,
                    'deleted_at': None
                }
            }
        )
        return result.modified_count > 0
    
    def get_student(self, student_id):
        """获取单个学生记录"""
        return self.collection.find_one({'_id': ObjectId(student_id)}) or self.collection.find_one({'Sno': student_id})
    
    def get_all_students(self):
        """获取所有未删除的学生记录"""
        return self.collection.find({'is_deleted': False}).sort('Sno', ASCENDING)

    def find_student_by_sno(self, sno):
        """根据学号查找学生记录"""
        return self.collection.find_one({'Sno': sno, 'is_deleted': False})

    def find_students_by_classroom(self, classroom_id):
        """根据班级ID查找学生记录"""
        # 确保 classroom_id 是 ObjectId 类型，如果不是，尝试转换
        if not isinstance(classroom_id, ObjectId):
            try:
                classroom_id = ObjectId(classroom_id)
            except:
                return [] # 如果 classroom_id 无效，返回空列表
        return self.collection.find({'classroom_id': classroom_id, 'is_deleted': False}).sort('Sno', ASCENDING)

    def find_student_by_id(self, student_id):
        """根据学生ID查找学生记录"""
        try:
            return self.collection.find_one({'_id': ObjectId(student_id), 'is_deleted': False})
        except:
            return None

    def search_students(self, query_params):
        """多条件搜索学生记录"""
        query = {'is_deleted': False}
        
        if 'Sno' in query_params and query_params['Sno']:
            query['Sno'] = {'$regex': query_params['Sno'], '$options': 'i'}
        if 'Sname' in query_params and query_params['Sname']:
            query['Sname'] = {'$regex': query_params['Sname'], '$options': 'i'}
        if 'entry_year' in query_params and query_params['entry_year']:
             query['entry_year'] = int(query_params['entry_year'])
        if 'major' in query_params and query_params['major']:
             query['major'] = {'$regex': query_params['major'], '$options': 'i'}
        if 'classroom_id' in query_params and query_params['classroom_id']:
             query['classroom_id'] = query_params['classroom_id']

        return self.collection.find(query).sort('Sno', ASCENDING)

    def delete_student_by_sno(self, sno):
        """根据学号删除学生记录（硬删除）"""
        result = self.collection.delete_one({'Sno': sno})
        return result.deleted_count > 0

    def delete_student_by_id(self, student_id):
        """根据ID删除学生记录（硬删除）"""
        result = self.collection.delete_one({'_id': ObjectId(student_id)})
        return result.deleted_count > 0

    def get_deleted_students(self, days=30):
        """获取指定天数内的已删除学生记录"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        query = {
            'is_deleted': True,
            'deleted_at': {'$gte': cutoff_date}
        }
        return self.collection.find(query).sort('deleted_at', DESCENDING)

    def count_students_by_classroom_id(self, classroom_id):
        """根据班级ID计算未删除的学生数量"""
        # 确保 classroom_id 是 ObjectId 类型，如果不是，尝试转换
        if not isinstance(classroom_id, ObjectId):
            try:
                classroom_id = ObjectId(classroom_id)
            except:
                return 0 # 如果 classroom_id 无效，返回0
        return self.collection.count_documents({'classroom_id': classroom_id, 'is_deleted': False})