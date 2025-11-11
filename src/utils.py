import platform
from .config import CLI_VERSION

def get_user_agent():
    """生成符合 gemini-cli 格式的 User-Agent 字符串"""
    version = CLI_VERSION
    system = platform.system()
    arch = platform.machine()
    return f"GeminiCLI/{version} ({system}; {arch})"

def get_platform_string():
    """生成符合 gemini-cli 格式的平台标识字符串"""
    system = platform.system().upper()
    arch = platform.machine().upper()

    # 将系统和架构信息映射为 gemini-cli 平台格式
    if system == "DARWIN":
        if arch in ["ARM64", "AARCH64"]:
            return "DARWIN_ARM64"
        else:
            return "DARWIN_AMD64"
    elif system == "LINUX":
        if arch in ["ARM64", "AARCH64"]:
            return "LINUX_ARM64"
        else:
            return "LINUX_AMD64"
    elif system == "WINDOWS":
        return "WINDOWS_AMD64"
    else:
        return "PLATFORM_UNSPECIFIED"

def get_client_metadata(project_id=None):
    return {
        "ideType": "IDE_UNSPECIFIED",
        "platform": get_platform_string(),
        "pluginType": "GEMINI",
        "duetProject": project_id,
    }