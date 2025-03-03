# 并行工作进程数
import os
workers = (2 * os.cpu_count()) + 1  # 自动计算：CPU核心数×2+1

# 每个worker的线程数
threads = 4

# 绑定地址
bind = '0.0.0.0:17771'

# 超时设置（秒）
timeout = 30
graceful_timeout = 10

# 日志配置
accesslog = 'access.log'
errorlog = 'error.log'
loglevel = 'info'

# 最大并发连接数
worker_connections = 1000

# 防止内存泄漏
max_requests = 1000
max_requests_jitter = 50