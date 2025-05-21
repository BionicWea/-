# 导入 Flask 类
from flask import Flask

def create_app():
    # 创建 Flask 应用实例
    app = Flask(__name__)
    
    # 从 config.py 文件中的 Config 类加载配置
    app.config.from_object('config.Config')
    
    # 从 models.db 模块导入数据库初始化函数
    from models.db import init_app
    # 初始化数据库连接，注册 teardown 函数
    init_app(app)
    
    # 从 routes 模块导入蓝图
    from routes.scores import scores_bp
    from routes.students import students_bp
    from routes.index import index_bp
    from routes.colleges import colleges_bp
    from routes.classrooms import classrooms_bp
    from routes.courses import courses_bp
    
    # 注册蓝图到应用实例
    # 蓝图用于组织相关的路由和视图函数
    app.register_blueprint(index_bp)  # 注册根路由蓝图
    app.register_blueprint(scores_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(colleges_bp)
    app.register_blueprint(classrooms_bp)
    app.register_blueprint(courses_bp)
    
    return app

# 创建应用实例
app = create_app()

# 当脚本直接运行时
if __name__ == '__main__':
    # 从 config.py 文件中的 Config 类加载配置
    app.config.from_object('config.Config')

    # 从 models.db 模块导入数据库初始化函数
    from models.db import init_app
    # 初始化数据库连接，注册 teardown 函数
    init_app(app)

    # 运行 Flask 应用
    # debug=True 开启调试模式，方便开发
    # host='0.0.0.0' 使应用在本地网络中可访问
    # port=5002 指定应用运行的端口
    app.run(debug=True, host='0.0.0.0', port=5002)