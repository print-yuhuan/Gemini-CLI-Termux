"""
Gemini-CLI-Termux 代理服务器主程序

本模块是 FastAPI 应用的入口点，负责：
1. 加载环境配置
2. 初始化日志系统
3. 配置 CORS 中间件
4. 注册路由处理器
5. 处理应用启动事件（OAuth 认证、用户引导等）
"""
import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .gemini_routes import router as gemini_router
from .openai_routes import router as openai_router
from .auth import get_credentials, get_user_project_id, onboard_user

# ==================== 环境配置加载 ====================
# 尝试从 .env 文件加载环境变量（若安装了 python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载项目根目录下的 .env 文件
    logging.info("Environment variables loaded from .env file")
except ImportError:
    # python-dotenv 未安装，跳过 .env 文件加载
    logging.warning("python-dotenv not installed, .env file will not be loaded automatically")
except Exception as e:
    # .env 文件加载失败（如文件不存在或格式错误）
    logging.warning(f"Could not load .env file: {e}")

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,  # 日志级别：INFO（生产环境推荐）
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 日志格式：时间 - 模块 - 级别 - 消息
)

# ==================== FastAPI 应用初始化 ====================
app = FastAPI()

# 添加 CORS 中间件以处理跨域预检请求
# 允许所有来源访问 API（适用于公共代理服务）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 允许所有来源（生产环境建议限制为特定域名）
    allow_credentials=True,     # 允许携带凭据（cookies、认证头等）
    allow_methods=["*"],        # 允许所有 HTTP 方法（GET、POST、PUT、DELETE 等）
    allow_headers=["*"],        # 允许所有请求头
)

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件处理器

    在 FastAPI 应用启动时执行，负责初始化认证和用户引导流程：
    1. 检查现有凭据（环境变量或文件）
    2. 若凭据存在，尝试加载并完成用户引导
    3. 若凭据不存在，启动 OAuth2 授权流程
    4. 记录启动状态和错误信息

    注意：
        - 即使认证失败，服务器仍会启动（延迟认证至首次请求）
        - 错误信息会记录到日志中，便于排查问题
    """
    try:
        logging.info("Starting Gemini proxy server...")

        # 检查凭据来源：环境变量或文件
        import os
        from .config import CREDENTIAL_FILE

        env_creds_json = os.getenv("GEMINI_CREDENTIALS")  # 环境变量凭据（JSON 字符串）
        creds_file_exists = os.path.exists(CREDENTIAL_FILE)  # 凭据文件是否存在

        if env_creds_json or creds_file_exists:
            # 路径1：发现现有凭据，尝试加载（不启动 OAuth 流程）
            try:
                creds = get_credentials(allow_oauth_flow=False)
                if creds:
                    try:
                        # 获取项目 ID 并完成用户引导
                        proj_id = get_user_project_id(creds)
                        if proj_id:
                            onboard_user(creds, proj_id)
                            logging.info(f"Successfully onboarded with project ID: {proj_id}")
                        logging.info("Gemini proxy server started successfully")
                        logging.info("Authentication required - Password: see .env file")
                    except Exception as e:
                        logging.error(f"Setup failed: {str(e)}")
                        logging.warning("Server started but may not function properly until setup issues are resolved.")
                else:
                    logging.warning("Credentials file exists but could not be loaded. Server started - authentication will be required on first request.")
            except Exception as e:
                logging.error(f"Credential loading error: {str(e)}")
                logging.warning("Server started but credentials need to be set up.")
        else:
            # 路径2：未找到凭据，启动 OAuth 身份验证流程
            logging.info("No credentials found. Starting OAuth authentication flow...")
            try:
                creds = get_credentials(allow_oauth_flow=True)
                if creds:
                    try:
                        # 完成用户引导流程
                        proj_id = get_user_project_id(creds)
                        if proj_id:
                            onboard_user(creds, proj_id)
                            logging.info(f"Successfully onboarded with project ID: {proj_id}")
                        logging.info("Gemini proxy server started successfully")
                    except Exception as e:
                        logging.error(f"Setup failed: {str(e)}")
                        logging.warning("Server started but may not function properly until setup issues are resolved.")
                else:
                    logging.error("Authentication failed. Server started but will not function until credentials are provided.")
            except Exception as e:
                logging.error(f"Authentication error: {str(e)}")
                logging.warning("Server started but authentication failed.")

        logging.info("Authentication required - Password: see .env file")

    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        logging.warning("Server may not function properly.")

@app.options("/{full_path:path}")
async def handle_preflight(request: Request, full_path: str):
    """
    处理 CORS 预检请求（无需身份验证）

    响应浏览器发送的 OPTIONS 预检请求，告知允许的请求方法和头部。
    这是 CORS 协议的一部分，确保跨域请求能够正常工作。

    参数：
        request: FastAPI 请求对象
        full_path: 请求的完整路径（通配符捕获）

    返回：
        Response: 包含 CORS 响应头的 200 响应
    """
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",  # 允许所有来源
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",  # 允许的 HTTP 方法
            "Access-Control-Allow-Headers": "*",  # 允许所有请求头
            "Access-Control-Allow-Credentials": "true",  # 允许携带凭据
        }
    )

# 根端点（无需身份验证）
@app.get("/")
async def root():
    """
    根端点 - 提供项目基本信息和 API 文档

    返回服务的基本信息、可用端点列表和使用说明。
    无需身份验证即可访问，便于用户了解服务功能。

    返回：
        dict: 包含服务名称、描述、版本、端点列表等信息的字典
    """
    return {
        "name": "Gemini-CLI-Termux",
        "description": "OpenAI-compatible API proxy for Google's Gemini models via gemini-cli",
        "purpose": "Provides both OpenAI-compatible endpoints (/v1/chat/completions) and native Gemini API endpoints for accessing Google's Gemini models",
        "version": "1.0.0",
        "endpoints": {
            "openai_compatible": {
                "chat_completions": "/v1/chat/completions",
                "models": "/v1/models"
            },
            "native_gemini": {
                "models": "/v1beta/models",
                "generate": "/v1beta/models/{model}/generateContent",
                "stream": "/v1beta/models/{model}/streamGenerateContent"
            },
            "health": "/health"
        },
        "authentication": "Required for all endpoints except root and health",
        "repository": "https://github.com/print-yuhuan/Gemini-CLI-Termux"
    }

# 健康检查端点（用于 Docker/Hugging Face 容器编排）
@app.get("/health")
async def health_check():
    """
    容器编排系统的健康检查端点

    用于 Docker、Kubernetes、Hugging Face Spaces 等容器编排系统
    检查服务是否正常运行。返回固定的健康状态响应。

    返回：
        dict: 包含状态和服务名称的字典
    """
    return {"status": "healthy", "service": "Gemini-CLI-Termux"}

# ==================== 路由注册 ====================
# 注册 OpenAI 兼容路由（/v1/chat/completions、/v1/models 等）
app.include_router(openai_router)

# 注册原生 Gemini 路由（/v1beta/models、/v1beta/models/{model}/generateContent 等）
app.include_router(gemini_router)