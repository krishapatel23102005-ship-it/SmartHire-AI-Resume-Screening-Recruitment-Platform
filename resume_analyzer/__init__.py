# Hook PyMySQL as MySQLdb for WSGI/ASGI servers running in production
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
