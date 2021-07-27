# fastapi-microservice-template

# 结构
README.md  说明
alembic.ini 数据库迁移alembic包的配置
requirements 依赖
start-worker shell文件，启动celery 工作（定时，异步，周期）
.env 环境变量，供pydantic使用
app 主应用包
    - api
        \v1 版本包，这种代码组织方式，方便系统升级
        deps.py
    - core
        celery_app.py celery的相关配置
        config.py 配置
        security.py 认证相关
    - db 数据库连接、初始化相关
        base_class.py
        base.py
        init_db.py
        session.py 数据库连接
    - models
        
    - schemas
    - service

    - main.py
    - utils.py
    - worker.py

