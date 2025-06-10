#!/bin/bash
# 静的ファイルをstatic_rootへ移動
python manage.py collectstatic --noinput
# gunicornを使用してDjangoアプリケーションを実行
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --worker-class gthread --workers 1 --threads 256 --error-logfile - --log-level warning --keep-alive 20
