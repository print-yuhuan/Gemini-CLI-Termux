# Gemini-CLI-Termux 自动化部署工具

> ⚠️ 本项目基于 [geminicli2api](https://github.com/gzzhongqi/geminicli2api) 进行二次开发，提供 Termux 环境下的自动化部署和管理功能。

## 📌 项目简介

为 Android Termux 用户提供一键部署 Gemini API 反向代理服务的解决方案，通过交互式菜单实现服务的安装、配置和管理，无需复杂操作即可使用 OpenAI 兼容接口调用 Google Gemini 2.5 系列模型。

## 🎯 核心功能亮点

### 🤖 Gemini 2.5 系列模型支持
- **Gemini 2.5 Pro**: 高级多模态模型，支持超长上下文（1M tokens）
- **Gemini 2.5 Flash**: 快速高效的多模态模型
- **多版本支持**: 包括 Preview 版本（05-06、06-05、05-20、04-17）
- **模型变体**: 支持 search（搜索增强）、nothinking/maxthinking（思考模式）等变体
- **灵活配置**: 可调节温度、top_p、top_k 等生成参数

### 🔐 多种认证方式
- **HTTP Basic Auth**: 用户名密码认证
- **Bearer Token**: 标准 OAuth 2.0 令牌认证
- **API Key 查询参数**: URL 参数传递密钥
- **Google API Key 头**: x-goog-api-key 头部认证
- **默认密钥**: 123（可通过 .env 文件修改）

### 🌐 双 API 接口支持
- **OpenAI 兼容接口**: `/v1/chat/completions`, `/v1/models`
- **原生 Gemini 接口**: `/v1beta/models/*`, `/v1/models/*`
- **流式响应**: 完整支持 streaming 响应模式（SSE）
- **批量处理**: 支持非流式批量请求处理

## 📺 视频教程

**遇到问题请先查看视频教程：** [B站演示视频](https://b23.tv/JKAqkEv)

## ⚡ 快速开始

在 Termux 中执行：

```bash
curl -O https://raw.githubusercontent.com/print-yuhuan/Gemini-CLI-Termux/main/Setup.sh && bash Setup.sh
```

脚本会自动完成：
- ✅ 环境检测与依赖安装
- ✅ 项目克隆与配置
- ✅ 交互式菜单配置
- ✅ 开机自启动设置

## 📋 前置要求

### 1. Termux 应用
- 版本要求：v0.118.3 或 v0.119.0-beta.3
- 下载地址：[GitHub](https://github.com/termux/termux-app/releases) 或 [F-Droid](https://f-droid.org/packages/com.termux)

### 2. Google Cloud 配置

#### 步骤一：获取项目 ID
1. 访问 [Google Cloud Console](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fwelcome%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)
2. 创建新项目或选择现有项目
3. 记录项目 ID

#### 步骤二：启用 API
启用以下两个 API（缺一不可）：
- [Gemini for Google Cloud](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Flibrary%2Fcloudaicompanion.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)
- [Gemini Cloud Assist](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Fapi%2Fgeminicloudassist.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)

## 🚀 功能特性

### 交互式管理菜单

```
==== Gemini-CLI-Termux 菜单 ====
0. 退出脚本
1. 启动服务         - 运行 OpenAI 兼容 API 服务
2. 重新授权         - 清理缓存并重新授权登录谷歌云
3. 修改配置         - 修改密码/项目ID/端口/局域网等
4. 谷歌云项         - 快速访问谷歌云控制台服务
5. 系统管理         - 更新/重装/卸载服务
```

### 🔧 交互式配置管理

通过菜单 `3` 可以修改：
- **监听地址**: 修改服务监听地址（默认 127.0.0.1）
- **监听端口**: 修改服务端口号（默认 8888）
- **项目ID**: 修改 Google Cloud 项目 ID
- **连接秘钥**: 修改 API 接口访问密码
- **局域网配置**: 开启/关闭局域网监听，获取内网 IP

### 🌐 局域网访问支持

通过菜单 `3 → 5` 可以：
- **开启网络监听**: 允许局域网内其他设备访问（HOST=0.0.0.0）
- **关闭网络监听**: 仅限本机访问（HOST=127.0.0.1）
- **获取内网地址**: 自动检测并显示局域网 IPv4 地址
- **连接帮助**: 查看详细的局域网连接指南

## 📖 API 文档

### 基础信息
- **服务地址**: `http://127.0.0.1:8888`
- **根端点**: `GET /` (项目信息，无需认证)
- **健康检查**: `GET /health` (健康状态，无需认证)

### 认证方式
支持多种认证方式（默认密码：`123`）：

#### 1. HTTP Basic 认证
```bash
curl -u admin:123 http://127.0.0.1:8888/v1/models
```

#### 2. Bearer Token 认证
```bash
curl -H "Authorization: Bearer 123" http://127.0.0.1:8888/v1/models
```

#### 3. API Key 查询参数
```bash
curl http://127.0.0.1:8888/v1/models?key=123
```

#### 4. Google API Key 头
```bash
curl -H "x-goog-api-key: 123" http://127.0.0.1:8888/v1/models
```

### 主要端点

#### OpenAI 兼容接口
```
GET  /v1/models                  - 获取可用模型列表
POST /v1/chat/completions        - 聊天补全接口（支持流式和非流式）
```

**支持的模型**:
- `gemini-2.5-pro`, `gemini-2.5-pro-preview-05-06`, `gemini-2.5-pro-preview-06-05`
- `gemini-2.5-flash`, `gemini-2.5-flash-preview-05-20`, `gemini-2.5-flash-preview-04-17`
- `gemini-2.5-flash-image-preview`
- 所有基础模型的 `-search`（搜索增强）变体
- 所有基础模型的 `-nothinking`/`-maxthinking`（思考模式）变体

#### 原生 Gemini 接口
```
GET  /v1beta/models                                        - 获取模型列表
POST /v1beta/models/{model}/generateContent                - 生成内容
POST /v1beta/models/{model}/streamGenerateContent          - 流式生成
GET  /v1/models                                            - v1 版本模型列表
POST /v1/models/{model}/generateContent                    - v1 生成内容
POST /v1/models/{model}/streamGenerateContent              - v1 流式生成
```

### 状态码说明

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| **200** | 请求成功 | - |
| **401** | 认证失败 | 检查 API 密钥是否正确 |
| **404** | 资源未找到 | 检查模型名称或端点路径 |
| **500** | 服务器错误 | 检查服务日志或重新启动 |

## 🔧 默认配置

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| API 地址 | `http://127.0.0.1:8888` | 服务访问地址 |
| API 密钥 | `123` | 访问认证密码（GEMINI_AUTH_PASSWORD） |
| 监听地址 | `127.0.0.1` | 仅本机访问（HOST） |
| 监听端口 | `8888` | 服务端口（PORT） |
| 项目ID | `your-project-id` | Google Cloud 项目 ID（GOOGLE_CLOUD_PROJECT） |
| 凭证文件 | `oauth_creds.json` | OAuth 认证凭证文件 |

⚠️ **重要提示**：
- 首次使用**必须**修改项目 ID 为你的 Google Cloud 项目 ID
- 其他配置建议保持默认值，除非有特殊需求
- 所有配置可通过交互式菜单修改，无需手动编辑 .env 文件

## 🐛 故障排查

### 常见错误代码

| 错误代码 | 问题描述 | 解决方案 |
|---------|---------|---------|
| **401** | 认证失败 | 检查 API 密钥是否正确（默认：`123`） |
| **403** | 权限拒绝 | 1. 检查项目 ID 是否正确<br>2. 确认登录账号与项目匹配<br>3. 验证两个 API 均已启用 |
| **404** | 资源未找到 | 检查模型名称拼写或端点路径 |
| **500** | 服务器错误 | 查看服务日志，检查依赖安装或重新授权 |
| **连接错误** | 无法访问服务 | 1. 确认服务已启动<br>2. 检查端口是否被占用<br>3. 如修改过配置请恢复默认 |
| **OAuth 错误** | 授权失败 | 使用菜单选项 2 重新授权，清理旧凭证 |

### 排查建议

1. **首先查看视频教程** - [B站演示视频](https://b23.tv/JKAqkEv) 包含完整的安装和配置流程
2. **使用交互式菜单** - 所有配置都应通过菜单修改，避免手动编辑文件
3. **必须配置项目 ID** - 这是服务运行的前提条件
4. **确认 API 已启用** - Gemini for Google Cloud 和 Gemini Cloud Assist 两个 API 都必须启用
5. **重新授权** - 遇到 OAuth 问题时使用菜单选项 2 重新授权
6. **查看详细日志** - 服务启动时会显示详细的错误信息和提示

## 🔄 更新与维护

### 更新服务
通过菜单 `5 → 1` 可以更新到最新版本：
- 自动备份 `.env` 和 `oauth_creds.json` 文件
- 拉取最新代码并重置到最新版本
- 恢复备份的配置文件
- 重新安装 Python 依赖

### 重新部署
通过菜单 `5 → 2` 可以完全重新部署（会清除所有配置）

### 卸载服务
通过菜单 `5 → 3` 可以完全卸载并删除项目目录

## 📝 项目结构

```
Gemini-CLI-Termux/
├── Setup.sh                    # 自动化部署和管理脚本
├── run.py                      # 主程序入口
├── .env                        # 环境变量配置文件
├── oauth_creds.json            # Google OAuth 授权凭证
├── requirements.txt            # Python 依赖列表
├── MapleMono.ttf              # Termux 终端字体
├── LICENSE                     # MIT 开源协议
├── .gitignore                  # Git 忽略文件配置
└── src/                        # 源代码目录
    ├── __init__.py             # Python 包初始化
    ├── main.py                 # FastAPI 应用主文件
    ├── auth.py                 # OAuth 认证和用户授权
    ├── config.py               # 配置常量和模型定义
    ├── gemini_routes.py        # 原生 Gemini API 路由
    ├── openai_routes.py        # OpenAI 兼容接口路由
    ├── google_api_client.py    # Google API 客户端封装
    ├── openai_transformers.py  # OpenAI/Gemini 格式转换
    ├── models.py               # Pydantic 数据模型
    └── utils.py                # 工具函数
```

## 🛠️ 技术栈

- **后端框架**: FastAPI（异步 Web 框架）
- **Web 服务器**: Uvicorn（ASGI 服务器）
- **认证方式**: OAuth 2.0（Google Cloud）、多种 API 认证方式
- **API 兼容**: OpenAI API 规范、原生 Gemini API
- **数据验证**: Pydantic（数据模型和验证）
- **HTTP 客户端**: Requests（API 通信）
- **环境管理**: python-dotenv（.env 文件加载）

### Python 依赖

```
fastapi<0.100           # Web 框架
uvicorn                 # ASGI 服务器
requests                # HTTP 客户端
python-dotenv           # 环境变量管理
google-auth-oauthlib    # Google OAuth 认证
pydantic<2.0           # 数据验证
```

## 📄 许可证

本项目遵循 MIT 协议，详见 [LICENSE](./LICENSE)

## 🙏 致谢

- 核心功能基于：[geminicli2api](https://github.com/gzzhongqi/geminicli2api)
- Termux 自动化脚本：[@print-yuhuan](https://github.com/print-yuhuan)
- Google Gemini API：[Google Cloud](https://cloud.google.com/)

## 📮 问题反馈

1. 先查看[视频教程](https://b23.tv/JKAqkEv)
2. 阅读常见问题解答
3. 提交 [Issue](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues)

## 📋 使用示例

### OpenAI SDK 调用示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8888/v1",
    api_key="123"  # 默认密码
)

# 非流式调用
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "user", "content": "你好，介绍一下你自己"}
    ]
)
print(response.choices[0].message.content)

# 流式调用
stream = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "user", "content": "讲一个故事"}
    ],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### curl 调用示例

```bash
# 获取模型列表
curl -H "Authorization: Bearer 123" http://127.0.0.1:8888/v1/models

# 非流式调用
curl -X POST http://127.0.0.1:8888/v1/chat/completions \
  -H "Authorization: Bearer 123" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "你好"}]
  }'

# 流式调用
curl -X POST http://127.0.0.1:8888/v1/chat/completions \
  -H "Authorization: Bearer 123" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "讲个笑话"}],
    "stream": true
  }'
```

---

*最后更新：2025年10月8日*