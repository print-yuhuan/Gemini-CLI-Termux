import os
import json
import base64
import time
import subprocess
import logging
from datetime import datetime
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBasic
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleAuthRequest

from .utils import get_user_agent, get_client_metadata
from .config import (
    CLIENT_ID, CLIENT_SECRET, SCOPES, CREDENTIAL_FILE,
    CODE_ASSIST_ENDPOINT, GEMINI_AUTH_PASSWORD
)

# --- 全局状态变量 ---
credentials = None
user_project_id = None
onboarding_complete = False
credentials_from_env = False  # 标记凭据来源是否为环境变量

security = HTTPBasic()

class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get("code", [None])[0]
        if code:
            _OAuthCallbackHandler.auth_code = code
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>OAuth authentication successful!</h1><p>You can close this window. Please check the proxy server logs to verify that onboarding completed successfully. No need to restart the proxy.</p>")
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication failed.</h1><p>Please try again.</p>")

def authenticate_user(request: Request):
    """使用多种方式进行用户身份验证"""
    # 优先级1：检查查询参数中的 API 密钥（Gemini 客户端兼容）
    api_key = request.query_params.get("key")
    if api_key and api_key == GEMINI_AUTH_PASSWORD:
        return "api_key_user"
    
    # 优先级2：检查 x-goog-api-key 请求头（Google SDK 格式）
    goog_api_key = request.headers.get("x-goog-api-key", "")
    if goog_api_key and goog_api_key == GEMINI_AUTH_PASSWORD:
        return "goog_api_key_user"

    # 优先级3：检查 Authorization 请求头中的 Bearer 令牌
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header[7:]
        if bearer_token == GEMINI_AUTH_PASSWORD:
            return "bearer_user"
    
    # 优先级4：检查 HTTP Basic 基本身份验证
    if auth_header.startswith("Basic "):
        try:
            encoded_credentials = auth_header[6:]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8', "ignore")
            username, password = decoded_credentials.split(':', 1)
            if password == GEMINI_AUTH_PASSWORD:
                return username
        except Exception:
            pass
    
    # 所有验证方式均失败
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials. Use HTTP Basic Auth, Bearer token, 'key' query parameter, or 'x-goog-api-key' header.",
        headers={"WWW-Authenticate": "Basic"},
    )

def save_credentials(creds, project_id=None):
    global credentials_from_env

    # 环境变量来源的凭据不写入文件，
    # 但若提供 project_id 且文件中缺失，则更新 project_id
    if credentials_from_env:
        if project_id and os.path.exists(CREDENTIAL_FILE):
            try:
                with open(CREDENTIAL_FILE, "r") as f:
                    existing_data = json.load(f)
                # 仅在文件中缺少 project_id 时更新
                if "project_id" not in existing_data:
                    existing_data["project_id"] = project_id
                    with open(CREDENTIAL_FILE, "w") as f:
                        json.dump(existing_data, f, indent=2)
                    logging.info(f"Added project_id {project_id} to existing credential file")
            except Exception as e:
                logging.warning(f"Could not update project_id in credential file: {e}")
        return
    
    creds_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "scopes": creds.scopes if creds.scopes else SCOPES,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    if creds.expiry:
        if creds.expiry.tzinfo is None:
            from datetime import timezone
            expiry_utc = creds.expiry.replace(tzinfo=timezone.utc)
        else:
            expiry_utc = creds.expiry
        # 保持 ISO 格式以实现向后兼容，确保加载时正确处理
        creds_data["expiry"] = expiry_utc.isoformat()
    
    if project_id:
        creds_data["project_id"] = project_id
    elif os.path.exists(CREDENTIAL_FILE):
        try:
            with open(CREDENTIAL_FILE, "r") as f:
                existing_data = json.load(f)
                if "project_id" in existing_data:
                    creds_data["project_id"] = existing_data["project_id"]
        except Exception:
            pass
    
    
    with open(CREDENTIAL_FILE, "w") as f:
        json.dump(creds_data, f, indent=2)
    

