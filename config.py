# config.py 文件用于存放应用的配置信息

class Config:
    # MongoDB 连接 URI
    # 指定 MongoDB 服务器的地址和端口，以及要连接的数据库名称 (student_scores)
    MONGO_URI = "mongodb://localhost:27017/student_scores"

    # 在这里添加其他配置变量

    # Flask 应用的密钥
    # 用于保护会话（session）和其他安全相关的操作
    # 在生产环境中务必更改为一个随机且复杂的密钥
    SECRET_KEY = 'your_secret_key_here' # 在生产环境中更改此密钥