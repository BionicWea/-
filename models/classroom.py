from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from models.db import get_db

class Classroom:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.classrooms
        
        # 创建索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保必要的索引存在"""
        # 班级编号索引
        self.collection.create_index([('classroom_id', ASCENDING)], unique=True)
        # 班级名称索引
        self.collection.create_index([('classroom_name', ASCENDING)])
        # 学院ID索引
        self.collection.create_index([('college_id', ASCENDING)])
    
    def create_classroom(self, data):
        """创建新的班级记录"""
        classroom_doc = {
            'classroom_id': data['classroom_id'],  # 班级编号
            'classroom_name': data['classroom_name'],  # 班级名称
            'college_id': ObjectId(data['college_id']), # 所属学院ID
            'entry_year': data.get('entry_year'), # 入学年份
            'created_at': datetime.now(),  # 创建时间
            'updated_at': datetime.now(),  # 更新时间
            'is_deleted': False,  # 软删除标记
            'deleted_at': None  # 删除时间
        }
        
        result = self.collection.insert_one(classroom_doc)
        return str(result.inserted_id)
    
    def update_classroom(self, classroom_id, data):
        """更新班级记录"""
        update_data = {
            '$set': {
                'classroom_name': data['classroom_name'],
                'college_id': data['college_id'],
                'entry_year': data.get('entry_year'),
                'updated_at': datetime.now()
            }
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(classroom_id), 'is_deleted': False},
            update_data
        )
        return result.modified_count > 0
    
    def soft_delete(self, classroom_id):
        """软删除班级记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(classroom_id), 'is_deleted': False},
            {
                '$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def restore_classroom(self, classroom_id):
        """恢复被删除的班级记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(classroom_id), 'is_deleted': True},
            {
                '$set': {
                    'is_deleted': False,
                    'deleted_at': None
                }
            }
        )
        return result.modified_count > 0
    
    def get_classroom(self, classroom_id):
        """获取单个班级记录"""
        return self.collection.find_one({'_id': ObjectId(classroom_id), 'is_deleted': False})
    
    def get_all_classrooms(self, college_id=None):
        """获取所有未删除的班级记录，可按学院ID筛选"""
        query = {'is_deleted': False}
        if college_id:
            # 确保 college_id 是 ObjectId 类型
            if not isinstance(college_id, ObjectId):
                try:
                    college_id = ObjectId(college_id)
                except:
                    # 如果 college_id 无效，返回空列表
                    return []
            query['college_id'] = college_id
        return list(self.collection.find(query).sort('created_at', ASCENDING))

    def find_classroom_by_id(self, classroom_id):
        """根据班级编号查找班级记录"""
        return self.collection.find_one({'classroom_id': classroom_id, 'is_deleted': False})

    def count_classrooms_by_college_id(self, college_id):
        """计算属于某个学院的未删除班级数量"""
        # 确保 college_id 是 ObjectId 类型
        if not isinstance(college_id, ObjectId):
            try:
                college_id = ObjectId(college_id)
            except:
                return 0 # 如果 college_id 无效，返回0
        return self.collection.count_documents({'college_id': college_id, 'is_deleted': False})

    def get_deleted_classrooms(self):
        """获取所有已软删除的班级记录"""
        return list(self.collection.find({'is_deleted': True}).sort('deleted_at', DESCENDING))