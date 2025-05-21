from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from models.db import get_db

class College:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.colleges
        
        # 创建索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保必要的索引存在"""
        # 学院编号索引
        self.collection.create_index([('college_id', ASCENDING)], unique=True)
        # 学院名称索引
        self.collection.create_index([('college_name', ASCENDING)])
    
    def create_college(self, data):
        """创建新的学院记录"""
        college_doc = {
            'college_id': data['college_id'],  # 学院编号
            'college_name': data['college_name'],  # 学院名称
            'created_at': datetime.now(),  # 创建时间
            'updated_at': datetime.now(),  # 更新时间
            'is_deleted': False,  # 软删除标记
            'deleted_at': None  # 删除时间
        }
        
        result = self.collection.insert_one(college_doc)
        return str(result.inserted_id)
    
    def update_college(self, college_id, data):
        """更新学院记录"""
        update_data = {
            '$set': {
                'college_name': data['college_name'],
                'updated_at': datetime.now()
            }
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(college_id), 'is_deleted': False},
            update_data
        )
        return result.modified_count > 0
    
    def soft_delete(self, college_id):
        """软删除学院记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(college_id), 'is_deleted': False},
            {
                '$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def restore_college(self, college_id):
        """恢复被删除的学院记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(college_id), 'is_deleted': True},
            {
                '$set': {
                    'is_deleted': False,
                    'deleted_at': None
                }
            }
        )
        return result.modified_count > 0
    
    def get_college(self, college_id):
        """获取单个学院记录"""
        return self.collection.find_one({'_id': ObjectId(college_id), 'is_deleted': False})
    
    def get_all_colleges(self):
        """获取所有未删除的学院记录"""
        return list(self.collection.find({'is_deleted': False}).sort('created_at', ASCENDING))

    def find_college_by_id(self, college_id):
        """根据学院编号查找学院记录"""
        return self.collection.find_one({'college_id': college_id, 'is_deleted': False})