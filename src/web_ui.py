"""
WEB UI Module for Gemini-CLI-Termux
Provides a modern web interface for monitoring and managing the API service.
"""
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .config import GEMINI_AUTH_PASSWORD, CREDENTIAL_FILE

# Statistics file path
STATS_FILE = Path(__file__).parent.parent / "api_stats.json"
MAX_HISTORY_ENTRIES = 1000

def load_persistent_stats():
    """Load statistics from persistent storage."""
    default_stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "last_request_time": None,
        "start_time": time.time(),
        "history": []
    }

    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Update start_time to current session
                data["start_time"] = time.time()
                return data
        else:
            logging.info("No existing stats file found, starting with fresh statistics")
            return default_stats
    except Exception as e:
        logging.error(f"Error loading stats file: {e}, starting with fresh statistics")
        return default_stats

def save_persistent_stats():
    """Save current statistics to persistent storage."""
    try:
        data = {
            "total_requests": api_stats["total_requests"],
            "successful_requests": api_stats["successful_requests"],
            "failed_requests": api_stats["failed_requests"],
            "last_request_time": api_stats["last_request_time"],
            "start_time": api_stats["start_time"],
            "history": api_history
        }

        # Ensure parent directory exists
        STATS_FILE.parent.mkdir(exist_ok=True)

        # Write to temporary file first, then rename for atomic operation
        temp_file = STATS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_file.replace(STATS_FILE)
        logging.debug("Statistics saved successfully")

    except Exception as e:
        logging.error(f"Error saving stats file: {e}")

# Load persistent data on module import
stats_data = load_persistent_stats()
api_stats = {
    "total_requests": stats_data["total_requests"],
    "successful_requests": stats_data["successful_requests"],
    "failed_requests": stats_data["failed_requests"],
    "last_request_time": stats_data["last_request_time"],
    "start_time": stats_data["start_time"]
}

# API call history
api_history: List[Dict] = stats_data.get("history", [])

router = APIRouter()

# Setup templates
try:
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    
    # Create directories if they don't exist
    templates_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Add custom Jinja2 filters
    def format_uptime_filter(seconds):
        """Format uptime seconds to human readable format."""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}天 {hours}小时"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def format_timestamp_filter(timestamp):
        """Format timestamp to readable date."""
        if not timestamp:
            return "暂无"
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    templates.env.filters["format_uptime"] = format_uptime_filter
    templates.env.filters["format_timestamp"] = format_timestamp_filter
    
    logging.info("WEB UI templates directory initialized")
except Exception as e:
    logging.error(f"Failed to initialize WEB UI directories: {e}")
    templates = None

def track_api_call(success: bool = True, endpoint: str = "", error_message: str = "", status_code: int = None):
    """Track API call statistics and history."""
    global api_stats, api_history

    current_time = time.time()

    # Update statistics
    api_stats["total_requests"] += 1
    if success:
        api_stats["successful_requests"] += 1
    else:
        api_stats["failed_requests"] += 1

    api_stats["last_request_time"] = current_time

    # Add to history
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "success": success,
        "error_message": error_message if not success else "",
        "status_code": status_code
    }

    api_history.append(history_entry)

    # Keep history within limit
    if len(api_history) > MAX_HISTORY_ENTRIES:
        api_history = api_history[-MAX_HISTORY_ENTRIES:]

    # Save to persistent storage
    save_persistent_stats()

def get_config_values() -> Dict:
    """Read current configuration values from .env file."""
    config = {}
    env_file = Path(__file__).parent.parent / ".env"
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            logging.error(f"Error reading .env file: {e}")
    
    return config

def update_config_value(key: str, value: str) -> bool:
    """Update a configuration value in .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        return False
    
    try:
        lines = []
        key_found = False
        
        # Read existing file
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    current_key = line.split('=', 1)[0].strip()
                    if current_key == key:
                        lines.append(f"{key}={value}\n")
                        key_found = True
                    else:
                        lines.append(line)
                else:
                    lines.append(line)
        
        # If key not found, add it
        if not key_found:
            lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        logging.error(f"Error updating .env file: {e}")
        return False

@router.get("/api/docs", response_class=HTMLResponse)
async def api_documentation(request: Request):
    """Serve the API documentation page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="WEB UI templates not available")
    
    return templates.TemplateResponse(
        "api_docs.html",
        {
            "request": request,
            "username": "admin"
        }
    )

@router.get("/admin", response_class=HTMLResponse)
async def web_ui_dashboard(request: Request):
    """Serve the main WEB UI dashboard."""
    if templates is None:
        raise HTTPException(status_code=500, detail="WEB UI templates not available")
    
    config = get_config_values()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": api_stats,
            "config": config,
            "uptime": int(time.time() - api_stats["start_time"]),
            "history_count": len(api_history),
            "username": "admin"
        }
    )

@router.get("/admin/api/stats")
async def get_api_stats():
    """Get current API statistics."""
    return {
        "stats": api_stats,
        "uptime_seconds": int(time.time() - api_stats["start_time"]),
        "history_count": len(api_history)
    }

@router.get("/admin/api/history")
async def get_api_history(
    limit: int = 100,
    filter_success: Optional[bool] = None
):
    """Get API call history with optional filtering."""
    filtered_history = api_history
    
    if filter_success is not None:
        filtered_history = [entry for entry in api_history if entry["success"] == filter_success]
    
    return {
        "history": filtered_history[-limit:],
        "total_count": len(api_history),
        "filtered_count": len(filtered_history)
    }

@router.get("/admin/config")
async def get_configuration():
    """Get current configuration values."""
    return {"config": get_config_values()}

@router.post("/admin/config")
async def update_configuration(
    request: Request
):
    """Update configuration values."""
    try:
        data = await request.json()
        
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Invalid configuration data")
        
        results = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                success = update_config_value(key, str(value))
                results[key] = "updated" if success else "failed"
            else:
                results[key] = "invalid_type"
        
        return {
            "message": "Configuration updated",
            "results": results,
            "current_config": get_config_values()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update configuration: {e}")

@router.get("/admin/system/info")
async def get_system_info():
    """Get system information."""
    import platform
    
    try:
        # Try to import psutil, but handle gracefully if not available
        try:
            import psutil
            psutil_available = True
        except ImportError:
            psutil_available = False
        
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "psutil_available": psutil_available
        }
        
        # Add psutil-based info if available
        if psutil_available:
            system_info.update({
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/')._asdict()
            })
        
        return {
            "system": system_info,
            "service": {
                "start_time": api_stats["start_time"],
                "uptime": int(time.time() - api_stats["start_time"]),
                "credential_file_exists": Path(CREDENTIAL_FILE).exists()
            }
        }
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {"error": "Unable to retrieve system information"}

@router.post("/admin/api/clear")
async def clear_statistics():
    """Clear all statistics and history."""
    global api_stats, api_history

    # Reset statistics to zero
    api_stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "last_request_time": None,
        "start_time": time.time()
    }

    # Clear history
    api_history.clear()

    # Save cleared state to persistent storage
    save_persistent_stats()

    logging.info("Statistics and history cleared")
    return {
        "message": "Statistics and history cleared successfully",
        "stats": api_stats,
        "history_count": len(api_history)
    }