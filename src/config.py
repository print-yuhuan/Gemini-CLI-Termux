"""
Gemini-CLI-Termux 代理服务器配置模块

集中管理所有配置常量，避免模块间重复定义。
"""
import os

# 加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 未安装
except Exception:
    pass  # .env 文件加载失败

# API 端点
CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com"

# 客户端配置
CLI_VERSION = "0.16.0"  # 当前 Gemini-CLI 版本

# OAuth 配置
CLIENT_ID = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# 文件路径
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIAL_FILE = os.path.join(SCRIPT_DIR, os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "oauth_creds.json"))

# 身份验证
GEMINI_AUTH_PASSWORD = os.getenv("GEMINI_AUTH_PASSWORD", "123")

# Google API 默认安全配置
# 配置说明：所有类别均设置为 BLOCK_NONE（不阻止），允许模型处理所有类型的内容
DEFAULT_SAFETY_SETTINGS = [
    # 1. HARM_CATEGORY_UNSPECIFIED - 默认值，未使用（保留用于兼容性）
    {"category": "HARM_CATEGORY_UNSPECIFIED", "threshold": "BLOCK_NONE"},

    # 2. HARM_CATEGORY_HATE_SPEECH - 仇恨言论：宣扬暴力或基于某些属性煽动对个人或群体仇恨的内容
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},

    # 3. HARM_CATEGORY_DANGEROUS_CONTENT - 危险内容：宣传、促进或支持危险活动的内容
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},

    # 4. HARM_CATEGORY_HARASSMENT - 骚扰：辱骂性、威胁性或旨在欺凌、折磨或嘲笑的内容
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},

    # 5. HARM_CATEGORY_SEXUALLY_EXPLICIT - 色情内容：包含露骨性材料的内容
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},

    # 6. HARM_CATEGORY_CIVIC_INTEGRITY - 公民诚信（已弃用，保留用于向后兼容）
    {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"},

    # 7. HARM_CATEGORY_IMAGE_HATE - 图像仇恨言论：包含仇恨言论的图像
    {"category": "HARM_CATEGORY_IMAGE_HATE", "threshold": "BLOCK_NONE"},

    # 8. HARM_CATEGORY_IMAGE_DANGEROUS_CONTENT - 图像危险内容：包含危险内容的图像
    {"category": "HARM_CATEGORY_IMAGE_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},

    # 9. HARM_CATEGORY_IMAGE_HARASSMENT - 图像骚扰：包含骚扰内容的图像
    {"category": "HARM_CATEGORY_IMAGE_HARASSMENT", "threshold": "BLOCK_NONE"},

    # 10. HARM_CATEGORY_IMAGE_SEXUALLY_EXPLICIT - 图像色情内容：包含露骨性内容的图像
    {"category": "HARM_CATEGORY_IMAGE_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},

    # 11. HARM_CATEGORY_JAILBREAK - 越狱提示：旨在绕过安全过滤器的提示
    {"category": "HARM_CATEGORY_JAILBREAK", "threshold": "BLOCK_NONE"},
]

# 基础模型列表（不含搜索和思考变体）
BASE_MODELS = [
    {
        "name": "models/gemini-2.5-pro-preview-06-05",
        "version": "001",
        "displayName": "Gemini 2.5 Pro Preview 06-05",
        "description": "Gemini 2.5 Pro Preview 06-05",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 65535,
        "supportedGenerationMethods": ["generateContent", "streamGenerateContent"],
        "temperature": 1.0,
        "maxTemperature": 2.0,
        "topP": 0.95,
        "topK": 64
    },
    {
        "name": "models/gemini-2.5-pro",
        "version": "001",
        "displayName": "Gemini 2.5 Pro",
        "description": "Gemini 2.5 Pro",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 65535,
        "supportedGenerationMethods": ["generateContent", "streamGenerateContent"],
        "temperature": 1.0,
        "maxTemperature": 2.0,
        "topP": 0.95,
        "topK": 64
    },
    {
        "name": "models/gemini-3-pro-preview",
        "version": "001",
        "displayName": "Gemini 3 Pro Preview",
        "description": "Gemini 3 Pro Preview",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 65535,
        "supportedGenerationMethods": ["generateContent", "streamGenerateContent"],
        "temperature": 1.0,
        "maxTemperature": 2.0,
        "topP": 0.95,
        "topK": 64
    },
    {
        "name": "models/gemini-2.5-flash",
        "version": "001",
        "displayName": "Gemini 2.5 Flash",
        "description": "Gemini 2.5 Flash",
        "inputTokenLimit": 1048576,
        "outputTokenLimit": 65535,
        "supportedGenerationMethods": ["generateContent", "streamGenerateContent"],
        "temperature": 1.0,
        "maxTemperature": 2.0,
        "topP": 0.95,
        "topK": 64
    },
]

# 生成搜索增强模型变体
def _generate_search_variants():
    """
    为支持内容生成的模型生成搜索变体

    为每个基础模型创建一个带有 Google 搜索增强功能的变体。
    这些变体在模型名称后添加 "-search" 后缀，并启用 Google 搜索工具。

    返回：
        list: 搜索增强模型变体列表
    """
    search_models = []
    for model in BASE_MODELS:
        # 仅为支持内容生成的模型创建搜索变体
        if "generateContent" in model["supportedGenerationMethods"]:
            search_variant = model.copy()  # 深拷贝基础模型配置
            search_variant["name"] = model["name"] + "-search"  # 添加 -search 后缀
            search_variant["displayName"] = model["displayName"] + " with Google Search"
            search_variant["description"] = model["description"] + " (includes Google Search grounding)"
            search_models.append(search_variant)
    return search_models

# 生成思考模式变体
def _generate_thinking_variants():
    """
    为支持思考的模型生成 nothinking 和 maxthinking 变体

    为具有思考能力的模型创建两种变体：
    1. nothinking 变体：最小化思考预算，快速响应
    2. maxthinking 变体：最大化思考预算，深度推理

    仅适用于支持思考的模型系列：gemini-2.5-flash、gemini-2.5-pro、gemini-3-pro

    返回：
        list: 思考模式变体列表
    """
    thinking_models = []
    for model in BASE_MODELS:
        # 仅为支持内容生成且具备思考能力的模型创建变体
        # 适用模型：gemini-2.5-flash、gemini-2.5-pro、gemini-3-pro
        if ("generateContent" in model["supportedGenerationMethods"] and
            ("gemini-2.5-flash" in model["name"] or "gemini-2.5-pro" in model["name"] or "gemini-3-pro" in model["name"])):

            # 创建 -nothinking 变体（禁用或最小化思考）
            nothinking_variant = model.copy()
            nothinking_variant["name"] = model["name"] + "-nothinking"
            nothinking_variant["displayName"] = model["displayName"] + " (No Thinking)"
            nothinking_variant["description"] = model["description"] + " (thinking disabled)"
            thinking_models.append(nothinking_variant)

            # 创建 -maxthinking 变体（最大思考预算）
            maxthinking_variant = model.copy()
            maxthinking_variant["name"] = model["name"] + "-maxthinking"
            maxthinking_variant["displayName"] = model["displayName"] + " (Max Thinking)"
            maxthinking_variant["description"] = model["description"] + " (maximum thinking budget)"
            thinking_models.append(maxthinking_variant)
    return thinking_models

# 生成搜索与思考的组合变体
def _generate_combined_variants():
    """生成搜索增强与思考模式的组合变体"""
    combined_models = []
    for model in BASE_MODELS:
        # 仅为支持内容生成的模型创建组合变体
        # 适用模型：gemini-2.5-flash、gemini-2.5-pro、gemini-3-pro
        if ("generateContent" in model["supportedGenerationMethods"] and
            ("gemini-2.5-flash" in model["name"] or "gemini-2.5-pro" in model["name"] or "gemini-3-pro" in model["name"])):
            
            # 搜索 + 无思考模式
            search_nothinking = model.copy()
            search_nothinking["name"] = model["name"] + "-search-nothinking"
            search_nothinking["displayName"] = model["displayName"] + " with Google Search (No Thinking)"
            search_nothinking["description"] = model["description"] + " (includes Google Search grounding, thinking disabled)"
            combined_models.append(search_nothinking)

            # 搜索 + 最大思考模式
            search_maxthinking = model.copy()
            search_maxthinking["name"] = model["name"] + "-search-maxthinking"
            search_maxthinking["displayName"] = model["displayName"] + " with Google Search (Max Thinking)"
            search_maxthinking["description"] = model["description"] + " (includes Google Search grounding, maximum thinking budget)"
            combined_models.append(search_maxthinking)
    return combined_models

# 完整的支持模型列表（包括基础模型、搜索变体和思考变体）
# 合并所有模型并按名称排序，以便将变体分组展示
all_models = BASE_MODELS + _generate_search_variants() + _generate_thinking_variants()
SUPPORTED_MODELS = sorted(all_models, key=lambda x: x['name'])

# 工具函数：提取基础模型名称
def get_base_model_name(model_name):
    """
    从变体模型名称中提取基础模型名称

    移除模型名称中的所有变体后缀（-search、-nothinking、-maxthinking 等），
    返回原始的基础模型名称，用于实际的 API 调用。

    参数：
        model_name (str): 可能包含变体后缀的模型名称

    返回：
        str: 基础模型名称

    示例：
        "gemini-2.5-pro-search-maxthinking" -> "gemini-2.5-pro"
        "gemini-2.5-flash-nothinking" -> "gemini-2.5-flash"
    """
    # 按顺序移除所有可能的变体后缀（顺序很重要，需先移除较长的后缀）
    suffixes = ["-maxthinking", "-nothinking", "-search"]
    for suffix in suffixes:
        if model_name.endswith(suffix):
            # 递归移除，处理多重后缀的情况（如 -search-maxthinking）
            return get_base_model_name(model_name[:-len(suffix)])
    return model_name  # 无后缀，返回原始名称

# 工具函数：判断是否为搜索增强模型
def is_search_model(model_name):
    """检查模型名称是否包含搜索变体标识"""
    return "-search" in model_name

# 工具函数：判断是否为无思考模式
def is_nothinking_model(model_name):
    """检查模型名称是否包含无思考变体标识"""
    return "-nothinking" in model_name

# 工具函数：判断是否为最大思考模式
def is_maxthinking_model(model_name):
    """检查模型名称是否包含最大思考变体标识"""
    return "-maxthinking" in model_name

# 工具函数：获取思考预算配置
def get_thinking_budget(model_name):
    """
    根据模型名称和变体类型返回对应的思考预算值

    思考预算控制模型在生成响应前的推理步骤数量。
    不同模型系列和变体有不同的预算配置：
    - flash 模型：更低的预算，适合快速响应
    - pro 模型：更高的预算，适合复杂推理

    参数：
        model_name (str): 模型名称（可能包含变体后缀）

    返回：
        int: 思考预算值
            -1: 使用模型默认值（常规模型）
            0: 完全禁用思考（flash-nothinking）
            128: 最小思考预算（pro-nothinking）
            24576: flash 最大思考预算（flash-maxthinking）
            32768: pro 最大思考预算（pro-maxthinking）
    """
    base_model = get_base_model_name(model_name)

    if is_nothinking_model(model_name):
        # nothinking 变体：最小化思考
        if "gemini-2.5-flash" in base_model:
            return 0  # flash 模型完全禁用思考
        elif "gemini-2.5-pro" in base_model or "gemini-3-pro" in base_model:
            return 128  # pro 模型保留最小思考预算（完全禁用可能影响质量）
    elif is_maxthinking_model(model_name):
        # maxthinking 变体：最大化思考
        if "gemini-2.5-flash" in base_model:
            return 24576  # flash 最大思考预算
        elif "gemini-2.5-pro" in base_model or "gemini-3-pro" in base_model:
            return 32768  # pro 最大思考预算
    else:
        # 常规模型使用 API 默认思考预算
        return -1  # -1 表示使用模型默认值

# 工具函数：判断是否应返回思考内容
def should_include_thoughts(model_name):
    """
    检查响应中是否应包含思考过程

    决定 API 响应是否包含模型的中间推理步骤（thinking tokens）。
    即使在 nothinking 模式下，pro 模型也会返回思考内容（因其保留了最小思考预算）。

    参数：
        model_name (str): 模型名称（可能包含变体后缀）

    返回：
        bool: True 表示应返回思考内容，False 表示不返回
    """
    if is_nothinking_model(model_name):
        # nothinking 模式下，pro 模型仍返回思考内容（因预算>0）
        base_model = get_base_model_name(model_name)
        return "gemini-2.5-pro" in base_model or "gemini-3-pro" in base_model
    else:
        # 其他模式均返回思考内容
        return True