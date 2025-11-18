"""
OpenAI 格式转换器模块 - 处理 OpenAI 与 Gemini API 格式互转

本模块包含 OpenAI 和 Gemini API 之间请求/响应格式转换的全部逻辑。

主要功能：
1. 请求转换（OpenAI → Gemini）
   - 角色映射（assistant → model、system → user）
   - 参数映射（temperature、top_p、max_tokens 等）
   - 多模态内容处理（Markdown 图片 → inlineData）
   - 思考配置（reasoning_effort、thinkingBudget）

2. 响应转换（Gemini → OpenAI）
   - 非流式响应转换
   - 流式响应块转换
   - 思考内容分离（thought flag → reasoning_content）
   - 结束原因映射（STOP、MAX_TOKENS、SAFETY 等）
"""
import json
import time
import uuid
import re
from typing import Dict, Any

from .models import OpenAIChatCompletionRequest, OpenAIChatCompletionResponse
from .config import (
    DEFAULT_SAFETY_SETTINGS,
    is_search_model,
    get_base_model_name,
    get_thinking_budget,
    should_include_thoughts,
    is_nothinking_model,
    is_maxthinking_model
)


def openai_request_to_gemini(openai_request: OpenAIChatCompletionRequest) -> Dict[str, Any]:
    """
    转换 OpenAI 聊天完成请求为 Gemini 格式

    参数：
        openai_request: OpenAI 格式的请求对象

    返回：
        Gemini API 格式的字典
    """
    contents = []

    # 处理对话历史中的每条消息
    for message in openai_request.messages:
        role = message.role

        # 映射角色名称：OpenAI → Gemini
        # OpenAI: system, user, assistant
        # Gemini: user, model（无 system 角色，系统消息作为用户消息处理）
        if role == "assistant":
            role = "model"  # 助手 → 模型
        elif role == "system":
            role = "user"  # 系统 → 用户

        # 处理不同的内容类型（纯文本字符串或多部分列表）
        if isinstance(message.content, list):
            parts = []
            for part in message.content:
                if part.get("type") == "text":
                    text_value = part.get("text", "") or ""
                    # 提取 Markdown 图片（数据 URI）为内联图片，保留周围文本
                    pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
                    matches = list(pattern.finditer(text_value))
                    if not matches:
                        parts.append({"text": text_value})
                    else:
                        last_idx = 0
                        for m in matches:
                            url = m.group(1).strip().strip('"').strip("'")
                            # 提取图片前的文本内容
                            if m.start() > last_idx:
                                before = text_value[last_idx:m.start()]
                                if before:
                                    parts.append({"text": before})
                            # 处理数据 URI 格式图片：data:image/png;base64,xxxx
                            if url.startswith("data:"):
                                try:
                                    header, base64_data = url.split(",", 1)
                                    # header 格式示例：data:image/png;base64
                                    mime_type = ""
                                    if ":" in header:
                                        mime_type = header.split(":", 1)[1].split(";", 1)[0] or ""
                                    # 仅图片类型 MIME 转换为 inlineData 格式
                                    if mime_type.startswith("image/"):
                                        parts.append({
                                            "inlineData": {
                                                "mimeType": mime_type,
                                                "data": base64_data
                                            }
                                        })
                                    else:
                                        # 非图片数据 URI：保留为 Markdown 文本
                                        parts.append({"text": text_value[m.start():m.end()]})
                                except Exception:
                                    # 解析失败时保留原始 Markdown 文本
                                    parts.append({"text": text_value[m.start():m.end()]})
                            else:
                                # 非数据 URI：保留为 Markdown 文本（无法内联远程资源）
                                parts.append({"text": text_value[m.start():m.end()]})
                            last_idx = m.end()
                        # 提取最后一张图片后的文本内容
                        if last_idx < len(text_value):
                            tail = text_value[last_idx:]
                            if tail:
                                parts.append({"text": tail})
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {}).get("url")
                    if image_url:
                        # 解析数据 URI："data:image/jpeg;base64,{base64_image}"
                        try:
                            mime_type, base64_data = image_url.split(";")
                            _, mime_type = mime_type.split(":")
                            _, base64_data = base64_data.split(",")
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": base64_data
                                }
                            })
                        except ValueError:
                            continue
            contents.append({"role": role, "parts": parts})
        else:
            # 纯文本内容：提取 Markdown 图片（数据 URI）为内联图片
            text = message.content or ""
            parts = []
            # 转换 Markdown 图片格式：![alt](data:<mimeType>;base64,<data>)
            pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
            last_idx = 0
            for m in pattern.finditer(text):
                url = m.group(1).strip().strip('"').strip("'")
                # 提取图片前的文本内容
                if m.start() > last_idx:
                    before = text[last_idx:m.start()]
                    if before:
                        parts.append({"text": before})
                # 处理数据 URI 格式图片：data:image/png;base64,xxxx
                if url.startswith("data:"):
                    try:
                        header, base64_data = url.split(",", 1)
                        # header 格式示例：data:image/png;base64
                        mime_type = ""
                        if ":" in header:
                            mime_type = header.split(":", 1)[1].split(";", 1)[0] or ""
                        # 仅图片类型 MIME 转换为 inlineData 格式
                        if mime_type.startswith("image/"):
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": base64_data
                                }
                            })
                        else:
                            # 非图片数据 URI：保留为 Markdown 文本
                            parts.append({"text": text[m.start():m.end()]})
                    except Exception:
                        # 解析失败时保留原始 Markdown 文本
                        parts.append({"text": text[m.start():m.end()]})
                else:
                    # 非数据 URI：保留为 Markdown 文本（无法内联远程资源）
                    parts.append({"text": text[m.start():m.end()]})
                last_idx = m.end()
            # 提取最后一张图片后的文本内容
            if last_idx < len(text):
                tail = text[last_idx:]
                if tail:
                    parts.append({"text": tail})
            contents.append({"role": role, "parts": parts if parts else [{"text": text}]})

    # 映射 OpenAI 生成参数为 Gemini 格式
    generation_config = {}
    if openai_request.temperature is not None:
        generation_config["temperature"] = openai_request.temperature
    if openai_request.top_p is not None:
        generation_config["topP"] = openai_request.top_p
    if openai_request.max_tokens is not None:
        generation_config["maxOutputTokens"] = openai_request.max_tokens
    if openai_request.stop is not None:
        # 映射停止序列（Gemini 原生支持）
        if isinstance(openai_request.stop, str):
            generation_config["stopSequences"] = [openai_request.stop]
        elif isinstance(openai_request.stop, list):
            generation_config["stopSequences"] = openai_request.stop
    if openai_request.frequency_penalty is not None:
        # 映射频率惩罚参数
        generation_config["frequencyPenalty"] = openai_request.frequency_penalty
    if openai_request.presence_penalty is not None:
        # 映射存在惩罚参数
        generation_config["presencePenalty"] = openai_request.presence_penalty
    if openai_request.n is not None:
        # 映射完成数量（n → candidateCount）
        generation_config["candidateCount"] = openai_request.n
    if openai_request.seed is not None:
        # 映射随机种子（用于可重现输出）
        generation_config["seed"] = openai_request.seed
    if openai_request.response_format is not None:
        # 处理响应格式（如 JSON 模式）
        if openai_request.response_format.get("type") == "json_object":
            generation_config["responseMimeType"] = "application/json"
    
    # generation_config["enableEnhancedCivicAnswers"] = False

    # 构建最终请求负载
    request_payload = {
        "contents": contents,
        "generationConfig": generation_config,
        "safetySettings": DEFAULT_SAFETY_SETTINGS,
        "model": get_base_model_name(openai_request.model)  # 使用基础模型名称调用 API
    }

    # 为搜索模型启用 Google 搜索增强功能
    if is_search_model(openai_request.model):
        request_payload["tools"] = [{"googleSearch": {}}]

    # 配置思考模型的思考参数
    thinking_budget = None

    # 判断是否为显式思考模式（nothinking 或 maxthinking）
    if is_nothinking_model(openai_request.model) or is_maxthinking_model(openai_request.model):
        # 显式思考模式：忽略 reasoning_effort，使用预设预算
        thinking_budget = get_thinking_budget(openai_request.model)
    else:
        # 常规模型：检查是否指定了 reasoning_effort 参数
        reasoning_effort = getattr(openai_request, 'reasoning_effort', None)
        if reasoning_effort:
            base_model = get_base_model_name(openai_request.model)
            if reasoning_effort == "minimal":
                # 最小推理力度（与 nothinking 模式相同）
                if "gemini-2.5-flash" in base_model:
                    thinking_budget = 0
                elif "gemini-2.5-pro" in base_model or "gemini-3-pro" in base_model:
                    thinking_budget = 128
            elif reasoning_effort == "low":
                thinking_budget = 1000
            elif reasoning_effort == "medium":
                thinking_budget = -1
            elif reasoning_effort == "high":
                # 高推理力度（与 maxthinking 模式相同）
                if "gemini-2.5-flash" in base_model:
                    thinking_budget = 24576
                elif "gemini-2.5-pro" in base_model:
                    thinking_budget = 32768
                elif "gemini-3-pro" in base_model:
                    thinking_budget = 45000
        else:
            # 未指定 reasoning_effort，使用默认思考预算
            thinking_budget = get_thinking_budget(openai_request.model)

        if thinking_budget is not None:
            request_payload["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": thinking_budget,
                "includeThoughts": should_include_thoughts(openai_request.model)
            }
    
    return request_payload


