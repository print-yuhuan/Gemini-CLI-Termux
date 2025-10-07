# Gemini-CLI-Termux 自动化部署工具

> ⚠️ 本项目基于 [geminicli2api](https://github.com/gzzhongqi/geminicli2api) 进行二次开发，提供 Termux 环境下的自动化部署和管理功能。

## 📌 项目简介

为 Android Termux 用户提供一键部署 Gemini-CLI 反向代理服务的解决方案，通过交互式菜单实现服务的安装、配置和管理，无需复杂操作即可使用 OpenAI 兼容接口调用 Google Gemini。

## 🎯 核心功能亮点

### 🎨 现代化 WEB UI 控制面板
- **实时统计仪表板**: 总请求数、成功请求、失败请求的可视化展示
- **饼图分析**: 请求分布饼图，直观显示成功/失败比例
- **调用历史**: 完整的 API 调用历史记录，包含状态码追踪
- **系统监控**: 实时系统资源使用情况监控
- **配置管理**: 在线编辑服务配置，即时生效

### 🔐 完善的认证与追踪
- **多认证方式**: 支持 Basic Auth、Bearer Token、API Key 等多种认证
- **状态码追踪**: 完整记录 401、404、500 等 HTTP 状态码
- **实时监控**: 自动刷新统计数据，5秒间隔实时更新
- **错误追踪**: 详细的错误信息和状态码记录

### 🌐 双 API 接口支持
- **OpenAI 兼容接口**: `/v1/chat/completions`, `/v1/models`
- **原生 Gemini 接口**: `/v1beta/models/*`, `/v1/models/*`
- **流式响应**: 完整支持 streaming 响应模式
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

### 局域网访问支持

通过菜单 `3 → 5` 可以：
- 开启/关闭局域网监听
- 获取本机内网 IP
- 实现多设备访问

### WEB UI 控制面板增强版

服务启动后自动打开浏览器访问 `http://127.0.0.1:8888/admin`，提供：

#### 📊 实时统计面板
- **总请求数**: 累计 API 调用次数
- **成功请求**: 成功处理的请求数量
- **失败请求**: 失败的请求数量及占比
- **请求分布饼图**: 可视化展示成功/失败比例
- **最后请求时间**: 最近一次 API 调用时间

#### 📝 调用历史记录
- **时间戳**: 精确到毫秒的调用时间
- **端点**: 访问的 API 端点路径
- **状态码**: HTTP 状态码 (200, 401, 404, 500 等)
- **状态**: 成功/失败状态标识
- **错误信息**: 详细的错误描述
- **筛选功能**: 按成功/失败状态筛选历史记录

#### ⚙️ 配置管理
- **监听地址**: 修改服务监听地址
- **监听端口**: 修改服务端口号
- **API 密钥**: 修改访问认证密码
- **项目ID**: 修改 Google Cloud 项目 ID
- **实时生效**: 配置修改后立即生效

#### 📈 系统监控
- **系统信息**: 操作系统、Python 版本、主机名
- **资源使用**: CPU 核心数、内存可用量、磁盘空间
- **服务状态**: 运行时间、凭证文件状态
- **实时刷新**: 自动更新系统监控信息

#### 🔄 快速操作
- **查看 API 文档**: 打开完整的 API 接口文档
- **刷新统计**: 刷新页面并更新统计数据
- **重置统计**: 清空所有统计信息和历史记录
- **一键刷新**: 按钮支持页面刷新功能

## 📖 API 文档

### 基础信息
- **服务地址**: `http://127.0.0.1:8888`
- **健康检查**: `GET /health` (无需认证)
- **WEB UI**: `GET /admin` (管理界面)
- **API 文档**: `GET /api/docs` (接口文档)

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
- `GET /v1/models` - 获取可用模型列表
- `POST /v1/chat/completions` - 聊天补全接口
- 支持流式 (`stream=true`) 和非流式响应

#### 原生 Gemini 接口
- `GET /v1beta/models` - 获取 Gemini 模型列表
- `POST /v1beta/models/{model}/generateContent` - 生成内容
- `POST /v1beta/models/{model}/streamGenerateContent` - 流式生成内容
- `GET /v1/models` - v1 版本模型列表

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
| API 地址 | `http://127.0.0.1:8888` | OpenAI 兼容接口地址 |
| WEB UI 地址 | `http://127.0.0.1:8888/admin` | 管理控制面板地址 |
| API 密钥 | `123` | 访问认证密码 |
| 监听地址 | `127.0.0.1` | 仅本机访问 |
| 监听端口 | `8888` | 服务端口 |
| 项目ID | 用户配置 | Google Cloud 项目 ID |

⚠️ **重要提示：** 除项目 ID 外，其他配置建议保持默认值！

## 🐛 故障排查

### 常见错误代码

| 错误代码 | 问题描述 | 解决方案 |
|---------|---------|---------|
| **401** | 认证失败 | 检查 API 密钥是否正确（默认：`123`） |
| **403** | 权限拒绝 | 1. 检查项目 ID 是否正确<br>2. 确认登录账号与项目匹配<br>3. 验证两个 API 均已启用 |
| **404** | 资源未找到 | 检查模型名称拼写或端点路径 |
| **500** | 服务器错误 | 查看服务日志，检查依赖安装 |
| **连接错误** | 无法访问服务 | 不要修改监听地址和端口，如已修改请恢复默认 |
| **WEB UI 无法访问** | 控制面板打不开 | 确保服务正常运行，检查浏览器是否支持现代 JavaScript |

### 排查建议

1. **首先查看视频教程** - 大部分问题都有演示
2. **使用菜单功能** - 不要手动修改配置文件
3. **保持默认配置** - 仅修改必要的项目 ID
4. **检查 API 启用** - 两个 API 都必须启用
5. **查看服务日志** - 运行 `python run.py` 查看详细错误信息

## 🔄 更新与维护

通过菜单 `5 → 1` 可以更新到最新版本，保留现有配置。

## 📝 项目结构

```
Gemini-CLI-Termux/
├── Setup.sh              # 自动化部署脚本
├── run.py               # 主程序入口
├── .env                 # 配置文件
├── oauth_creds.json     # Google 授权凭证
├── requirements.txt     # Python 依赖
├── CLAUDE.md           # Claude 代码助手配置
└── src/                 # 源代码目录
    ├── main.py          # FastAPI 应用主文件
    ├── auth.py          # 认证和 OAuth 流程
    ├── config.py        # 配置常量
    ├── gemini_routes.py # 原生 Gemini 接口
    ├── openai_routes.py # OpenAI 兼容接口
    ├── google_api_client.py # Google API 通信
    ├── web_ui.py        # WEB UI 控制面板
    ├── utils.py         # 工具函数
    ├── models.py        # 数据模型
    ├── openai_transformers.py # 格式转换
    ├── templates/       # HTML 模板
    │   ├── dashboard.html # 主控制面板
    │   └── api_docs.html # API 文档页面
    └── static/          # 静态资源
        ├── favicon.ico  # 网站图标
        └── css/style.css # 样式文件
```

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **前端界面**: Bootstrap 5 + Chart.js
- **模板引擎**: Jinja2
- **认证方式**: HTTP Basic Auth, Bearer Token, API Key
- **API 兼容**: OpenAI API 规范
- **监控统计**: 实时请求追踪和状态码记录

## 📄 许可证

本项目遵循 MIT 协议，详见 [LICENSE](./LICENSE)

## 🙏 致谢

- 核心功能：[geminicli2api](https://github.com/gzzhongqi/geminicli2api)
- 自动化脚本：[Gemini-CLI-Termux](https://github.com/print-yuhuan/Gemini-CLI-Termux)
- WEB UI 设计：Claude Code && DeepSeek

## 📮 问题反馈

1. 先查看[视频教程](https://b23.tv/JKAqkEv)
2. 阅读常见问题解答
3. 提交 [Issue](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues)

---

*最后更新：2025年9月10日*