# 学生成绩管理系统

这是一个基于 Flask 和 MongoDB 的学生成绩管理系统。

## 功能

- 学生成绩管理（录入、查询、修改、删除）
- 班级管理
- 学院管理
- 课程管理
- 学生成绩数据分析（总学生数、平均成绩、不及格人数等）
- 用户认证（待实现或基础实现）
- 管理员仪表盘

## 技术栈

- **后端**: Python, Flask
- **数据库**: MongoDB
- **前端**: HTML, CSS, JavaScript, Bootstrap
- **依赖管理**: pip, requirements.txt

## 安装和运行

1.  **克隆仓库**

    ```bash
    git clone <仓库地址>
    cd 学生成绩管理系统
    ```

2.  **创建并激活虚拟环境**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

4.  **配置数据库**

    确保您已经安装并运行了 MongoDB 数据库。修改 `config.py` 文件中的 `MONGO_URI` 连接字符串以匹配您的数据库配置。

    ```python
    # config.py
    class Config:
        MONGO_URI = "mongodb://localhost:27017/student_scores"
        SECRET_KEY = 'your_secret_key_here'
    ```

5.  **运行应用**

    ```bash
    flask run
    ```

    应用将在默认端口（通常是 5000）上运行。在浏览器中访问 `http://127.0.0.1:5000/`。

## 项目结构

项目的目录结构如下：

```
/学生成绩管理系统
├── .venv/                  # 虚拟环境目录
├── README.md               # 项目说明文件
├── app.py                  # 应用程序入口
├── config.py               # 配置文件
├── generate_data.py        # 数据生成脚本
├── models/                 # 数据模型目录
│   ├── __init__.py
│   ├── classroom.py
│   ├── college.py
│   ├── course.py
│   ├── db.py
│   ├── score.py
│   └── student.py
├── requirements.txt        # 依赖包列表
├── routes/                 # 路由目录
│   ├── __init__.py
│   ├── classrooms.py
│   ├── colleges.py
│   ├── courses.py
│   ├── index.py
│   ├── scores.py
│   └── students.py
├── static/                 # 静态文件目录
│   ├── css/
│   ├── icons/
│   ├── img/
│   └── js/
└── templates/             # 模板文件目录
    ├── add_score.html
    ├── admin_dashboard.html
    ├── base.html
    ├── classrooms/
    ├── colleges/
    ├── courses/
    ├── edit_score.html
    ├── includes/
    ├── scores/
    └── students_list.html
```

## 使用说明

1. **启动应用程序**

    确保 MongoDB 正在运行，然后在项目根目录下执行以下命令启动应用程序：

    ```bash
    flask run
    ```

2. **访问应用程序**

    在浏览器中打开 `http://127.0.0.1:5000` 访问应用程序。

## 常见问题解答

- **如何添加新学院？**
  在“学院管理”页面点击“新增学院”按钮，填写相关信息后提交。

- **如何删除学院？**
  在“学院管理”页面点击“删除”按钮，确认后即可删除学院。

- **如何恢复已删除的学院？**
  在“学院管理”页面点击“恢复”按钮，确认后即可恢复学院。

## 贡献

欢迎贡献！请提交 Pull Request 或报告问题。

## 许可证

本项目采用 [许可证名称] 许可协议。