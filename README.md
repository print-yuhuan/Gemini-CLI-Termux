# Gemini-CLI-Termux 自动化部署工具

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/print-yuhuan/Gemini-CLI-Termux?style=flat-square)](https://github.com/print-yuhuan/Gemini-CLI-Termux/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/print-yuhuan/Gemini-CLI-Termux?style=flat-square)](https://github.com/print-yuhuan/Gemini-CLI-Termux/network)
[![GitHub issues](https://img.shields.io/github/issues/print-yuhuan/Gemini-CLI-Termux?style=flat-square)](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues)
[![License](https://img.shields.io/github/license/print-yuhuan/Gemini-CLI-Termux?style=flat-square)](./LICENSE)

**为 Android Termux 用户提供一键部署 Gemini API 反向代理服务**

[📺 视频教程](https://b23.tv/JKAqkEv) · [🐛 问题反馈](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues) · [💬 QQ交流群：807134015](https://qm.qq.com/q/FUme0cSMqV)

</div>

---

> 💡 **项目声明**
> 本项目基于 [geminicli2api](https://github.com/gzzhongqi/geminicli2api) 进行二次开发，提供 Termux 环境下的自动化部署和管理功能。

## 📌 项目简介

**Gemini-CLI-Termux** 是一个专为 Android Termux 环境设计的自动化部署工具，让你能够轻松在手机上运行 Gemini API 反向代理服务。通过交互式菜单界面，无需复杂的命令行操作，即可完成服务的安装、配置和管理，并使用 OpenAI 兼容接口调用 Google Gemini 2.5 系列模型。

### ✨ 为什么选择本项目？

- 🚀 **一键部署**：单条命令完成所有安装配置
- 🎯 **零门槛**：交互式菜单，无需命令行基础
- 🔧 **易于管理**：可视化配置修改，实时生效
- 🌐 **局域网支持**：多设备共享，手机变身API服务器
- 📱 **移动优先**：专为 Termux 环境深度优化
- 🔄 **持续更新**：菜单内一键更新到最新版本

## 🎯 核心功能亮点

### 🤖 Gemini 模型全系列支持
- **Gemini 3 Pro**: 🌟 最新一代高级多模态模型，支持超长上下文（1M tokens）
- **Gemini 2.5 Pro**: 高级多模态模型，支持超长上下文（1M tokens）
- **Gemini 2.5 Flash**: 快速高效的多模态模型
- **多版本支持**:
  - Gemini 3 Pro Preview (11-2025)
  - Gemini 2.5 Pro Preview (03-25、05-06、06-05)
  - Gemini 2.5 Flash Preview (04-17、05-20)
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

## 📖 目录

- [项目简介](#-项目简介)
- [核心功能亮点](#-核心功能亮点)
- [快速开始](#-快速开始)
- [前置要求](#-前置要求)
- [功能特性](#-功能特性)
- [API 文档](#-api-文档)
- [默认配置](#-默认配置)
- [故障排查](#-故障排查)
- [更新与维护](#-更新与维护)
- [使用示例](#-使用示例)
- [项目结构](#-项目结构)
- [技术栈](#️-技术栈)
- [许可证](#-许可证)
- [致谢](#-致谢)
- [问题反馈](#-问题反馈)

---

## ⚡ 快速开始

### 📺 视频教程

**强烈推荐先观看视频教程：** [B站完整演示](https://b23.tv/JKAqkEv)

### 🚀 一键安装

在 Termux 中执行：

```bash
curl -O https://raw.githubusercontent.com/print-yuhuan/Gemini-CLI-Termux/main/Setup.sh && bash Setup.sh
```

### 📋 安装流程

脚本将自动完成以下步骤：

| 步骤 | 内容 | 说明 |
|------|------|------|
| 1/8 | 🔍 **环境检测** | 验证 Termux 环境和必要权限 |
| 2/8 | 📦 **更新包管理器** | 配置镜像源并更新系统包 |
| 3/8 | 🛠️ **安装依赖** | 自动安装 Python、Git、Curl 等 |
| 4/8 | 🎨 **配置终端字体** | 下载并应用优化字体 |
| 5/8 | 📥 **克隆项目** | 从 GitHub 下载项目文件 |
| 6/8 | ✅ **验证文件** | 检查项目文件完整性 |
| 7/8 | 🚀 **配置自启动** | 设置开机自动启动菜单 |
| 8/8 | 🐍 **安装 Python 依赖** | 安装 FastAPI、Uvicorn 等 |

安装完成后将自动进入交互式主菜单。

## 📋 前置要求

### 1️⃣ Termux 应用

> ⚠️ **重要提示**：请从官方渠道下载，避免使用 Google Play 版本（已停止维护）

| 项目 | 要求 | 下载地址 |
|------|------|----------|
| **版本** | v0.118.3 或更高 | [GitHub Releases](https://github.com/termux/termux-app/releases) |
| **推荐版本** | v0.119.0-beta.3 | [F-Droid](https://f-droid.org/packages/com.termux) |
| **最低 Android 版本** | Android 7.0+ | - |

### 2️⃣ Google Cloud 配置

> 💡 **新手提示**：配置 Google Cloud 是使用本项目的必要步骤，但非常简单！脚本会自动打开浏览器帮助你完成配置。

#### 📝 配置步骤

> 🌐 **便捷功能**：使用菜单选项 `4. 谷歌云项` 可自动打开相应的 Google Cloud 页面（通过 `termux-open-url` 命令）

<details>
<summary><b>步骤一：获取项目 ID</b>（点击展开）</summary>

1. 访问 [Google Cloud Console](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fwelcome%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)
2. 使用 Google 账号登录
3. 点击顶部导航栏的项目选择器
4. 点击「**新建项目**」或选择现有项目
5. 记录项目 ID（通常显示在项目名称下方）

> 💡 提示：项目 ID 格式类似 `my-project-123456`

</details>

<details>
<summary><b>步骤二：启用 API</b>（点击展开）</summary>

启用以下两个 API（**缺一不可**）：

1. **Gemini for Google Cloud API**
   - 访问 [启用链接](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Flibrary%2Fcloudaicompanion.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)
   - 选择你的项目
   - 点击「**启用**」按钮

2. **Gemini Cloud Assist API**
   - 访问 [启用链接](https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Fapi%2Fgeminicloudassist.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser)
   - 选择你的项目
   - 点击「**启用**」按钮

> ⚠️ 注意：两个 API 都必须启用，否则服务无法正常运行

</details>

<details>
<summary><b>步骤三：配置项目 ID</b>（点击展开）</summary>

安装完成后，在主菜单中：
1. 选择 `3. 修改配置`
2. 选择 `3. 修改项目标识`
3. 输入你的 Google Cloud 项目 ID
4. 确认保存

</details>

#### ✅ 快速验证

使用菜单选项 `4. 谷歌云项` 可以快速访问：
- 获取项目 ID
- 管理 Gemini for Google Cloud API
- 管理 Gemini Cloud Assist API

## 🚀 功能特性

### 🎛️ 交互式管理菜单

```
==== Gemini-CLI-Termux 主菜单 ====
0. 退出脚本
1. 启动服务         - 运行 OpenAI 兼容 API 服务
2. 重新授权         - 清理缓存并重新登录 Google Cloud
3. 修改配置         - 修改密码/项目ID/端口/局域网等
4. 谷歌云项         - 快速访问 Google Cloud 控制台
5. 系统管理         - 更新/重新部署/卸载服务
6. 关于脚本         - 查看作者信息和联系方式
```

### 🔧 配置管理功能

通过 `主菜单 → 3. 修改配置` 进入配置菜单：

| 选项 | 功能 | 说明 |
|------|------|------|
| **1. 修改监听地址** | 设置服务监听地址 | `127.0.0.1` 仅本机，`0.0.0.0` 允许局域网 |
| **2. 修改监听端口** | 设置服务端口号 | 默认 `8888`，范围 `1-65535` |
| **3. 修改项目标识** | 设置 Google Cloud 项目 ID | **首次使用必填** |
| **4. 修改连接秘钥** | 设置 API 访问密码 | 默认 `123`，建议修改为强密码 |
| **5. 局域网配置项** | 局域网访问配置 | 详见下方说明 |

### 🌐 局域网访问功能

通过 `主菜单 → 3. 修改配置 → 5. 局域网配置项` 进入局域网配置：

<details>
<summary><b>功能列表</b>（点击展开）</summary>

| 选项 | 功能 | 说明 |
|------|------|------|
| **1. 开启网络监听** | 允许局域网设备访问 | 自动设置 `HOST=0.0.0.0` |
| **2. 关闭网络监听** | 仅限本机访问 | 自动设置 `HOST=127.0.0.1` |
| **3. 获取内网地址** | 显示局域网 IP 地址 | 自动检测 WiFi 接口地址 |
| **4. 内网连接帮助** | 查看详细使用指南 | 包含常见问题解答 |

</details>

<details>
<summary><b>局域网使用场景</b>（点击展开）</summary>

- 📱 **手机访问手机**：两台设备连接同一 WiFi
- 💻 **电脑访问手机**：电脑和手机在同一局域网
- 🔥 **多设备共享**：手机开热点，其他设备连接
- 🏠 **家庭网络**：所有设备使用同一路由器

</details>

### 🔐 系统管理功能

通过 `主菜单 → 5. 系统管理` 进入管理菜单：

| 选项 | 功能 | 说明 |
|------|------|------|
| **1. 更新服务** | 更新到最新版本 | 自动备份配置，拉取最新代码，恢复配置 |
| **2. 重新部署** | 完全重新安装 | ⚠️ 删除所有配置和数据，重新安装 |
| **3. 卸载服务** | 完全卸载项目 | ⚠️ 不可逆操作，删除所有项目文件 |

## 📖 API 文档

### 🔌 基础信息

| 项目 | 内容 | 说明 |
|------|------|------|
| **服务地址** | `http://127.0.0.1:8888` | 本机访问地址 |
| **局域网地址** | `http://<内网IP>:8888` | 开启网络监听后可用 |
| **根端点** | `GET /` | 返回项目信息，无需认证 |
| **健康检查** | `GET /health` | 返回服务状态，无需认证 |

### 🔑 认证方式

支持以下 4 种认证方式（默认密码：`123`）：

<details>
<summary><b>查看所有认证方式示例</b>（点击展开）</summary>

#### 1️⃣ HTTP Basic 认证

```bash
curl -u admin:123 http://127.0.0.1:8888/v1/models
```

#### 2️⃣ Bearer Token 认证（推荐）

```bash
curl -H "Authorization: Bearer 123" http://127.0.0.1:8888/v1/models
```

#### 3️⃣ API Key 查询参数

```bash
curl http://127.0.0.1:8888/v1/models?key=123
```

#### 4️⃣ Google API Key 头

```bash
curl -H "x-goog-api-key: 123" http://127.0.0.1:8888/v1/models
```

</details>

### 🎯 API 端点

#### OpenAI 兼容接口

| 端点 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/v1/models` | GET | 获取模型列表 | 返回所有可用的 Gemini 模型 |
| `/v1/chat/completions` | POST | 聊天补全 | 支持流式和非流式响应 |

**可用模型列表**：

<details>
<summary><b>查看完整模型列表</b>（点击展开）</summary>

**Gemini 3 Pro 系列** 🌟：
- `gemini-3-pro-preview-11-2025` - 最新一代高级多模态模型
- `gemini-3-pro-preview-11-2025-search` - 搜索增强版
- `gemini-3-pro-preview-11-2025-nothinking` - 无思考模式
- `gemini-3-pro-preview-11-2025-maxthinking` - 最大思考模式

**Gemini 2.5 Pro 系列**：
- `gemini-2.5-pro` - 高级多模态模型
- `gemini-2.5-pro-preview-03-25` - 预览版本
- `gemini-2.5-pro-preview-05-06` - 预览版本
- `gemini-2.5-pro-preview-06-05` - 预览版本
- `gemini-2.5-pro-search` - 搜索增强版
- `gemini-2.5-pro-nothinking` - 无思考模式
- `gemini-2.5-pro-maxthinking` - 最大思考模式

**Gemini 2.5 Flash 系列**：
- `gemini-2.5-flash` - 快速多模态模型
- `gemini-2.5-flash-preview-04-17` - 预览版本
- `gemini-2.5-flash-preview-05-20` - 预览版本
- `gemini-2.5-flash-image-preview` - 图像预览版
- `gemini-2.5-flash-search` - 搜索增强版
- `gemini-2.5-flash-nothinking` - 无思考模式
- `gemini-2.5-flash-maxthinking` - 最大思考模式

**思考模式说明**：
- **nothinking**: 思考预算最小化（2.5 Flash: 0 tokens, 2.5 Pro/3 Pro: 128 tokens）
- **maxthinking**: 思考预算最大化（2.5 Flash: 24576 tokens, 2.5 Pro/3 Pro: 32768 tokens）
- **默认模式**: 自动平衡的思考预算

</details>

#### 原生 Gemini 接口

| 端点 | 方法 | 功能 |
|------|------|------|
| `/v1beta/models` | GET | 获取 v1beta 模型列表 |
| `/v1beta/models/{model}/generateContent` | POST | v1beta 生成内容 |
| `/v1beta/models/{model}/streamGenerateContent` | POST | v1beta 流式生成 |
| `/v1/models` | GET | 获取 v1 模型列表 |
| `/v1/models/{model}/generateContent` | POST | v1 生成内容 |
| `/v1/models/{model}/streamGenerateContent` | POST | v1 流式生成 |

### 📊 HTTP 状态码

| 状态码 | 含义 | 可能原因 | 解决方案 |
|--------|------|----------|----------|
| **200** | 请求成功 | - | - |
| **401** | 认证失败 | API 密钥错误 | 检查密钥是否为 `123` 或已修改的值 |
| **403** | 权限拒绝 | 项目配置错误 | 检查项目 ID 和 API 启用状态 |
| **404** | 资源未找到 | 端点或模型不存在 | 检查 URL 拼写和模型名称 |
| **500** | 服务器错误 | 内部错误 | 查看日志，尝试重启服务 |
| **502/503** | 服务不可用 | 服务未启动 | 确认服务正在运行 |

## 🔧 默认配置

### 📝 配置文件说明

项目包含两个主要配置文件：

| 文件 | 路径 | 用途 | 修改方式 |
|------|------|------|----------|
| **环境配置** | `~/Gemini-CLI-Termux/.env` | 服务配置参数 | 通过菜单修改（推荐） |
| **OAuth 凭证** | `~/Gemini-CLI-Termux/oauth_creds.json` | Google 授权凭证 | 重新授权自动生成 |

### ⚙️ 默认配置参数

| 配置项 | 环境变量 | 默认值 | 说明 |
|-------|---------|--------|------|
| **API 密钥** | `GEMINI_AUTH_PASSWORD` | `123` | API 访问密码 ⚠️ 建议修改 |
| **监听地址** | `HOST` | `127.0.0.1` | 仅本机访问 |
| **监听端口** | `PORT` | `8888` | 服务端口号 |
| **项目 ID** | `GOOGLE_CLOUD_PROJECT` | `your-project-id` | **必须修改** |
| **凭证文件** | `GOOGLE_APPLICATION_CREDENTIALS` | `oauth_creds.json` | OAuth 凭证路径 |
| **凭证 JSON** | `GEMINI_CREDENTIALS` | （可选） | 直接提供 OAuth 凭证 JSON |

### ⚠️ 配置注意事项

<details>
<summary><b>重要配置说明</b>（点击展开）</summary>

1. **必须修改的配置**：
   - 项目 ID (`GOOGLE_CLOUD_PROJECT`) - **首次使用必填**

2. **建议修改的配置**：
   - API 密钥 (`GEMINI_AUTH_PASSWORD`) - 默认 `123` 不安全，建议改为强密码

3. **可选修改的配置**：
   - 监听地址 (`HOST`) - 局域网访问时改为 `0.0.0.0`
   - 监听端口 (`PORT`) - 端口冲突时修改

4. **修改配置的方式**：
   - ✅ **推荐**：使用交互式菜单（`主菜单 → 3. 修改配置`）
   - ❌ **不推荐**：手动编辑 `.env` 文件（可能导致格式错误）

</details>

### 📍 配置示例

```bash
# .env 配置文件示例
GEMINI_AUTH_PASSWORD=your_secure_password_here  # 默认：123
HOST=127.0.0.1
PORT=8888
GOOGLE_CLOUD_PROJECT=my-cloud-project-123456    # 必须修改为你的项目 ID
GOOGLE_APPLICATION_CREDENTIALS=oauth_creds.json
# GEMINI_CREDENTIALS={"refresh_token":"..."}    # 可选：直接提供凭证 JSON
```

## 🐛 故障排查

### 🔍 常见问题分类

<details>
<summary><b>❌ HTTP 错误代码</b>（点击展开）</summary>

| 错误代码 | 问题描述 | 可能原因 | 解决方案 |
|---------|---------|---------|---------|
| **401** | 认证失败 | API 密钥错误 | 检查密钥是否为 `123` 或已修改的值 |
| **403** | 权限拒绝 | 项目配置错误 | • 检查项目 ID 是否正确<br>• 确认登录账号与项目匹配<br>• 验证两个 API 均已启用 |
| **404** | 资源未找到 | 路径或模型错误 | 检查模型名称拼写和端点路径 |
| **500** | 服务器内部错误 | 依赖或配置问题 | 查看日志，尝试重新授权或重启服务 |
| **502/503** | 服务不可用 | 服务未运行 | 确认服务已启动 |

</details>

<details>
<summary><b>🔐 OAuth 授权问题</b>（点击展开）</summary>

| 问题 | 现象 | 解决方案 |
|------|------|---------|
| **授权失败** | 无法完成 Google 登录 | 使用 `主菜单 → 2. 重新授权` 清理旧凭证 |
| **凭证过期** | 服务运行一段时间后失败 | 重新授权以刷新 token |
| **账号不匹配** | 403 权限错误 | 确认使用与项目关联的 Google 账号 |
| **浏览器无法打开** | 授权链接无法访问 | 手动复制链接到浏览器 |

</details>

<details>
<summary><b>🌐 网络连接问题</b>（点击展开）</summary>

| 问题 | 现象 | 解决方案 |
|------|------|---------|
| **无法连接服务** | 请求超时 | • 确认服务已启动<br>• 检查端口是否被占用<br>• 验证防火墙设置 |
| **局域网无法访问** | 其他设备连接失败 | • 确认已开启网络监听（`0.0.0.0`）<br>• 检查设备是否在同一网络<br>• 使用 `局域网配置 → 3` 获取正确 IP |
| **获取不到内网IP** | 显示空白或错误 | • 确认 WiFi 已连接<br>• 尝试断开重连网络<br>• 检查网络接口名称 |

</details>

<details>
<summary><b>⚙️ 配置和安装问题</b>（点击展开）</summary>

| 问题 | 现象 | 解决方案 |
|------|------|---------|
| **项目 ID 错误** | 403 或 500 错误 | 使用 `主菜单 → 3 → 3` 修改为正确的项目 ID |
| **依赖安装失败** | Python 包错误 | 使用 `主菜单 → 5 → 2` 重新部署 |
| **端口被占用** | 启动失败 | 使用 `主菜单 → 3 → 2` 修改端口号 |
| **字体显示异常** | 乱码或方框 | 重启 Termux 应用使字体生效 |

</details>

### 🛠️ 排查步骤

按照以下顺序进行问题排查：

```
1. 📺 观看视频教程
   └─> B站教程：https://b23.tv/JKAqkEv
       包含完整安装和配置流程

2. ✅ 验证前置条件
   ├─> Termux 版本 >= v0.118.3
   ├─> 两个 API 均已启用
   └─> 项目 ID 已正确配置

3. 🔄 尝试重新授权
   └─> 主菜单 → 2. 重新授权

4. 📋 检查配置文件
   ├─> 主菜单 → 3. 修改配置
   └─> 确认所有配置项正确

5. 📝 查看详细日志
   └─> 服务启动时的错误信息

6. 🆘 寻求帮助
   ├─> 提交 Issue：https://github.com/print-yuhuan/Gemini-CLI-Termux/issues
   └─> 加入 QQ 群：807134015
```

### 💡 常见问题快速解答

**Q: 首次安装后无法启动服务？**
A: 请确保已配置项目 ID（`主菜单 → 3 → 3`）并完成授权（`主菜单 → 2`）。

**Q: 局域网其他设备无法访问？**
A: 使用 `主菜单 → 3 → 5 → 1` 开启网络监听，然后通过选项 3 获取内网 IP。

**Q: 提示 403 权限错误？**
A: 检查三个关键点：① 项目 ID 是否正确 ② 两个 API 是否都已启用 ③ 登录账号是否与项目匹配。

**Q: 如何修改 API 密码？**
A: 使用 `主菜单 → 3 → 4` 修改连接秘钥（默认密码：123）。

**Q: 授权页面无法自动打开？**
A: 脚本使用 `termux-open-url` 命令自动打开浏览器。如果无法打开，请手动复制终端显示的链接到浏览器中访问。

**Q: 服务更新后出现问题？**
A: 尝试使用 `主菜单 → 5 → 2` 重新部署（会清除配置，请备份重要数据）。

## 🔄 更新与维护

### 🔧 维护操作说明

通过 `主菜单 → 5. 系统管理` 访问维护功能：

<details>
<summary><b>1️⃣ 更新服务（推荐）</b>（点击展开）</summary>

**功能**：将项目更新到最新版本，保留现有配置

**操作流程**：
```
1. 自动备份配置文件
   ├─> .env (环境配置)
   └─> oauth_creds.json (授权凭证)

2. 拉取最新代码
   ├─> 重置 Git 仓库
   └─> 切换到最新版本

3. 恢复配置文件
   └─> 还原备份的配置

4. 更新依赖
   └─> 重新安装 Python 包
```

**适用场景**：
- ✅ 获取最新功能和修复
- ✅ 保留当前配置和授权
- ✅ 常规版本升级

**注意事项**：
- 配置文件会自动备份和恢复
- 如果更新失败，可尝试重新部署

</details>

<details>
<summary><b>2️⃣ 重新部署</b>（点击展开）</summary>

**功能**：完全重新安装项目，清除所有配置和数据

**操作流程**：
```
1. 删除项目目录
   └─> 清除所有文件和配置

2. 重新下载安装脚本
   └─> 获取最新版本

3. 执行完整安装流程
   └─> 从零开始安装
```

**适用场景**：
- ⚠️ 更新失败需要重置
- ⚠️ 配置文件严重损坏
- ⚠️ 想要完全清理重装

**注意事项**：
- ⚠️ **会删除所有配置和授权凭证**
- ⚠️ **需要重新配置项目 ID 和授权**
- ⚠️ 建议提前备份重要数据

</details>

<details>
<summary><b>3️⃣ 卸载服务</b>（点击展开）</summary>

**功能**：完全卸载项目，删除所有文件

**操作流程**：
```
1. 确认卸载操作
   └─> 二次确认防止误操作

2. 删除项目目录
   └─> 完全移除所有文件

3. 清理自启动配置
   └─> 移除 .bashrc 中的启动项
```

**适用场景**：
- ⚠️ 不再使用本项目
- ⚠️ 需要完全清理

**注意事项**：
- ⚠️ **不可逆操作**
- ⚠️ **所有数据将永久删除**
- ⚠️ 卸载后需重新安装才能使用

</details>

### 📅 维护建议

| 维护类型 | 推荐频率 | 说明 |
|---------|---------|------|
| **检查更新** | 每月一次 | 使用 `5 → 1` 获取最新功能 |
| **重新授权** | 凭证过期时 | 使用 `2` 刷新授权 |
| **配置备份** | 修改前 | 手动备份 `.env` 和 `oauth_creds.json` |
| **日志检查** | 遇到问题时 | 查看服务启动时的输出信息 |

## 📝 项目结构

### 📂 目录结构说明

```
Gemini-CLI-Termux/
├── 📜 Setup.sh                     # 自动化部署和管理脚本
├── 🐍 run.py                       # 主程序入口
├── ⚙️ .env                         # 环境变量配置文件
├── 🔐 oauth_creds.json             # Google OAuth 授权凭证
├── 📋 requirements.txt             # Python 依赖列表
├── 🔤 MapleMono.ttf               # Termux 终端字体
├── 📄 LICENSE                      # MIT 开源协议
├── 🚫 .gitignore                   # Git 忽略文件配置
├── 📘 README.md                    # 项目文档
└── 📦 src/                         # 源代码目录
    ├── __init__.py                 # Python 包初始化
    ├── main.py                     # FastAPI 应用主文件
    ├── auth.py                     # OAuth 认证和用户授权
    ├── config.py                   # 配置常量和模型定义
    ├── gemini_routes.py            # 原生 Gemini API 路由
    ├── openai_routes.py            # OpenAI 兼容接口路由
    ├── google_api_client.py        # Google API 客户端封装
    ├── openai_transformers.py      # OpenAI/Gemini 格式转换
    ├── models.py                   # Pydantic 数据模型
    └── utils.py                    # 工具函数
```

### 🗂️ 核心文件说明

<details>
<summary><b>查看详细说明</b>（点击展开）</summary>

| 文件/目录 | 作用 | 是否可修改 |
|----------|------|-----------|
| **Setup.sh** | 一键安装和管理脚本 | ❌ 不建议 |
| **run.py** | 启动服务的主入口 | ❌ 不建议 |
| **.env** | 配置参数（密码、端口等） | ✅ 通过菜单修改 |
| **oauth_creds.json** | Google 授权凭证 | ❌ 自动生成 |
| **requirements.txt** | Python 依赖版本定义 | ❌ 不建议 |
| **MapleMono.ttf** | 优化的等宽字体 | ❌ 不需要 |
| **src/** | 核心业务逻辑代码 | ❌ 不建议 |

</details>

## 🛠️ 技术栈

### 🔧 核心技术

| 技术 | 用途 | 版本 |
|------|------|------|
| **FastAPI** | 现代化异步 Web 框架 | < 0.100 |
| **Uvicorn** | ASGI 高性能服务器 | 最新 |
| **Requests** | HTTP 客户端库 | 最新 |
| **Pydantic** | 数据验证和模型定义 | < 2.0 |
| **Google Auth** | Google OAuth 2.0 认证 | 最新 |
| **Python-dotenv** | 环境变量管理 | 最新 |

### 📦 Python 依赖包

```txt
fastapi<0.100           # 高性能异步 Web 框架
uvicorn                 # ASGI 服务器实现
requests                # HTTP 请求处理
python-dotenv           # .env 文件加载
google-auth-oauthlib    # Google OAuth 2.0 认证
pydantic<2.0           # 数据验证和序列化
```

### 🌟 技术特性

<details>
<summary><b>查看详细特性说明</b>（点击展开）</summary>

**API 设计**：
- ✅ RESTful API 规范
- ✅ OpenAI 兼容接口
- ✅ 原生 Gemini API 支持
- ✅ 流式和非流式响应

**认证安全**：
- ✅ OAuth 2.0 授权
- ✅ 多种 API 认证方式
- ✅ Bearer Token 支持
- ✅ HTTP Basic Auth

**性能优化**：
- ✅ 异步请求处理
- ✅ 流式响应传输
- ✅ 连接池管理
- ✅ 高并发支持

**开发体验**：
- ✅ 自动 API 文档（Swagger UI）
- ✅ 类型检查和验证
- ✅ 详细错误提示
- ✅ 环境变量配置

</details>

## 📄 许可证

本项目基于 **MIT 协议** 开源，详见 [LICENSE](./LICENSE) 文件。

### 📋 许可证要点

- ✅ 可自由使用、复制、修改
- ✅ 可用于商业用途
- ✅ 需保留原始版权声明
- ⚠️ 软件按"原样"提供，不提供任何保证

## 🙏 致谢与贡献

### 💖 特别鸣谢

| 项目/组织 | 贡献 |
|---------|------|
| **[geminicli2api](https://github.com/gzzhongqi/geminicli2api)** | 提供核心 API 转换功能 |
| **[Google Cloud](https://cloud.google.com/)** | Gemini API 和云服务支持 |
| **[Termux](https://termux.dev/)** | Android 终端模拟器平台 |
| **[@print-yuhuan](https://github.com/print-yuhuan)** | Termux 自动化脚本开发 |

### 🤝 参与贡献

欢迎各种形式的贡献：

- 🐛 提交 Bug 报告
- 💡 提出新功能建议
- 📝 改进文档说明
- 🔧 提交代码改进

## 📮 联系与反馈

### 🆘 获取帮助

遇到问题时请按以下顺序寻求帮助：

```
1️⃣ 查看文档
   └─> 阅读本 README 和常见问题部分

2️⃣ 观看教程
   └─> B站视频：https://b23.tv/JKAqkEv

3️⃣ 搜索 Issue
   └─> 查看是否有相同问题已被解决

4️⃣ 提交 Issue
   └─> 详细描述问题和环境信息
   └─> https://github.com/print-yuhuan/Gemini-CLI-Termux/issues

5️⃣ 加入交流群
   └─> QQ群：807134015
```

### 📧 联系方式

- **GitHub Issues**: [提交问题](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues)
- **QQ 交流群**: [807134015](https://qm.qq.com/q/FUme0cSMqV)
- **作者主页**: [@print-yuhuan](https://github.com/print-yuhuan)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！⭐**

*最后更新：2025年11月8日*

</div>