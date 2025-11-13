"""
工具函数模块 - 提供项目通用工具函数

包含 User-Agent 生成、平台识别、客户端元数据构建等辅助功能。
"""
import platform
from .config import CLI_VERSION


def get_user_agent():
    """
    生成符合 gemini-cli 格式的 User-Agent 字符串

    构建标准的 HTTP User-Agent 请求头，用于标识客户端应用版本和运行环境。
    格式：GeminiCLI/{version} ({system}; {architecture})

    返回：
        str: User-Agent 字符串，例如 "GeminiCLI/0.13.0 (Linux; x86_64)"
    """
    version = CLI_VERSION
    system = platform.system()  # 操作系统名称：Linux、Windows、Darwin 等
    arch = platform.machine()   # 架构类型：x86_64、arm64、aarch64 等
    return f"GeminiCLI/{version} ({system}; {arch})"


def get_platform_string():
    """
    生成符合 gemini-cli 格式的平台标识字符串

    将系统和架构信息规范化为 Google API 识别的平台标识符。
    用于客户端元数据上报，帮助 Google 识别客户端运行环境。

    返回：
        str: 规范化的平台标识符，如 "LINUX_AMD64"、"DARWIN_ARM64" 等

    支持的平台：
        - macOS (DARWIN): DARWIN_ARM64 (Apple Silicon)、DARWIN_AMD64 (Intel)
        - Linux: LINUX_ARM64 (ARM 架构)、LINUX_AMD64 (x86_64)
        - Windows: WINDOWS_AMD64
        - 其他平台: PLATFORM_UNSPECIFIED
    """
    system = platform.system().upper()  # 系统名称转大写
    arch = platform.machine().upper()   # 架构名称转大写

    # 将系统和架构信息映射为 gemini-cli 平台格式
    if system == "DARWIN":  # macOS 系统
        if arch in ["ARM64", "AARCH64"]:
            return "DARWIN_ARM64"  # Apple Silicon (M1/M2/M3)
        else:
            return "DARWIN_AMD64"  # Intel Mac
    elif system == "LINUX":  # Linux 系统
        if arch in ["ARM64", "AARCH64"]:
            return "LINUX_ARM64"  # ARM 架构 Linux（如 Raspberry Pi、Android Termux）
        else:
            return "LINUX_AMD64"  # x86_64 架构 Linux
    elif system == "WINDOWS":  # Windows 系统
        return "WINDOWS_AMD64"
    else:
        return "PLATFORM_UNSPECIFIED"  # 未识别的平台


def get_client_metadata(project_id=None):
    """
    构建客户端元数据字典

    生成符合 Google API 要求的客户端元数据信息，
    用于 API 请求中标识客户端类型、平台和项目信息。

    参数：
        project_id (str, optional): Google Cloud 项目 ID。默认为 None。

    返回：
        dict: 客户端元数据字典，包含以下字段：
            - ideType: IDE 类型标识（此处固定为 IDE_UNSPECIFIED）
            - platform: 平台标识符（通过 get_platform_string 获取）
            - pluginType: 插件类型（固定为 GEMINI）
            - duetProject: 关联的项目 ID（可选）
    """
    return {
        "ideType": "IDE_UNSPECIFIED",      # IDE 类型：未指定（非 IDE 环境）
        "platform": get_platform_string(), # 平台标识符
        "pluginType": "GEMINI",            # 插件类型：Gemini CLI
        "duetProject": project_id,         # 关联的 Google Cloud 项目 ID
    }