# 每个爬虫对应的并发数
CONCURRENCY = 16
# 日志默认打印级别
LOG_LEVEL = 'INFO'
# HTTP 超时时间
DOWNLOAD_TIMEOUT = 60
# 是否验证证书
VERIFY_SSL = False
# 每个请求是否都需要新创建一个 session
NEW_SESSION = False
# 指定框架使用哪个下载器
DOWNLOADER = "pyler.core.downloader.AIOHTTPDownloader"
