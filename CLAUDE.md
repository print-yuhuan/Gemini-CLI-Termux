# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gemini-CLI-Termux is a FastAPI-based proxy server that provides OpenAI-compatible API endpoints for Google's Gemini models. It's designed specifically for Termux environments and includes a comprehensive web UI for monitoring and management.

## Development Commands

### Starting the Server
```bash
python run.py
```
The server will start on `127.0.0.1:8888` by default and automatically open the web UI at `/admin`.

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
- Copy `.env` file and configure required variables:
  - `GEMINI_AUTH_PASSWORD`: API authentication password (default: `123`)
  - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
  - `HOST`: Server host (default: `127.0.0.1`)
  - `PORT`: Server port (default: `8888`)

## Architecture Overview

### Core Components

**Entry Point**: `run.py` - Uses uvicorn to serve the FastAPI application

**Main Application**: `src/main.py` - FastAPI app with:
- CORS middleware for cross-origin requests
- Automatic browser opening on startup
- OAuth credential management
- Static file serving for web UI

**Authentication**: `src/auth.py` - Handles Google OAuth2 flow and credential management

**API Routes**:
- `src/openai_routes.py` - OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/models`)
- `src/gemini_routes.py` - Native Gemini API endpoints (`/v1beta/models/*`)
- `src/web_ui.py` - Web UI dashboard and management endpoints

**Core Services**:
- `src/google_api_client.py` - Google API communication
- `src/openai_transformers.py` - Format conversion between OpenAI and Gemini APIs
- `src/config.py` - Configuration constants and settings

**Web Interface**:
- `src/templates/dashboard.html` - Main web UI with real-time statistics
- `src/templates/api_docs.html` - API documentation page
- `src/static/` - Static assets (CSS, favicon)

### Key Features

1. **Multi-format Authentication**: Supports Basic Auth, Bearer tokens, API keys, and Google API key headers
2. **Real-time Monitoring**: Web dashboard with request tracking and system metrics
3. **Dual API Support**: Both OpenAI-compatible and native Gemini endpoints
4. **Termux Integration**: Automatic setup via `Setup.sh` script with menu-driven configuration

### Request Flow

1. Client sends request to OpenAI-compatible endpoint
2. Authentication middleware validates credentials
3. Request transformed from OpenAI format to Gemini format
4. Forwarded to Google's Gemini API using authenticated credentials
5. Response transformed back to OpenAI format
6. Statistics and logs updated in real-time

### Configuration Management

- Environment variables loaded from `.env` file
- Google credentials stored in `oauth_creds.json`
- Interactive configuration via web UI at `/admin`
- Termux-specific setup and management via `Setup.sh`

## Testing

This project does not currently include automated tests. Manual testing can be performed using:
- Health check endpoint: `GET /health`
- Test endpoint: `GET /test`
- Web UI functionality verification

## Important Notes

- Designed specifically for Termux Android environment
- Requires Google Cloud project with Gemini APIs enabled
- Default authentication password is `123` (change in production)
- Server automatically opens browser to web UI on startup
- Supports both streaming and non-streaming responses