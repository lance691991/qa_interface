# fastapi-microservice-template

# 结构
- README.md  说明
- alembic.ini 数据库迁移alembic包的配置
- requirements 依赖
- start-worker shell文件，启动celery 工作（定时，异步，周期）
- .env 环境变量，供pydantic使用
- app 主应用包
    - api
        - v1 版本包，这种代码组织方式，方便系统升级
        - deps.py
    - core
        - celery_app.py celery的相关配置
        - config.py 配置
        - security.py 认证相关
    - db 数据库连接、初始化相关
        - base_class.py
        - base.py
        - init_db.py
        - session.py 数据库连接
    - models 模型存放的位置
    - schemas 使用pydantic定义的schema
    - service 业务逻辑，主要与crud相关的代码
    
    - main.py 主程序
    - utils.py 工具类，比如发送email
    - worker.py celery相关的worker

# 开发过程中的启动
- 命令行 uvicorn app.main:app
- 可以查看api localhost:4000/docs

# 部署过程中，使用dapr+容器

