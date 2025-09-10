import logging
import os
import webbrowser
import threading
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .gemini_routes import router as gemini_router
from .openai_routes import router as openai_router
from .web_ui import router as web_ui_router
from .auth import get_credentials, get_user_project_id, onboard_user

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    logging.warning("python-dotenv not installed, .env file will not be loaded automatically")
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Global flag to track if browser has been opened
browser_opened = False

def open_browser_delayed():
    """Open browser with a delay to ensure server is ready."""
    global browser_opened
    
    # Wait a bit for the server to start
    time.sleep(3)
    
    if not browser_opened:
        try:
            host = os.getenv("HOST", "127.0.0.1")
            port = int(os.getenv("PORT", "8888"))
            
            # For browser redirection, always use localhost (127.0.0.1) instead of 0.0.0.0
            # because browsers cannot connect to 0.0.0.0 directly
            browser_host = "127.0.0.1" if host == "0.0.0.0" else host
            url = f"http://{browser_host}:{port}/admin"
            
            logging.info(f"Attempting to open browser: {url}")
            
            # Try multiple methods to open browser
            success = webbrowser.open(url)
            if success:
                logging.info(f"Browser opened successfully: {url}")
            else:
                logging.warning(f"webbrowser.open() returned False for: {url}")
                # Try alternative method for Termux
                try:
                    import subprocess
                    subprocess.run(["termux-open-url", url], check=False)
                    logging.info(f"Used termux-open-url for: {url}")
                except:
                    logging.warning("termux-open-url also failed")
            
            browser_opened = True
        except Exception as e:
            logging.error(f"Failed to open browser: {e}")

# Add CORS middleware for preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
    try:
        logging.info("Starting Gemini proxy server...")
        
        # Check if credentials exist
        import os
        from .config import CREDENTIAL_FILE
        
        env_creds_json = os.getenv("GEMINI_CREDENTIALS")
        creds_file_exists = os.path.exists(CREDENTIAL_FILE)
        
        if env_creds_json or creds_file_exists:
            try:
                # Try to load existing credentials without OAuth flow first
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
            # No credentials found - prompt user to authenticate
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
        
        # Start browser redirection in a separate thread
        browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
        browser_thread.start()
        
    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        logging.warning("Server may not function properly.")

@app.options("/{full_path:path}")
async def handle_preflight(request: Request, full_path: str):
    """Handle CORS preflight requests without authentication."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Root endpoint - no authentication required
@app.get("/")
async def root():
    """
    Gemini-CLI-Termux API Documentation
    
    OpenAI-compatible API proxy for Google's Gemini models with comprehensive documentation.
    No authentication required for this endpoint.
    """
    return {
        "name": "Gemini-CLI-Termux",
        "description": "OpenAI-compatible API proxy for Google's Gemini models",
        "version": "1.0.0",
        "authentication": {
            "type": "Basic Auth",
            "username": "admin",
            "password": "From GEMINI_AUTH_PASSWORD environment variable (default: 123)",
            "required_for": "All endpoints except /, /health, and /admin"
        },
        "endpoints": {
            "openai_compatible": {
                "description": "OpenAI-compatible endpoints for easy integration",
                "endpoints": {
                    "chat_completions": {
                        "path": "/v1/chat/completions",
                        "method": "POST",
                        "description": "Chat completion endpoint compatible with OpenAI API",
                        "request_format": {
                            "model": "string (e.g., 'gemini-2.5-pro')",
                            "messages": "array of message objects",
                            "temperature": "number (0.0-2.0)",
                            "max_tokens": "number",
                            "stream": "boolean"
                        }
                    },
                    "models": {
                        "path": "/v1/models",
                        "method": "GET",
                        "description": "List available models"
                    }
                }
            },
            "native_gemini": {
                "description": "Native Gemini API endpoints",
                "endpoints": {
                    "models": {
                        "path": "/v1beta/models",
                        "method": "GET",
                        "description": "List available Gemini models with details"
                    },
                    "generate": {
                        "path": "/v1beta/models/{model}/generateContent",
                        "method": "POST",
                        "description": "Generate content using specified Gemini model"
                    },
                    "stream": {
                        "path": "/v1beta/models/{model}/streamGenerateContent",
                        "method": "POST",
                        "description": "Stream generated content"
                    }
                }
            },
            "management": {
                "description": "Management and monitoring endpoints",
                "endpoints": {
                    "health": {
                        "path": "/health",
                        "method": "GET",
                        "description": "Health check endpoint",
                        "authentication": "None"
                    },
                    "admin": {
                        "path": "/admin",
                        "method": "GET",
                        "description": "Web-based administration dashboard",
                        "authentication": "None for UI, but API calls require auth"
                    }
                }
            }
        },
        "supported_models": [
            "gemini-2.5-pro", "gemini-2.5-pro-search", "gemini-2.5-pro-nothinking", "gemini-2.5-pro-maxthinking",
            "gemini-2.5-flash", "gemini-2.5-flash-search", "gemini-2.5-flash-nothinking", "gemini-2.5-flash-maxthinking"
        ],
        "example_requests": {
            "openai_chat_completion": {
                "curl": "curl -X POST http://localhost:{PORT}/v1/chat/completions -H 'Content-Type: application/json' -H 'Authorization: Basic YWRtaW46MTIz' -d '{\"model\": \"gemini-2.5-pro\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}'"
            },
            "list_models": {
                "curl": "curl -X GET http://localhost:{PORT}/v1/models -H 'Authorization: Basic YWRtaW46MTIz'"
            }
        },
        "configuration": {
            "host": "Set via HOST environment variable (default: 127.0.0.1)",
            "port": "Set via PORT environment variable (default: 8888)",
            "password": "Set via GEMINI_AUTH_PASSWORD environment variable (default: 123)",
            "google_project": "Set via GOOGLE_CLOUD_PROJECT environment variable"
        },
        "repository": "https://github.com/print-yuhuan/Gemini-CLI-Termux",
        "documentation": "Visit /admin for web-based management interface with real-time statistics"
    }

# Health check endpoint for Docker/Hugging Face
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "geminicli2api"}

# Simple test endpoint to verify WEB UI accessibility
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is running."""
    return {
        "message": "Server is running", 
        "web_ui_available": True,
        "admin_url": "http://127.0.0.1:8888/admin"
    }

# Favicon endpoint - no authentication required
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon.ico without authentication."""
    import os
    from fastapi.responses import FileResponse
    
    # Check if favicon exists in static directory
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    favicon_path = os.path.join(static_dir, "favicon.ico")
    
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return 404 if favicon doesn't exist
        return Response(status_code=404)

app.include_router(openai_router)
app.include_router(web_ui_router)  # Must come before gemini_router to avoid path conflicts
app.include_router(gemini_router)

# Mount static files for WEB UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Favicon is served by the explicit route above, no need for mount