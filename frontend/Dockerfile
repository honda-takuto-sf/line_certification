# Node.js の公式イメージを使用
FROM node:18

# 作業ディレクトリを /app に設定
WORKDIR /app

# package.json & package-lock.json をコピーして依存関係をインストール
COPY package.json package-lock.json ./

# 依存関係のインストール
RUN npm install

# Next.js のソースコードをコピー
COPY . .

# HTTPS の証明書フォルダを作成
RUN mkdir -p /app/certificates

# Next.js サーバーを起動
CMD ["npm", "run", "dev"]
