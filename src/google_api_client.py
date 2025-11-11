"""
Google API 客户端模块 - 负责与 Google Gemini API 的通信

本模块为 OpenAI 兼容层和原生 Gemini 端点提供统一的 API 通信接口。
"""
import json
import logging
import requests
from fastapi import Response
from fastapi.responses import StreamingResponse
from google.auth.transport.requests import Request as GoogleAuthRequest

from .auth import get_credentials, save_credentials, get_user_project_id, onboard_user
from .utils import get_user_agent
from .config import (
    CODE_ASSIST_ENDPOINT,
    DEFAULT_SAFETY_SETTINGS,
    get_base_model_name,
    is_search_model,
    get_thinking_budget,
    should_include_thoughts
)
import asyncio


def send_gemini_request(payload: dict, is_streaming: bool = False) -> Response:
    """
    向 Google Gemini API 发送请求

    参数：
        payload: Gemini 格式的请求负载
        is_streaming: 是否为流式请求

    返回：
        FastAPI Response 对象
    """
    # 获取并验证身份凭据
    creds = get_credentials()
    if not creds:
        return Response(
            content="Authentication failed. Please restart the proxy to log in.", 
            status_code=500
        )
    

    # 若凭据已过期且存在刷新令牌，则刷新凭据
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleAuthRequest())
            save_credentials(creds)
        except Exception as e:
            return Response(
                content="Token refresh failed. Please restart the proxy to re-authenticate.", 
                status_code=500
            )
    elif not creds.token:
        return Response(
            content="No access token. Please restart the proxy to re-authenticate.", 
            status_code=500
        )

    # 获取项目 ID 并完成用户引导流程
    proj_id = get_user_project_id(creds)
    if not proj_id:
        return Response(content="Failed to get user project ID.", status_code=500)
    
    onboard_user(creds, proj_id)

    # 构建包含项目信息的最终请求负载
    final_payload = {
        "model": payload.get("model"),
        "project": proj_id,
        "request": payload.get("request", {})
    }

    # 确定请求操作类型和目标 URL
    action = "streamGenerateContent" if is_streaming else "generateContent"
    target_url = f"{CODE_ASSIST_ENDPOINT}/v1internal:{action}"
    if is_streaming:
        target_url += "?alt=sse"

    # 构建 HTTP 请求头
    request_headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "User-Agent": get_user_agent(),
    }

    final_post_data = json.dumps(final_payload)

    # 发送请求
    try:
        if is_streaming:
            resp = requests.post(target_url, data=final_post_data, headers=request_headers, stream=True)
            return _handle_streaming_response(resp)
        else:
            resp = requests.post(target_url, data=final_post_data, headers=request_headers)
            return _handle_non_streaming_response(resp)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to Google API failed: {str(e)}")
        return Response(
            content=json.dumps({"error": {"message": f"Request failed: {str(e)}"}}),
            status_code=500,
            media_type="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error during Google API request: {str(e)}")
        return Response(
            content=json.dumps({"error": {"message": f"Unexpected error: {str(e)}"}}),
            status_code=500,
            media_type="application/json"
        )


def _handle_streaming_response(resp) -> StreamingResponse:
    """处理 Google API 返回的流式响应"""

    # 在流式传输前检查 HTTP 错误状态
    if resp.status_code != 200:
        logging.error(f"Google API returned status {resp.status_code}: {resp.text}")
        error_message = f"Google API error: {resp.status_code}"
        try:
            error_data = resp.json()
            if "error" in error_data:
                error_message = error_data["error"].get("message", error_message)
        except:
            pass
        
        # 以流式格式返回错误信息
        async def error_generator():
            error_response = {
                "error": {
                    "message": error_message,
                    "type": "invalid_request_error" if resp.status_code == 404 else "api_error",
                    "code": resp.status_code
                }
            }
            yield f'data: {json.dumps(error_response)}\n\n'.encode('utf-8')
        
        response_headers = {
            "Content-Type": "text/event-stream",
            "Content-Disposition": "attachment",
            "Vary": "Origin, X-Origin, Referer",
            "X-XSS-Protection": "0",
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "Server": "ESF"
        }
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers=response_headers,
            status_code=resp.status_code
        )
    
    async def stream_generator():
        try:
            with resp:
                for chunk in resp.iter_lines():
                    if chunk:
                        if not isinstance(chunk, str):
                            chunk = chunk.decode('utf-8', "ignore")
                            
                        if chunk.startswith('data: '):
                            chunk = chunk[len('data: '):]
                            
                            try:
                                obj = json.loads(chunk)
                                
                                if "response" in obj:
                                    response_chunk = obj["response"]
                                    response_json = json.dumps(response_chunk, separators=(',', ':'))
                                    response_line = f"data: {response_json}\n\n"
                                    yield response_line.encode('utf-8', "ignore")
                                    await asyncio.sleep(0)
                                else:
                                    obj_json = json.dumps(obj, separators=(',', ':'))
                                    yield f"data: {obj_json}\n\n".encode('utf-8', "ignore")
                            except json.JSONDecodeError:
                                continue
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Streaming request failed: {str(e)}")
            error_response = {
                "error": {
                    "message": f"Upstream request failed: {str(e)}",
                    "type": "api_error",
                    "code": 502
                }
            }
            yield f'data: {json.dumps(error_response)}\n\n'.encode('utf-8', "ignore")
        except Exception as e:
            logging.error(f"Unexpected error during streaming: {str(e)}")
            error_response = {
                "error": {
                    "message": f"An unexpected error occurred: {str(e)}",
                    "type": "api_error",
                    "code": 500
                }
            }
            yield f'data: {json.dumps(error_response)}\n\n'.encode('utf-8', "ignore")

    response_headers = {
        "Content-Type": "text/event-stream",
        "Content-Disposition": "attachment",
        "Vary": "Origin, X-Origin, Referer",
        "X-XSS-Protection": "0",
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "Server": "ESF"
    }
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers=response_headers
    )


