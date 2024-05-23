# # 首先安装redis
# pip install redis
# 一、直连
import redis
coon = redis.Redis(host='127.0.0.1',port=6379,password='123456') # 拿到redis链接
coon.set('name','luwei') # 朝内存数据库存放key是name，value是luwei的字符串
coon.get('name') # 获取值  打印出来的值为luwei
# print(coon.get('name'))



# 二、使用连接池连接
import redis
pool = redis.ConnectionPool(host='127.0.0.1',port=6379,password='123456')# 连接池
coon = redis.Redis(connection_pool=pool)# 从池子里拿一个连接
coon.set('name','luwei')
coon.get('name')


# # 三、在Django里面进行连接
# pip install django_redis  #安装模块
# setting.py 中配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',# 缓存使用redis数据库储存
        'LOCATION': 'redis://127.0.0.1:6379/1',
        # 使用本地的6379端口(redis的默认端口)第1个数据库(redis共有16个数据库0-15)
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",# 使用django_redis的默认参数
            "PASSWORD":"123456"
        },
    },
}
# 配置完成后即可在view文件中连接redis
from django_redis import get_redis_connection
conn = get_redis_connection('default') # 建立连接 default为设置的连接名
conn.set('name','luwei')
conn.get('name')
name = conn.hget('name', 'luwei') # hget hash取值


# 四、Django框架中session存储到redis中的配置
# 第一种
# pip install django-redis-sessions  # 安装包
#  在Django项目的settings文件中增加下面的配置
# SESSION_ENGINE = 'redis_sessions.session'
# SESSION_REDIS_HOST = 'localhost'
# SESSION_REDIS_PORT = 6379
# SESSION_REDIS_DB = 1
# SESSION_REDIS_PASSWORD = '123456'
# SESSION_REDIS_PREFIX = 'session'

# 第二种 先将Django中的缓存设置为redis，然后将session的存储地方设置为Django的缓存中
# CACHES = {
#  "default": {
#   "BACKEND": "django_redis.cache.RedisCache",
#   # 把这里缓存你的redis服务器ip和port
#   "LOCATION": "redis://192.168.1.1:6379/1",
#   "OPTIONS": {
#    "CLIENT_CLASS": "django_redis.client.DefaultClient",
#    "PASSWORD":"admin"
#   }
#  }
# }
# # 设置redis存储session信息
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