def gemini_response_to_openai(gemini_response: Dict[str, Any], model: str) -> Dict[str, Any]:
    """
    转换 Gemini API 响应为 OpenAI 聊天完成格式

    参数：
        gemini_response: Gemini API 返回的响应
        model: 响应中包含的模型名称

    返回：
        OpenAI 聊天完成格式的字典
    """
    choices = []
    
    for candidate in gemini_response.get("candidates", []):
        role = candidate.get("content", {}).get("role", "assistant")

        # 映射角色名称：Gemini → OpenAI
        if role == "model":
            role = "assistant"

        # 提取并分离思考令牌与常规内容
        # Gemini API 使用 "thought": true 标记思考过程的文本片段
        parts = candidate.get("content", {}).get("parts", [])
        content_parts = []  # 常规内容（返回给用户）
        reasoning_content = ""  # 思考内容（推理过程）

        for part in parts:
            # 文本部分（可能包含思考令牌）
            if part.get("text") is not None:
                if part.get("thought", False):
                    # 思考令牌：添加到 reasoning_content
                    reasoning_content += part.get("text", "")
                else:
                    # 常规文本：添加到 content_parts
                    content_parts.append(part.get("text", ""))
                continue

            # 内联图片数据 -> 嵌入为 Markdown 数据 URI
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                mime = inline.get("mimeType") or "image/png"
                if isinstance(mime, str) and mime.startswith("image/"):
                    data_b64 = inline.get("data")
                    content_parts.append(f"![image](data:{mime};base64,{data_b64})")
                continue

        content = "\n\n".join([p for p in content_parts if p is not None])

        # 构建消息对象
        message = {
            "role": role,
            "content": content,
        }

        # 若存在思考内容则添加 reasoning_content 字段
        if reasoning_content:
            message["reasoning_content"] = reasoning_content
        
        choices.append({
            "index": candidate.get("index", 0),
            "message": message,
            "finish_reason": _map_finish_reason(candidate.get("finishReason")),
        })
    
    return {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": choices,
    }


