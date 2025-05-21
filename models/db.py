# 导入所需的库
# MongoClient 用于连接 MongoDB 数据库
from pymongo import MongoClient
# current_app 用于访问当前 Flask 应用的配置
# g 用于在请求生命周期内存储数据，这里用于存储数据库连接
from flask import current_app, g

def get_db():
    """获取 MongoDB 数据库连接。

    如果当前应用上下文的 g 对象中没有 'db'，则创建一个新的 MongoClient 连接，
    并获取默认数据库，然后将其存储在 g.db 中。
    这样可以确保在同一个请求中重复调用 get_db() 时，使用的是同一个数据库连接。
    """
    # 检查 g 对象中是否已存在数据库连接
    if 'db' not in g:
        # 从应用配置中获取 MongoDB 连接 URI，并创建 MongoClient 实例
        client = MongoClient(current_app.config['MONGO_URI'])
        # 获取默认数据库
        g.db = client.get_default_database()
    # 返回数据库连接
    return g.db

def close_db(e=None):
    """关闭 MongoDB 数据库连接。

    在应用上下文结束时调用，用于清理资源。
    从 g 对象中弹出 'db' 连接，如果存在，则关闭客户端连接。
    """
    # 从 g 对象中弹出 'db'，如果不存在则返回 None
    db = g.pop('db', None)

    # 如果数据库连接存在，则关闭客户端连接
    if db is not None:
        db.client.close()

def init_app(app):
    """注册数据库相关的函数到 Flask 应用。

    将 close_db 函数注册为应用上下文的 teardown 函数，
    确保在每个请求结束后都会调用 close_db 来关闭数据库连接。
    """
    # 注册 teardown 函数，在请求结束后自动关闭数据库连接
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command) # 可选：如果需要，可以添加用于初始化数据库的 CLI 命令

# 可选：如果需要，可以添加一个用于初始化数据库的 CLI 命令
# import click
# from flask.cli import with_appcontext

# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     """清除现有数据并创建新的集合/索引。"""
#     db = get_db()
#     # 示例：如果需要，可以创建索引
#     # db.scores.create_index([('Sno', 1)], unique=True)
#     click.echo('数据库已初始化。')