bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
wsgi_app = "askme_nikitina.wsgi:application"
accesslog = "-"
errorlog = "-"
loglevel = "info"