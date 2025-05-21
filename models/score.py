from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from models.db import get_db

class Score:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.scores
        
        # 创建索引
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保必要的索引存在"""
        # 学号索引
        self.collection.create_index([('student_id', ASCENDING)])
        # 科目索引
        self.collection.create_index([('subject', ASCENDING)])
        # 考试类型和时间复合索引
        self.collection.create_index([
            ('exam_type', ASCENDING),
            ('created_at', DESCENDING)
        ])
    
    def create_score(self, data):
        """创建新的成绩记录"""
        score_doc = {
            'student_id': data['student_id'],  # 学号
            'student_name': data['student_name'],  # 学生姓名
            'subject': data['subject'],  # 科目
            'score': float(data['score']),  # 成绩
            'exam_type': data['exam_type'],  # 考试类型（期中/期末/平时）
            'note': data.get('note', ''),  # 备注
            'status': data.get('status', 'normal'),  # 成绩状态（正常/补考/缓考/缺考）
            'created_at': datetime.now(),  # 创建时间
            'updated_at': datetime.now(),  # 更新时间
            'is_deleted': False,  # 软删除标记
            'deleted_at': None  # 删除时间
        }
        
        result = self.collection.insert_one(score_doc)
        return str(result.inserted_id)
    
    def update_score(self, score_id, data):
        """更新成绩记录"""
        update_data = {
            '$set': {
                'score': float(data['score']),
                'note': data.get('note', ''),
                'status': data.get('status', 'normal'),
                'updated_at': datetime.now()
            }
        }
        
        result = self.collection.update_one(
            {'_id': ObjectId(score_id)},
            update_data
        )
        return result.modified_count > 0
    
    def soft_delete(self, score_id):
        """软删除成绩记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(score_id)},
            {
                '$set': {
                    'is_deleted': True,
                    'deleted_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    def restore_score(self, score_id):
        """恢复被删除的成绩记录"""
        result = self.collection.update_one(
            {'_id': ObjectId(score_id)},
            {
                '$set': {
                    'is_deleted': False,
                    'deleted_at': None
                }
            }
        )
        return result.modified_count > 0
    
    def get_score(self, score_id):
        """获取单个成绩记录"""
        return self.collection.find_one({'_id': ObjectId(score_id)})
    
    def search_scores(self, query_params):
        """多条件搜索成绩记录"""
        query = {'is_deleted': False}
        
        # 添加查询条件
        if 'student_id' in query_params:
            query['student_id'] = {'$regex': query_params['student_id'], '$options': 'i'}
        if 'student_name' in query_params:
            query['student_name'] = {'$regex': query_params['student_name'], '$options': 'i'}
        if 'subject' in query_params:
            query['subject'] = query_params['subject']
        if 'exam_type' in query_params:
            query['exam_type'] = query_params['exam_type']
        if 'score_range' in query_params:
            score_range = query_params['score_range']
            query['score'] = {
                '$gte': float(score_range['min']),
                '$lte': float(score_range['max'])
            }
        if 'status' in query_params:
            query['status'] = query_params['status']
            
        return self.collection.find(query).sort('created_at', DESCENDING)
    
    def get_scores_by_student_id(self, student_id):
        """根据学生 ID 获取所有成绩记录"""
        query = {'student_id': student_id, 'is_deleted': False}
        return list(self.collection.find(query).sort('created_at', DESCENDING))

    def delete_scores_by_student_id(self, student_id):
        """删除与特定学生 ID 相关的所有成绩记录"""
        result = self.collection.delete_many({'student_id': student_id})
        return result.deleted_count

    def get_deleted_scores(self, days=30):
        """获取指定天数内的已删除成绩记录"""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = {
            'is_deleted': True,
            'deleted_at': {'$gte': cutoff_date}
        }
        return self.collection.find(query).sort('deleted_at', DESCENDING)