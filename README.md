# fastapi-microservice-template

## 结构
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
    - alembic 这是数据库迁移的文件目录，可以手动修改，也可以自动生成。
        - version
        - env.py 这里可以配置自动生成。找到target_metadata 配置为模型即可
        ```
        import app.models
        target_metadata=[app.models.item.Item]  

        然后需要执行如下命令：
        alembic revision --autogenerate -m "说明信息" 会根据target_meta中的定义，自动在alembic目录下生成

        ```
    - main.py 主程序
    - utils.py 工具类，比如发送email
    - worker.py celery相关的worker
## 数据初始化
- sql类数据库的初始化，可以使用alembic
```
参照alembic的用法
执行 alembic upgrade head，就可以成功的创建库表甚至更多的操作，比如增加字段删除字段等；

```

## 开发过程中的启动
- 命令行 uvicorn app.main:app
- 可以查看api localhost:8000/docs

## 定时和周期性任务管理
- 准备工作：允许rabbitmq或者redis
- 修改app.core.celery_app中与redis或者rabbitmq连接的内容
- 采用celery
- 在项目目录中执行start-worker 即可

## 部署过程中，使用dapr+容器

## OPA服务授权

- 代码示例
```python
from app.core.security import ServiceAuthenticator

# 初始化认证器
authenticator = ServiceAuthenticator(service_name='test')

@app.post('/hello/hi')
async def hi(req: Request):
    # 传入请求进行验证
    await authenticator.auth(req=req)
    return
```
