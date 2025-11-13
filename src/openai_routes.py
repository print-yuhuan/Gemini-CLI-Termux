"""
OpenAI API 路由模块 - 处理 OpenAI 兼容端点

本模块提供 OpenAI 兼容接口，负责请求/响应格式转换，
并委托给 Google API 客户端进行实际处理。

主要功能：
1. OpenAI 聊天完成端点（/v1/chat/completions）
   - 支持流式和非流式响应
   - 自动转换请求/响应格式
2. OpenAI 模型列表端点（/v1/models）
   - 将 Gemini 模型列表转换为 OpenAI 格式
3. 错误处理与格式转换
"""
import json
import uuid
import asyncio
import logging
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import StreamingResponse

from .auth import authenticate_user
from .models import OpenAIChatCompletionRequest
from .openai_transformers import (
    openai_request_to_gemini,
    gemini_response_to_openai,
    gemini_stream_chunk_to_openai
)
from .google_api_client import send_gemini_request, build_gemini_payload_from_openai

router = APIRouter()


@router.post("/v1/chat/completions")
async def openai_chat_completions(
    request: OpenAIChatCompletionRequest, 
    http_request: Request, 
    username: str = Depends(authenticate_user)
):
    """
    OpenAI 兼容的聊天完成端点

    将 OpenAI 格式请求转换为 Gemini 格式，发送至 Google API，
    再将响应转换回 OpenAI 格式返回。
    """
    
    try:
        logging.info(f"OpenAI chat completion request: model={request.model}, stream={request.stream}")

        # 转换 OpenAI 请求为 Gemini 格式
        gemini_request_data = openai_request_to_gemini(request)

        # 构建符合 Google API 规范的请求负载
        gemini_payload = build_gemini_payload_from_openai(gemini_request_data)
        
    except Exception as e:
        logging.error(f"Error processing OpenAI request: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Request processing failed: {str(e)}",
                    "type": "invalid_request_error",
                    "code": 400
                }
            }),
            status_code=400,
            media_type="application/json"
        )
    
    if request.stream:
        # 流式响应处理（Server-Sent Events 格式）
        async def openai_stream_generator():
            """异步生成器：逐块转换并发送流式响应"""
            try:
                # 向 Google API 发送流式请求
                response = send_gemini_request(gemini_payload, is_streaming=True)

                if isinstance(response, StreamingResponse):
                    # 生成唯一的响应 ID（整个流式会话保持一致）
                    response_id = "chatcmpl-" + str(uuid.uuid4())
                    logging.info(f"Starting streaming response: {response_id}")
                    
                    async for chunk in response.body_iterator:
                        if isinstance(chunk, bytes):
                            chunk = chunk.decode('utf-8', "ignore")
                        
                        if chunk.startswith('data: '):
                            try:
                                # 解析 Gemini 流式数据块
                                chunk_data = chunk[6:]  # 移除 'data: ' 前缀
                                gemini_chunk = json.loads(chunk_data)

                                # 检查是否为错误数据块
                                if "error" in gemini_chunk:
                                    logging.error(f"Error in streaming response: {gemini_chunk['error']}")
                                    # 转换错误信息为 OpenAI 格式
                                    error_data = {
                                        "error": {
                                            "message": gemini_chunk["error"].get("message", "Unknown error"),
                                            "type": gemini_chunk["error"].get("type", "api_error"),
                                            "code": gemini_chunk["error"].get("code")
                                        }
                                    }
                                    yield f"data: {json.dumps(error_data)}\n\n"
                                    yield "data: [DONE]\n\n"
                                    return
                                
                                # 转换为 OpenAI 流式格式
                                openai_chunk = gemini_stream_chunk_to_openai(
                                    gemini_chunk,
                                    request.model,
                                    response_id
                                )

                                # 以 SSE 格式发送数据块
                                yield f"data: {json.dumps(openai_chunk)}\n\n"
                                await asyncio.sleep(0)
                                
                            except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
                                logging.warning(f"Failed to parse streaming chunk: {str(e)}")
                                continue
                    
                    # 发送流式响应结束标记
                    yield "data: [DONE]\n\n"
                    logging.info(f"Completed streaming response: {response_id}")
                else:
                    # 错误处理 - 处理异常 Response 对象
                    error_msg = "Streaming request failed"
                    status_code = 500
                    
                    if hasattr(response, 'status_code'):
                        status_code = response.status_code
                        error_msg += f" (status: {status_code})"
                    
                    if hasattr(response, 'body'):
                        try:
                            # 解析错误响应内容
                            error_body = response.body
                            if isinstance(error_body, bytes):
                                error_body = error_body.decode('utf-8', "ignore")
                            error_data = json.loads(error_body)
                            if "error" in error_data:
                                error_msg = error_data["error"].get("message", error_msg)
                        except:
                            pass
                    
                    logging.error(f"Streaming request failed: {error_msg}")
                    error_data = {
                        "error": {
                            "message": error_msg,
                            "type": "invalid_request_error" if status_code == 404 else "api_error",
                            "code": status_code
                        }
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    yield "data: [DONE]\n\n"
            except Exception as e:
                logging.error(f"Streaming error: {str(e)}")
                error_data = {
                    "error": {
                        "message": f"Streaming failed: {str(e)}",
                        "type": "api_error",
                        "code": 500
                    }
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            openai_stream_generator(), 
            media_type="text/event-stream"
        )
    
    else:
        # 非流式响应处理
        try:
            response = send_gemini_request(gemini_payload, is_streaming=False)
            
            if isinstance(response, Response) and response.status_code != 200:
                # 处理 Google API 返回的错误响应
                logging.error(f"Gemini API error: status={response.status_code}")

                try:
                    # 解析并转换错误响应为 OpenAI 格式
                    error_body = response.body
                    if isinstance(error_body, bytes):
                        error_body = error_body.decode('utf-8', "ignore")
                    
                    error_data = json.loads(error_body)
                    if "error" in error_data:
                        # 转换 Google API 错误为 OpenAI 格式
                        openai_error = {
                            "error": {
                                "message": error_data["error"].get("message", f"API error: {response.status_code}"),
                                "type": error_data["error"].get("type", "invalid_request_error" if response.status_code == 404 else "api_error"),
                                "code": error_data["error"].get("code", response.status_code)
                            }
                        }
                        return Response(
                            content=json.dumps(openai_error),
                            status_code=response.status_code,
                            media_type="application/json"
                        )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                # 返回备用错误响应
                return Response(
                    content=json.dumps({
                        "error": {
                            "message": f"API error: {response.status_code}",
                            "type": "invalid_request_error" if response.status_code == 404 else "api_error",
                            "code": response.status_code
                        }
                    }),
                    status_code=response.status_code,
                    media_type="application/json"
                )
            
            try:
                # 解析 Gemini 响应并转换为 OpenAI 格式
                gemini_response = json.loads(response.body)
                openai_response = gemini_response_to_openai(gemini_response, request.model)
                
                logging.info(f"Successfully processed non-streaming response for model: {request.model}")
                return openai_response
                
            except (json.JSONDecodeError, AttributeError) as e:
                logging.error(f"Failed to parse Gemini response: {str(e)}")
                return Response(
                    content=json.dumps({
                        "error": {
                            "message": f"Failed to process response: {str(e)}",
                            "type": "api_error",
                            "code": 500
                        }
                    }),
                    status_code=500,
                    media_type="application/json"
                )
        except Exception as e:
            logging.error(f"Non-streaming request failed: {str(e)}")
            return Response(
                content=json.dumps({
                    "error": {
                        "message": f"Request failed: {str(e)}",
                        "type": "api_error",
                        "code": 500
                    }
                }),
                status_code=500,
                media_type="application/json"
            )


@router.get("/v1/models")
async def openai_list_models(username: str = Depends(authenticate_user)):
    """
    OpenAI 兼容的模型列表端点

    返回 OpenAI 格式的可用模型列表。
    """
    
    try:
        logging.info("OpenAI models list requested")

        # 转换 Gemini 模型列表为 OpenAI 格式
        from .config import SUPPORTED_MODELS

        openai_models = []
        for model in SUPPORTED_MODELS:
            # 移除 "models/" 前缀以兼容 OpenAI 格式
            model_id = model["name"].replace("models/", "")
            openai_models.append({
                "id": model_id,
                "object": "model",
                "created": 1677610602,  # Static timestamp
                "owned_by": "google",
                "permission": [
                    {
                        "id": "modelperm-" + model_id.replace("/", "-"),
                        "object": "model_permission",
                        "created": 1677610602,
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": False,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group": None,
                        "is_blocking": False
                    }
                ],
                "root": model_id,
                "parent": None
            })
        
        logging.info(f"Returning {len(openai_models)} models")
        return {
            "object": "list",
            "data": openai_models
        }
        
    except Exception as e:
        logging.error(f"Failed to list models: {str(e)}")
        return Response(
            content=json.dumps({
                "error": {
                    "message": f"Failed to list models: {str(e)}",
                    "type": "api_error",
                    "code": 500
                }
            }),
            status_code=500,
            media_type="application/json"
        )