def gemini_stream_chunk_to_openai(gemini_chunk: Dict[str, Any], model: str, response_id: str) -> Dict[str, Any]:
    """
    转换 Gemini 流式响应块为 OpenAI 流式格式

    参数：
        gemini_chunk: Gemini 流式响应中的单个数据块
        model: 响应中包含的模型名称
        response_id: 流式响应的一致标识符

    返回：
        OpenAI 流式格式的字典
    """
    choices = []
    
    for candidate in gemini_chunk.get("candidates", []):
        role = candidate.get("content", {}).get("role", "assistant")

        # 映射角色名称：Gemini → OpenAI
        if role == "model":
            role = "assistant"

        # 提取并分离思考令牌与常规内容
        parts = candidate.get("content", {}).get("parts", [])
        content_parts = []
        reasoning_content = ""

        for part in parts:
            # 文本部分（可能包含思考令牌）
            if part.get("text") is not None:
                if part.get("thought", False):
                    reasoning_content += part.get("text", "")
                else:
                    content_parts.append(part.get("text", ""))
                continue

            # 内联图片数据 -> 嵌入为 Markdown 数据 URI
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                mime = inline.get("mimeType") or "image/png"
                if isinstance(mime, str) and mime.startswith("image/"):
                    data_b64 = inline.get("data")
                    content_parts.append(f"![image](data:{mime};base64,{data_b64})")
                continue

        content = "\n\n".join([p for p in content_parts if p is not None])

        # 构建增量数据对象（delta）
        delta = {}
        if content:
            delta["content"] = content
        if reasoning_content:
            delta["reasoning_content"] = reasoning_content
        
        choices.append({
            "index": candidate.get("index", 0),
            "delta": delta,
            "finish_reason": _map_finish_reason(candidate.get("finishReason")),
        })
    
    return {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": choices,
    }


def _map_finish_reason(gemini_reason: str) -> str:
    """
    映射 Gemini 结束原因为 OpenAI 格式

    参数：
        gemini_reason: Gemini API 返回的结束原因

    返回：
        OpenAI 兼容的结束原因字符串
    """
    if gemini_reason == "STOP":
        return "stop"
    elif gemini_reason == "MAX_TOKENS":
        return "length"
    elif gemini_reason in ["SAFETY", "RECITATION"]:
        return "content_filter"
    else:
        return None