def get_credentials(allow_oauth_flow=True):
    """加载符合 gemini-cli OAuth2 流程的凭据"""
    global credentials, credentials_from_env, user_project_id
    
    if credentials and credentials.token:
        return credentials
    
    # 检查环境变量中的凭据（JSON 字符串格式）
    env_creds_json = os.getenv("GEMINI_CREDENTIALS")
    if env_creds_json:
        # 优先检查刷新令牌 - 若存在，应始终能够加载凭据
        try:
            raw_env_creds_data = json.loads(env_creds_json)
            
            # 安全保障：若存在 refresh_token，必须确保凭据加载成功
            if "refresh_token" in raw_env_creds_data and raw_env_creds_data["refresh_token"]:
                logging.info("Environment refresh token found - ensuring credentials load successfully")
                
                try:
                    creds_data = raw_env_creds_data.copy()

                    # 兼容不同的凭据格式
                    if "access_token" in creds_data and "token" not in creds_data:
                        creds_data["token"] = creds_data["access_token"]
                    
                    if "scope" in creds_data and "scopes" not in creds_data:
                        creds_data["scopes"] = creds_data["scope"].split()
                    
                    # 处理导致解析错误的有问题的过期格式
                    if "expiry" in creds_data:
                        expiry_str = creds_data["expiry"]
                        # 如果过期时间具有导致解析问题的时区信息，尝试修复它
                        if isinstance(expiry_str, str) and ("+00:00" in expiry_str or "Z" in expiry_str):
                            try:
                                # 尝试解析并重新格式化过期时间为 Google 凭据可处理的格式
                                from datetime import datetime
                                if "+00:00" in expiry_str:
                                    # 处理带时区偏移的 ISO 格式
                                    parsed_expiry = datetime.fromisoformat(expiry_str)
                                elif expiry_str.endswith("Z"):
                                    # 处理带 Z 后缀的 ISO 格式
                                    parsed_expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                                else:
                                    parsed_expiry = datetime.fromisoformat(expiry_str)
                                
                                # 转换为 Google 凭据库期望的 UTC 时间戳格式
                                import time
                                timestamp = parsed_expiry.timestamp()
                                creds_data["expiry"] = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
                                logging.info(f"Converted environment expiry format from '{expiry_str}' to '{creds_data['expiry']}'")
                            except Exception as expiry_error:
                                logging.warning(f"Could not parse environment expiry format '{expiry_str}': {expiry_error}, removing expiry field")
                                # 移除问题字段 - 凭据将视为已过期但仍可加载
                                del creds_data["expiry"]
                    
                    credentials = Credentials.from_authorized_user_info(creds_data, SCOPES)
                    credentials_from_env = True  # 标记为环境来源

                    # 从环境凭据中提取 project_id（若存在）
                    if "project_id" in raw_env_creds_data:
                        user_project_id = raw_env_creds_data["project_id"]
                        logging.info(f"Extracted project_id from environment credentials: {user_project_id}")

                    # 如果已过期且存在刷新令牌，尝试刷新
                    if credentials.expired and credentials.refresh_token:
                        try:
                            logging.info("Environment credentials expired, attempting refresh...")
                            credentials.refresh(GoogleAuthRequest())
                            logging.info("Environment credentials refreshed successfully")
                        except Exception as refresh_error:
                            logging.warning(f"Failed to refresh environment credentials: {refresh_error}")
                            logging.info("Using existing environment credentials despite refresh failure")
                    elif not credentials.expired:
                        logging.info("Environment credentials are still valid, no refresh needed")
                    elif not credentials.refresh_token:
                        logging.warning("Environment credentials expired but no refresh token available")
                    
                    return credentials
                    
                except Exception as parsing_error:
                    # 保障措施：即使解析失败，也尝试使用刷新令牌创建最小凭据
                    logging.warning(f"Failed to parse environment credentials normally: {parsing_error}")
                    logging.info("Attempting to create minimal environment credentials with refresh token")
                    
                    try:
                        minimal_creds_data = {
                            "client_id": raw_env_creds_data.get("client_id", CLIENT_ID),
                            "client_secret": raw_env_creds_data.get("client_secret", CLIENT_SECRET),
                            "refresh_token": raw_env_creds_data["refresh_token"],
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                        
                        credentials = Credentials.from_authorized_user_info(minimal_creds_data, SCOPES)
                        credentials_from_env = True  # 标记为环境来源

                        # 从环境凭据中提取 project_id（若存在）
                        if "project_id" in raw_env_creds_data:
                            user_project_id = raw_env_creds_data["project_id"]
                            logging.info(f"Extracted project_id from minimal environment credentials: {user_project_id}")
                        
                        # 强制刷新，因为我们没有有效的令牌
                        try:
                            logging.info("Refreshing minimal environment credentials...")
                            credentials.refresh(GoogleAuthRequest())
                            logging.info("Minimal environment credentials refreshed successfully")
                            return credentials
                        except Exception as refresh_error:
                            logging.error(f"Failed to refresh minimal environment credentials: {refresh_error}")
                            # 即使刷新失败也返回凭据 - 可能仍然有效
                            return credentials
                            
                    except Exception as minimal_error:
                        logging.error(f"Failed to create minimal environment credentials: {minimal_error}")
                        # 降级至基于文件的凭据
            else:
                logging.warning("No refresh token found in environment credentials")
                # 降级到基于文件的凭据
                
        except Exception as e:
            logging.error(f"Failed to parse environment credentials JSON: {e}")
            # 降级到基于文件的凭据
    
    # 检查凭据文件（若设置，CREDENTIAL_FILE 包含 GOOGLE_APPLICATION_CREDENTIALS 路径）
    if os.path.exists(CREDENTIAL_FILE):
        # 优先检查刷新令牌 - 若存在，应始终能够加载凭据
        try:
            with open(CREDENTIAL_FILE, "r") as f:
                raw_creds_data = json.load(f)
            
            # 安全保障：若存在 refresh_token，必须确保凭据加载成功
            if "refresh_token" in raw_creds_data and raw_creds_data["refresh_token"]:
                logging.info("Refresh token found - ensuring credentials load successfully")
                
                try:
                    creds_data = raw_creds_data.copy()

                    # 兼容不同的凭据格式
                    if "access_token" in creds_data and "token" not in creds_data:
                        creds_data["token"] = creds_data["access_token"]
                    
                    if "scope" in creds_data and "scopes" not in creds_data:
                        creds_data["scopes"] = creds_data["scope"].split()
                    
                    # 处理导致解析错误的有问题的过期格式
                    if "expiry" in creds_data:
                        expiry_str = creds_data["expiry"]
                        # 如果过期时间具有导致解析问题的时区信息，尝试修复它
                        if isinstance(expiry_str, str) and ("+00:00" in expiry_str or "Z" in expiry_str):
                            try:
                                # 尝试解析并重新格式化过期时间为 Google 凭据可处理的格式
                                from datetime import datetime
                                if "+00:00" in expiry_str:
                                    # 处理带时区偏移的 ISO 格式
                                    parsed_expiry = datetime.fromisoformat(expiry_str)
                                elif expiry_str.endswith("Z"):
                                    # 处理带 Z 后缀的 ISO 格式
                                    parsed_expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                                else:
                                    parsed_expiry = datetime.fromisoformat(expiry_str)
                                
                                # 转换为 Google 凭据库期望的 UTC 时间戳格式
                                import time
                                timestamp = parsed_expiry.timestamp()
                                creds_data["expiry"] = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
                                logging.info(f"Converted expiry format from '{expiry_str}' to '{creds_data['expiry']}'")
                            except Exception as expiry_error:
                                logging.warning(f"Could not parse expiry format '{expiry_str}': {expiry_error}, removing expiry field")
                                # 移除问题字段 - 凭据将视为已过期但仍可加载
                                del creds_data["expiry"]
                    
                    credentials = Credentials.from_authorized_user_info(creds_data, SCOPES)
                    # 若使用 GOOGLE_APPLICATION_CREDENTIALS，标记为环境来源
                    credentials_from_env = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

                    # 若已过期且有刷新令牌，尝试刷新
                    if credentials.expired and credentials.refresh_token:
                        try:
                            logging.info("File-based credentials expired, attempting refresh...")
                            credentials.refresh(GoogleAuthRequest())
                            logging.info("File-based credentials refreshed successfully")
                            save_credentials(credentials)
                        except Exception as refresh_error:
                            logging.warning(f"Failed to refresh file-based credentials: {refresh_error}")
                            logging.info("Using existing file-based credentials despite refresh failure")
                    elif not credentials.expired:
                        logging.info("File-based credentials are still valid, no refresh needed")
                    elif not credentials.refresh_token:
                        logging.warning("File-based credentials expired but no refresh token available")
                    
                    return credentials
                    
                except Exception as parsing_error:
                    # 保障措施：即使解析失败，也尝试使用刷新令牌创建最小凭据
                    logging.warning(f"Failed to parse credentials normally: {parsing_error}")
                    logging.info("Attempting to create minimal credentials with refresh token")
                    
                    try:
                        minimal_creds_data = {
                            "client_id": raw_creds_data.get("client_id", CLIENT_ID),
                            "client_secret": raw_creds_data.get("client_secret", CLIENT_SECRET),
                            "refresh_token": raw_creds_data["refresh_token"],
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                        
                        credentials = Credentials.from_authorized_user_info(minimal_creds_data, SCOPES)
                        credentials_from_env = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

                        # 强制刷新（因缺少有效令牌）
                        try:
                            logging.info("Refreshing minimal credentials...")
                            credentials.refresh(GoogleAuthRequest())
                            logging.info("Minimal credentials refreshed successfully")
                            save_credentials(credentials)
                            return credentials
                        except Exception as refresh_error:
                            logging.error(f"Failed to refresh minimal credentials: {refresh_error}")
                            # 即使刷新失败也返回凭据 - 可能仍然有效
                            return credentials
                            
                    except Exception as minimal_error:
                        logging.error(f"Failed to create minimal credentials: {minimal_error}")
                        # 作为最后手段，降级至新登录流程
            else:
                logging.warning("No refresh token found in credentials file")
                # 降级到新登录
                
        except Exception as e:
            logging.error(f"Failed to read credentials file {CREDENTIAL_FILE}: {e}")
            # 仅当文件完全无法读取时，降级至新登录流程

    # 仅在明确允许的情况下启动 OAuth 授权流程
    if not allow_oauth_flow:
        logging.info("OAuth flow not allowed - returning None (credentials will be required on first request)")
        return None

    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri="http://localhost:8080"
    )
    
    flow.oauth2session.scope = SCOPES
    
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes='true'
    )
    print(f"{'='*45}")
    print(f"正在自动跳转至 Google 账号授权页面")
    print(f"{auth_url}")
    print(f"{'='*45}\n")
    subprocess.run(['termux-open-url', auth_url])
    logging.info(f"正在自动跳转至 Google 账号授权页面：{auth_url}")
    
    server = HTTPServer(("", 8080), _OAuthCallbackHandler)
    server.handle_request()
    
    auth_code = _OAuthCallbackHandler.auth_code
    if not auth_code:
        return None

    import oauthlib.oauth2.rfc6749.parameters
    original_validate = oauthlib.oauth2.rfc6749.parameters.validate_token_parameters
    
    def patched_validate(params):
        try:
            return original_validate(params)
        except Warning:
            pass
    
    oauthlib.oauth2.rfc6749.parameters.validate_token_parameters = patched_validate
    
    try:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        credentials_from_env = False  # 标记为文件来源
        save_credentials(credentials)
        logging.info("Authentication successful! Credentials saved.")
        return credentials
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return None
    finally:
        oauthlib.oauth2.rfc6749.parameters.validate_token_parameters = original_validate

