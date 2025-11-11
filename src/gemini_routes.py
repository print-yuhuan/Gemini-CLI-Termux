"""
Gemini API 路由模块 - 处理原生 Gemini API 端点

本模块提供原生 Gemini API 端点，直接代理至 Google API，
无需进行任何格式转换。
"""
import json
import logging
from fastapi import APIRouter, Request, Response, Depends

from .auth import authenticate_user
from .google_api_client import send_gemini_request, build_gemini_payload_from_native
from .config import SUPPORTED_MODELS

router = APIRouter()


@router.get("/v1beta/models")
async def gemini_list_models(request: Request, username: str = Depends(authenticate_user)):
    """
    原生 Gemini 模型列表端点

    返回 Gemini 格式的可用模型列表，与官方 Gemini API 保持一致。
    """
    
    try:
        logging.info("Gemini models list requested")
        
        models_response = {
            "models": SUPPORTED_MODELS
        }
        
        logging.info(f"Returning {len(SUPPORTED_MODELS)} Gemini models")
        return Response(
            content=json.dumps(models_response),
            status_code=200,
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logging.error(f"Failed to list Gemini models: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Failed to list models: {str(e)}",
                    "code": 500
                }
            }),
            status_code=500,
            media_type="application/json"
        )


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gemini_proxy(request: Request, full_path: str, username: str = Depends(authenticate_user)):
    """
    原生 Gemini API 通用代理端点

    直接代理所有原生 Gemini API 请求至 Google API。

    支持的路径格式包括：
    - /v1beta/models/{model}/generateContent
    - /v1beta/models/{model}/streamGenerateContent
    - /v1/models/{model}/generateContent
    - 以及其他类似路径
    """
    
    try:
        # 读取请求体数据
        post_data = await request.body()

        # 根据路径判断是否为流式请求
        is_streaming = "stream" in full_path.lower()

        # 从路径中提取模型名称
        # 路径格式示例：v1beta/models/gemini-1.5-pro/generateContent
        model_name = _extract_model_from_path(full_path)
        
        logging.info(f"Gemini proxy request: path={full_path}, model={model_name}, stream={is_streaming}")
        
        if not model_name:
            logging.error(f"Could not extract model name from path: {full_path}")
            return Response(
                content=json.dumps({
                    "error": {
                        "message": f"Could not extract model name from path: {full_path}",
                        "code": 400
                    }
                }),
                status_code=400,
                media_type="application/json"
            )
        
        # 解析请求体为 JSON 对象
        try:
            if post_data:
                incoming_request = json.loads(post_data)
            else:
                incoming_request = {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in request body: {str(e)}")
            return Response(
                content=json.dumps({
                    "error": {
                        "message": "Invalid JSON in request body",
                        "code": 400
                    }
                }),
                status_code=400,
                media_type="application/json"
            )
        
        # 构建符合 Google API 规范的请求负载
        gemini_payload = build_gemini_payload_from_native(incoming_request, model_name)

        # 向 Google API 发送请求并获取响应
        response = send_gemini_request(gemini_payload, is_streaming=is_streaming)

        # 记录响应状态信息
        if hasattr(response, 'status_code'):
            if response.status_code != 200:
                logging.error(f"Gemini API returned error: status={response.status_code}")
            else:
                logging.info(f"Successfully processed Gemini request for model: {model_name}")
        
        return response
        
    except Exception as e:
        logging.error(f"Gemini proxy error: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Proxy error: {str(e)}",
                    "code": 500
                }
            }),
            status_code=500,
            media_type="application/json"
        )


def _extract_model_from_path(path: str) -> str:
    """
    从 Gemini API 路径中提取模型名称

    路径格式示例：
    - "v1beta/models/gemini-1.5-pro/generateContent" -> "gemini-1.5-pro"
    - "v1/models/gemini-2.0-flash/streamGenerateContent" -> "gemini-2.0-flash"

    参数：
        path: API 路径字符串

    返回：
        提取的模型名称（不含 "models/" 前缀），若未找到则返回 None
    """
    parts = path.split('/')

    # 查找路径模式：.../models/{model_name}/...
    try:
        models_index = parts.index('models')
        if models_index + 1 < len(parts):
            model_name = parts[models_index + 1]
            # 移除操作后缀（如 ":streamGenerateContent" 或 ":generateContent"）
            if ':' in model_name:
                model_name = model_name.split(':')[0]
            # 返回纯模型名称（不含 "models/" 前缀）
            return model_name
    except ValueError:
        pass

    # 未匹配到预期模式，返回 None
    return None


@router.get("/v1/models")
async def gemini_list_models_v1(request: Request, username: str = Depends(authenticate_user)):
    """
    模型列表端点（v1 版本）

    为使用 /v1/models 路径的客户端提供备用端点，
    部分客户端可能使用此路径而非 /v1beta/models。
    """
    return await gemini_list_models(request, username)


# 健康检查端点
@router.get("/health")
async def health_check():
    """
    服务健康检查端点
    """
    return {"status": "healthy", "service": "Gemini-CLI-Termux"}