import logging
import os
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from jwt import PyJWKClient, decode as jwt_decode, get_unverified_header
from jwt.exceptions import InvalidTokenError

from .models import LineUser

logger = logging.getLogger(__name__)

@csrf_exempt
def line_login(request):
    """
    LINEログイン用の認可エンドポイントにリダイレクトする。

    ユーザーが「LINEでログイン」ボタンを押すと呼び出される。
    認可リクエストに必要なパラメータ（client_id、redirect_uri、state、scope、nonce）を付与して、
    LINEのOAuth2.0認証ページへリダイレクトする。

    セキュリティ対策として、state（CSRF防止用）をセッションに保存する。

    Parameters:
        request (HttpRequest): DjangoのHTTPリクエストオブジェクト。

    Returns:
        HttpResponseRedirect: LINEの認可エンドポイントへのリダイレクトレスポンス。
    """
    state = str(uuid.uuid4())
    request.session["line_login_state"] = state

    params = {
        "response_type": "code",
        "client_id": os.environ["LINE_CLIENT_ID"],
        "redirect_uri": os.environ["LINE_REDIRECT_URI"],
        "state": state,
        "scope": "openid profile",
        "nonce": "secure_nonce_123",
    }

    url = "https://access.line.me/oauth2/v2.1/authorize?" + urlencode(params)
    logger.info(f"[LINE LOGIN] Redirect: {url}")
    return HttpResponseRedirect(url)

@csrf_exempt
def line_callback(request: HttpRequest):
    """
    LINEログインのコールバック処理。

    認可コードとstateを検証し、LINEからアクセストークンとIDトークンを取得。
    IDトークンを検証・デコードしてユーザー情報を取得し、アプリ内のLineUserテーブルに保存・更新する。
    最終的にフロントエンドのログイン成功画面へリダイレクトする。

    Parameters:
        request (HttpRequest): DjangoのHTTPリクエストオブジェクト
            - code: 認可コード
            - state: セッションに保存されたCSRF用トークンと一致する必要あり

    Returns:
        HttpResponseRedirect: ログイン成功ページへ遷移
        HttpResponseBadRequest: state不一致・トークン取得失敗など
    """
    code = request.GET.get("code")
    state = request.GET.get("state")
    expected_state = request.session.get("line_login_state")

    if not code or not state or state != expected_state:
        logger.warning("[LINE CALLBACK] Invalid or mismatched state/code")
        return HttpResponseBadRequest("Invalid state or code")

    # アクセストークン取得
    token_url = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ["LINE_REDIRECT_URI"],
        "client_id": os.environ["LINE_CLIENT_ID"],
        "client_secret": os.environ["LINE_CLIENT_SECRET"],
    }

    try:
        response = requests.post(token_url, data=data, headers=headers)
        logger.info(f"[LINE TOKEN] {response.status_code} {response.text}")
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"[LINE TOKEN ERROR] Failed to fetch token: {e}")
        return HttpResponseBadRequest("Token fetch failed")

    token_data = response.json()
    id_token = token_data.get("id_token")
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")

    # IDトークンを検証・デコード
    try:
        header = get_unverified_header(id_token)
        if header.get("alg") != "HS256":
            raise InvalidTokenError(f"Unsupported alg: {header.get('alg')}")

        # チャネルシークレットで署名検証してデコード
        decoded = jwt_decode(
            id_token,
            key=os.environ["LINE_CLIENT_SECRET"],
            algorithms=["HS256"],
            audience=os.environ["LINE_CLIENT_ID"],
            issuer="https://access.line.me",
        )
        logger.info(f"[LINE USER DECODED] {decoded}")

    except InvalidTokenError as e:
        logger.error(f"[JWT VERIFY ERROR] {e}")
        return HttpResponseBadRequest("Invalid ID token")
    except Exception as e:
        logger.error(f"[JWK ERROR] Failed to retrieve or parse JWK: {e}")
        return HttpResponseBadRequest("Invalid JWK or missing cryptography module")


    logger.info(f"[LINE USER DECODED] {decoded}")

    # ユーザー情報取得
    line_sub = decoded.get("sub")
    name = decoded.get("name")
    expire_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # DBに保存
    user, _ = LineUser.objects.get_or_create(line_sub=line_sub)
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.access_token_expire_at = expire_at
    user.save()

    # フロントエンドにリダイレクト
    return HttpResponseRedirect("http://localhost:3000/login/success")