def onboard_user(creds, project_id):
    """确保用户已完成引导流程，匹配 gemini-cli setupUser 行为"""
    global onboarding_complete
    if onboarding_complete:
        return

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleAuthRequest())
            save_credentials(creds)
        except Exception as e:
            raise Exception(f"Failed to refresh credentials during onboarding: {str(e)}")
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "User-Agent": get_user_agent(),
    }
    
    load_assist_payload = {
        "cloudaicompanionProject": project_id,
        "metadata": get_client_metadata(project_id),
    }
    
    try:
        import requests
        resp = requests.post(
            f"{CODE_ASSIST_ENDPOINT}/v1internal:loadCodeAssist",
            data=json.dumps(load_assist_payload),
            headers=headers,
        )
        resp.raise_for_status()
        load_data = resp.json()
        
        tier = None
        if load_data.get("currentTier"):
            tier = load_data["currentTier"]
        else:
            for allowed_tier in load_data.get("allowedTiers", []):
                if allowed_tier.get("isDefault"):
                    tier = allowed_tier
                    break
            
            if not tier:
                tier = {
                    "name": "",
                    "description": "",
                    "id": "legacy-tier",
                    "userDefinedCloudaicompanionProject": True,
                }

        if tier.get("userDefinedCloudaicompanionProject") and not project_id:
            raise ValueError("This account requires setting the GOOGLE_CLOUD_PROJECT env var.")

        if load_data.get("currentTier"):
            onboarding_complete = True
            return

        onboard_req_payload = {
            "tierId": tier.get("id"),
            "cloudaicompanionProject": project_id,
            "metadata": get_client_metadata(project_id),
        }

        while True:
            onboard_resp = requests.post(
                f"{CODE_ASSIST_ENDPOINT}/v1internal:onboardUser",
                data=json.dumps(onboard_req_payload),
                headers=headers,
            )
            onboard_resp.raise_for_status()
            lro_data = onboard_resp.json()

            if lro_data.get("done"):
                onboarding_complete = True
                break
            
            time.sleep(5)

    except requests.exceptions.HTTPError as e:
        raise Exception(f"User onboarding failed. Please check your Google Cloud project permissions and try again. Error: {e.response.text if hasattr(e, 'response') else str(e)}")
    except Exception as e:
        raise Exception(f"User onboarding failed due to an unexpected error: {str(e)}")

