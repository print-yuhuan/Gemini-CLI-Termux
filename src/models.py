from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any

# ==================== OpenAI 数据模型 ====================

class OpenAIChatMessage(BaseModel):
    """
    OpenAI 聊天消息模型

    表示对话历史中的单条消息，包含角色和内容信息。
    """
    role: str  # 消息角色：system（系统）、user（用户）、assistant（助手）
    content: Union[str, List[Dict[str, Any]]]  # 消息内容：纯文本字符串或多模态内容列表（支持文本、图片等）
    reasoning_content: Optional[str] = None  # 思考过程内容（可选），用于推理模型的中间思考步骤

class OpenAIChatCompletionRequest(BaseModel):
    """
    OpenAI 聊天完成请求模型

    定义聊天完成请求的所有参数，支持标准 OpenAI API 格式。
    """
    model: str  # 模型名称，如 "gemini-2.5-pro"
    messages: List[OpenAIChatMessage]  # 对话历史消息列表
    stream: bool = False  # 是否启用流式传输（SSE 格式）
    temperature: Optional[float] = None  # 温度参数（0.0-2.0），控制输出随机性，越高越随机
    top_p: Optional[float] = None  # 核采样参数（0.0-1.0），控制输出多样性
    max_tokens: Optional[int] = None  # 最大生成 token 数量限制
    stop: Optional[Union[str, List[str]]] = None  # 停止序列，遇到时停止生成
    frequency_penalty: Optional[float] = None  # 频率惩罚（-2.0 到 2.0），降低重复内容
    presence_penalty: Optional[float] = None  # 存在惩罚（-2.0 到 2.0），鼓励话题多样性
    n: Optional[int] = None  # 生成候选响应数量
    seed: Optional[int] = None  # 随机种子，用于可重现的输出
    response_format: Optional[Dict[str, Any]] = None  # 响应格式要求，如 {"type": "json_object"} 强制 JSON 输出
    reasoning_effort: Optional[str] = None  # 推理力度：minimal、low、medium、high，控制思考预算

    class Config:
        extra = "allow"  # 允许未明确定义的附加字段，提升兼容性

class OpenAIChatCompletionChoice(BaseModel):
    """
    OpenAI 聊天完成候选项模型

    表示单个生成结果候选项，包含消息内容和完成原因。
    """
    index: int  # 候选项索引，从 0 开始
    message: OpenAIChatMessage  # 生成的消息内容
    finish_reason: Optional[str] = None  # 完成原因：stop（正常结束）、length（达到长度限制）、content_filter（内容过滤）

class OpenAIChatCompletionResponse(BaseModel):
    """
    OpenAI 聊天完成响应模型

    表示完整的聊天完成响应，包含一个或多个候选结果。
    """
    id: str  # 响应的唯一标识符
    object: str  # 对象类型，固定为 "chat.completion"
    created: int  # 创建时间戳（Unix 时间）
    model: str  # 使用的模型名称
    choices: List[OpenAIChatCompletionChoice]  # 生成的候选结果列表

class OpenAIDelta(BaseModel):
    """
    OpenAI 流式响应增量模型

    表示流式传输中的增量内容块。
    """
    content: Optional[str] = None  # 增量文本内容
    reasoning_content: Optional[str] = None  # 增量思考过程内容

class OpenAIChatCompletionStreamChoice(BaseModel):
    """
    OpenAI 流式聊天完成候选项模型

    表示流式传输中的单个候选项增量数据。
    """
    index: int  # 候选项索引
    delta: OpenAIDelta  # 增量内容
    finish_reason: Optional[str] = None  # 完成原因（仅在最后一个块中出现）

class OpenAIChatCompletionStreamResponse(BaseModel):
    """
    OpenAI 流式聊天完成响应模型

    表示流式传输中的单个数据块（SSE 事件）。
    """
    id: str  # 响应的唯一标识符（整个流式会话保持一致）
    object: str  # 对象类型，固定为 "chat.completion.chunk"
    created: int  # 创建时间戳
    model: str  # 使用的模型名称
    choices: List[OpenAIChatCompletionStreamChoice]  # 候选项增量列表

# ==================== Gemini 数据模型 ====================

class GeminiPart(BaseModel):
    """
    Gemini 消息片段模型

    表示 Gemini 消息中的单个内容片段（文本、图片等）。
    """
    text: str  # 文本内容

class GeminiContent(BaseModel):
    """
    Gemini 消息内容模型

    表示完整的 Gemini 消息，包含角色和内容片段列表。
    """
    role: str  # 消息角色：user（用户）或 model（模型）
    parts: List[GeminiPart]  # 内容片段列表，支持多个文本或多模态内容

class GeminiRequest(BaseModel):
    """
    Gemini API 请求模型

    定义原生 Gemini API 请求的基本结构。
    """
    contents: List[GeminiContent]  # 对话内容列表

class GeminiCandidate(BaseModel):
    """
    Gemini 候选结果模型

    表示 Gemini API 返回的单个生成结果候选项。
    """
    content: GeminiContent  # 生成的内容
    finish_reason: Optional[str] = None  # 完成原因：STOP、MAX_TOKENS、SAFETY 等
    index: int  # 候选项索引

class GeminiResponse(BaseModel):
    """
    Gemini API 响应模型

    表示 Gemini API 返回的完整响应结构。
    """
    candidates: List[GeminiCandidate]  # 生成的候选结果列表