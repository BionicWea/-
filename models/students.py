# 导入获取数据库连接的函数
from models.db import get_db
# 导入 ObjectId 类，用于处理 MongoDB 的文档 ID
from bson.objectid import ObjectId

class Student:
    """学生模型类，用于操作 MongoDB 中的学生集合。"""

    def __init__(self):
        # 获取数据库连接
        self.db = get_db()
        # 获取学生集合
        self.collection = self.db['students']

    def get_all_students(self):
        """获取所有学生信息。"""
        # 从集合中查找所有文档并返回
        return self.collection.find()

    # TODO: Add methods for adding, updating, and deleting students
    # TODO: 添加用于添加、更新和删除学生的方法