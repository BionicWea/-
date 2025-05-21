from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from models.db import get_db

class Course:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.courses
        
        # 创建索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保必要的索引存在"""
        # 课程编号索引
        self.collection.create_index([('course_id', ASCENDING)], unique=True)
        # 课程名称索引
        self.collection.create_index([('course_name', ASCENDING)])
        # 班级ID索引
        self.collection.create_index([('classroom_id', ASCENDING)])
    
    def create_course(self, data):
        """创建新的课程记录"""
        course_doc = {
            'course_id': data['course_id'],  # 课程编号
            'course_name': data['course_name'],  # 课程名称
            'classroom_id': ObjectId(data['classroom_id']), # 所属班级ID
            'teacher_name': data.get('teacher_name'), # 授课教师姓名
            'created_at': datetime.now(),  # 创建时间
            'updated_at': datetime.now(),  # 更新时间
            'is_deleted': False,  # 软删除标记
            'deleted_at': None  # 删除时间
        }
        
        result = self.collection.insert_one(course_doc)
        return str(result.inserted_id)
    
    def update_course(self, course_id, data):
        """更新课程记录"""
        update_data = {
            '$set': {
                'course_name': data['course_name'],
                'classroom_id': data['classroom_id'],
                'teacher_name': data.get('teacher_name'),
                'updated_at': datetime.now()
            }
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(course_id), 'is_deleted': False},
            update_data
        )
        return result.modified_count > 0
    
    def soft_delete(self, course_id):
        """软删除课程记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(course_id), 'is_deleted': False},
            {
                '$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def restore_course(self, course_id):
        """恢复被删除的课程记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(course_id), 'is_deleted': True},
            {
                '$set': {
                    'is_deleted': False,
                    'deleted_at': None
                }
            }
        )
        return result.modified_count > 0
    
    def get_course(self, course_id):
        """获取单个课程记录"""
        return self.collection.find_one({'_id': ObjectId(course_id), 'is_deleted': False})
    
    def get_all_courses(self):
        """获取所有未删除的课程记录"""
        return list(self.collection.find({'is_deleted': False}).sort('created_at', ASCENDING))

    def find_course_by_id(self, course_id):
        """根据课程编号查找课程记录"""
        return self.collection.find_one({'course_id': course_id, 'is_deleted': False})

    def count_courses_by_classroom_id(self, classroom_id):
        """根据班级ID计算未删除的课程数量"""
        # 确保 classroom_id 是 ObjectId 类型，如果不是，尝试转换
        if not isinstance(classroom_id, ObjectId):
            try:
                classroom_id = ObjectId(classroom_id)
            except:
                return 0 # 如果 classroom_id 无效，返回0
        return self.collection.count_documents({'classroom_id': classroom_id, 'is_deleted': False})

    def find_courses_by_classroom_id(self, classroom_id):
        """根据班级ID查找未删除的课程记录"""
        # 确保 classroom_id 是 ObjectId 类型，如果不是，尝试转换
        if not isinstance(classroom_id, ObjectId):
            try:
                classroom_id = ObjectId(classroom_id)
            except:
                return [] # 如果 classroom_id 无效，返回空列表
        return list(self.collection.find({'classroom_id': classroom_id, 'is_deleted': False}).sort('created_at', ASCENDING))