def get_user_project_id(creds):
    """获取用户项目 ID，匹配 gemini-cli setupUser 逻辑"""
    global user_project_id

    # 优先级1：检查环境变量（始终检查，即使已设置 user_project_id）
    env_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if env_project_id:
        logging.info(f"Using project ID from GOOGLE_CLOUD_PROJECT environment variable: {env_project_id}")
        user_project_id = env_project_id
        save_credentials(creds, user_project_id)
        return user_project_id
    
    # 若已缓存 project_id 且无环境变量覆盖，直接使用
    if user_project_id:
        logging.info(f"Using cached project ID: {user_project_id}")
        return user_project_id

    # 优先级2：检查凭据文件中缓存的项目 ID
    if os.path.exists(CREDENTIAL_FILE):
        try:
            with open(CREDENTIAL_FILE, "r") as f:
                creds_data = json.load(f)
                cached_project_id = creds_data.get("project_id")
                if cached_project_id:
                    logging.info(f"Using cached project ID from credential file: {cached_project_id}")
                    user_project_id = cached_project_id
                    return user_project_id
        except Exception as e:
            logging.warning(f"Could not read project_id from credential file: {e}")

    # 优先级3：通过 API 调用获取项目 ID
    # 确保拥有 API 调用所需的有效凭据
    if creds.expired and creds.refresh_token:
        try:
            logging.info("Refreshing credentials before project ID discovery...")
            creds.refresh(GoogleAuthRequest())
            save_credentials(creds)
            logging.info("Credentials refreshed successfully for project ID discovery")
        except Exception as e:
            logging.error(f"Failed to refresh credentials while getting project ID: {e}")
            # 继续使用现有凭据 - 可能仍然有效
    
    if not creds.token:
        raise Exception("No valid access token available for project ID discovery")
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "User-Agent": get_user_agent(),
    }
    
    probe_payload = {
        "metadata": get_client_metadata(),
    }

    try:
        import requests
        logging.info("Attempting to discover project ID via API call...")
        resp = requests.post(
            f"{CODE_ASSIST_ENDPOINT}/v1internal:loadCodeAssist",
            data=json.dumps(probe_payload),
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        discovered_project_id = data.get("cloudaicompanionProject")
        if not discovered_project_id:
            raise ValueError("Could not find 'cloudaicompanionProject' in loadCodeAssist response.")

        logging.info(f"Discovered project ID via API: {discovered_project_id}")
        user_project_id = discovered_project_id
        save_credentials(creds, user_project_id)
        
        return user_project_id
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error during project ID discovery: {e}")
        if hasattr(e, 'response') and e.response:
            logging.error(f"Response status: {e.response.status_code}, body: {e.response.text}")
        raise Exception(f"Failed to discover project ID via API: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during project ID discovery: {e}")
        raise Exception(f"Failed to discover project ID: {e}")