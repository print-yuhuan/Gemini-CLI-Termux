import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .gemini_routes import router as gemini_router
from .openai_routes import router as openai_router
from .auth import get_credentials, get_user_project_id, onboard_user

# 加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    logging.warning("python-dotenv not installed, .env file will not be loaded automatically")
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

# 日志记录配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# 添加 CORS 中间件以处理跨域预检请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],        # 允许所有 HTTP 方法
    allow_headers=["*"],        # 允许所有请求头
)

@app.on_event("startup")
async def startup_event():
    try:
        logging.info("Starting Gemini proxy server...")

        # 检查凭据文件是否存在
        import os
        from .config import CREDENTIAL_FILE
        
        env_creds_json = os.getenv("GEMINI_CREDENTIALS")
        creds_file_exists = os.path.exists(CREDENTIAL_FILE)
        
        if env_creds_json or creds_file_exists:
            try:
                # 尝试加载现有凭据（不启动 OAuth 流程）
                creds = get_credentials(allow_oauth_flow=False)
                if creds:
                    try:
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
            # 未找到凭据，启动 OAuth 身份验证流程
            logging.info("No credentials found. Starting OAuth authentication flow...")
            try:
                creds = get_credentials(allow_oauth_flow=True)
                if creds:
                    try:
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
    """处理 CORS 预检请求（无需身份验证）"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# 根端点（无需身份验证）
@app.get("/")
async def root():
    """
    根端点 - 提供项目基本信息

    无需身份验证即可访问。
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
    """容器编排系统的健康检查端点"""
    return {"status": "healthy", "service": "Gemini-CLI-Termux"}

app.include_router(openai_router)
app.include_router(gemini_router)