from django.shortcuts import render

# Create your views here.

import os, logging, requests, jwt, time
from urllib.parse import urlencode
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@csrf_exempt
def line_login(request):
    state = str(int(time.time()))
    request.session["line_login_state"] = state

    params = {
        "response_type": "code",
        "client_id": os.environ["LINE_CLIENT_ID"],
        "redirect_uri": os.environ["LINE_REDIRECT_URI"],
        "state": state,
        "scope": "openid profile",
        "nonce": "secure_nonce_123",  # 推奨
    }
    url = "https://access.line.me/oauth2/v2.1/authorize?" + urlencode(params)

    logger.info(f"[LINE LOGIN] Redirect: {url}")
    return HttpResponseRedirect(url)

@csrf_exempt
def line_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    expected = request.session.get("line_login_state")

    if not code or not state or state != expected:
        logger.warning(f"[LINE CALLBACK] Invalid state or missing code")
        return HttpResponseBadRequest("Invalid state or code")

    token_url = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ["LINE_REDIRECT_URI"],
        "client_id": os.environ["LINE_CLIENT_ID"],
        "client_secret": os.environ["LINE_CLIENT_SECRET"],
    }

    response = requests.post(token_url, data=data, headers=headers)
    logger.info(f"[TOKEN] Response: {response.status_code} {response.text}")

    if response.status_code != 200:
        return HttpResponseBadRequest("Token fetch failed")

    token_data = response.json()
    id_token = token_data.get("id_token")

    # IDトークンデコード
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    logger.info(f"[LINE USER] {decoded}")

    # 最小レスポンス（画面表示なし）
    return JsonResponse({"message": "ログイン完了", "line_user": decoded})

@csrf_exempt
def line_unlink(request):
    access_token = request.POST.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post("https://api.line.me/oauth2/v2.1/revoke", headers=headers)
    logger.info(f"[UNLINK] {response.status_code} {response.text}")
    return JsonResponse({"status": response.status_code})