def _handle_non_streaming_response(resp) -> Response:
    """处理 Google API 返回的非流式响应"""
    if resp.status_code == 200:
        try:
            google_api_response = resp.text
            if google_api_response.startswith('data: '):
                google_api_response = google_api_response[len('data: '):]
            google_api_response = json.loads(google_api_response)
            standard_gemini_response = google_api_response.get("response")
            return Response(
                content=json.dumps(standard_gemini_response),
                status_code=200,
                media_type="application/json; charset=utf-8"
            )
        except (json.JSONDecodeError, AttributeError) as e:
            logging.error(f"Failed to parse Google API response: {str(e)}")
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("Content-Type")
            )
    else:
        # 记录错误详细信息
        logging.error(f"Google API returned status {resp.status_code}: {resp.text}")

        # 解析错误响应并构建有意义的错误信息
        try:
            error_data = resp.json()
            if "error" in error_data:
                error_message = error_data["error"].get("message", f"API error: {resp.status_code}")
                error_response = {
                    "error": {
                        "message": error_message,
                        "type": "invalid_request_error" if resp.status_code == 404 else "api_error",
                        "code": resp.status_code
                    }
                }
                return Response(
                    content=json.dumps(error_response),
                    status_code=resp.status_code,
                    media_type="application/json"
                )
        except (json.JSONDecodeError, KeyError):
            pass

        # 若无法解析错误，则返回原始响应
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("Content-Type")
        )


def build_gemini_payload_from_openai(openai_payload: dict) -> dict:
    """
    从 OpenAI 转换后的请求构建 Gemini API 负载

    在 OpenAI 请求转换为 Gemini 格式后调用此函数。
    """
    # 从负载中提取模型名称
    model = openai_payload.get("model")
    
    # 获取安全设置（若无则使用默认配置）
    safety_settings = openai_payload.get("safetySettings", DEFAULT_SAFETY_SETTINGS)

    # 构建请求数据结构
    request_data = {
        "contents": openai_payload.get("contents"),
        "systemInstruction": openai_payload.get("systemInstruction"),
        "cachedContent": openai_payload.get("cachedContent"),
        "tools": openai_payload.get("tools"),
        "toolConfig": openai_payload.get("toolConfig"),
        "safetySettings": safety_settings,
        "generationConfig": openai_payload.get("generationConfig", {}),
    }
    
    # 过滤掉值为 None 的键
    request_data = {k: v for k, v in request_data.items() if v is not None}
    
    return {
        "model": model,
        "request": request_data
    }


def build_gemini_payload_from_native(native_request: dict, model_from_path: str) -> dict:
    """
    从原生 Gemini 请求构建 API 负载

    用于处理直接的 Gemini API 调用。
    """
    native_request["safetySettings"] = DEFAULT_SAFETY_SETTINGS
    
    if "generationConfig" not in native_request:
        native_request["generationConfig"] = {}
        
    # native_request["enableEnhancedCivicAnswers"] = False
    
    if "thinkingConfig" not in native_request["generationConfig"]:
        native_request["generationConfig"]["thinkingConfig"] = {}
    
    if "gemini-2.5-flash-image" not in model_from_path:
        # 根据模型类型配置思考预算
        thinking_budget = get_thinking_budget(model_from_path)
        include_thoughts = should_include_thoughts(model_from_path)
    
        native_request["generationConfig"]["thinkingConfig"]["includeThoughts"] = include_thoughts
        if "thinkingBudget" in native_request["generationConfig"]["thinkingConfig"]:
            pass
        else:
            native_request["generationConfig"]["thinkingConfig"]["thinkingBudget"] = thinking_budget
    
    # 为搜索模型启用 Google 搜索增强功能
    if is_search_model(model_from_path):
        if "tools" not in native_request:
            native_request["tools"] = []
        # 添加 Google 搜索工具（若尚未配置）
        if not any(tool.get("googleSearch") for tool in native_request["tools"]):
            native_request["tools"].append({"googleSearch": {}})
    
    return {
        "model": get_base_model_name(model_from_path),  # 使用基础模型名称调用 API
        "request": native_request
    }