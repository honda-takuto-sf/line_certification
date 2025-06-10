# Pythonのイメージを使用
FROM --platform=linux/amd64 python:3.9

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを設定
WORKDIR /code

# 必要なパッケージをインストール
COPY requirements.txt /code/
RUN apt-get update && \
    apt-get install -y mariadb-client && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean

# エントリーポイントスクリプトをコピー
COPY entrypoint.sh /code/
COPY . /code/

# 実行コマンド
CMD ["/code/entrypoint.sh"]
