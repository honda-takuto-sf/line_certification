# line_certification
LINEのログインフローの実験
.env
```
# データベース設定
DBNAME='test-local_db'
DBHOST='mysql'
DBUSER='test'
DBPASS='test''

# チャネルID
## それぞれ自身で作成したチャンネルから持ってきて貼り付けてください。
LINE_CLIENT_ID=
# チャネルシークレット
LINE_CLIENT_SECRET=

# コールバックURL
LINE_REDIRECT_URI=http://localhost:8000/api/auth/line/callback
```
