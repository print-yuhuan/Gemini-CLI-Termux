# Gemini-CLI-API-Termux 自动化部署工具

> ⚠️ 本项目基于 [gzzhongqi/geminicli2api](https://github.com/gzzhongqi/geminicli2api) 项目进行二次开发，自动化脚本及部署流程由 [print-yuhuan](https://github.com/print-yuhuan) 优化。核心功能和 LICENSE 均遵循 MIT 协议。

## 📌 项目简介

本项目提供一键式脚本，用于在 Termux 环境中自动部署和管理 Gemini-CLI-API-Termux 服务。脚本具备自动检测环境、自动安装依赖、仓库一键克隆、配置管理和服务维护等功能，通过交互式菜单实现 Google Gemini API 反向代理服务的快速安装、配置和运行。

## ⚡ 快速开始

### 一键部署

在 Termux 中运行以下命令自动完成环境检测、依赖安装及服务部署：

```bash
curl -O https://raw.githubusercontent.com/print-yuhuan/Gemini-CLI-API-Termux/main/Install.sh && bash Install.sh
```

## 📋 前置要求

### 1. Termux 版本要求
- **推荐版本**：v0.118.3 或 v0.119.0-beta.3 及以上
- ⚠️ 旧版 Termux 可能存在兼容性问题，脚本将自动检测并提醒

### 2. Google Cloud 配置
在使用本项目之前，您需要：

1. **获取 Google Cloud 项目 ID**
   - 访问 [Google Cloud Console](https://console.cloud.google.com/welcome)
   - 创建或选择现有项目，记录项目 ID

2. **启用必要的 API 服务**
   - [Gemini for Google Cloud](https://console.cloud.google.com/apis/library/cloudaicompanion.googleapis.com)
   - [Gemini Cloud Assist](https://console.cloud.google.com/apis/library/geminicloudassist.googleapis.com)

## 🎯 功能特性

- **自动化安装**：自动检测 Termux 环境和依赖，自动克隆仓库与初始化配置
- **一键部署/重装**：支持一键初装和菜单6一键重装，自动清理旧目录
- **智能检测**：检测依赖、端口占用、关键文件完整性，自动提示
- **交互式菜单**：支持服务启动、重新登录、密码/项目ID/端口修改、重装等常用管理操作
- **配置管理**：便捷修改 .env 文件中的项目 ID、端口、密码等参数
- **端口检测**：自动检测端口占用，避免冲突
- **重新认证**：支持清理认证缓存后重新登录 Google 账号

## 📖 使用说明

### 菜单功能

脚本启动后将显示如下菜单：

| 选项 | 功能         | 说明                                       |
|------|--------------|--------------------------------------------|
| 0    | 退出脚本     | 安全退出脚本程序                           |
| 1    | 启动服务     | 启动 Gemini-CLI-API-Termux 反向代理服务    |
| 2    | 重新登录     | 清除认证缓存并重新登录 Google 账号         |
| 3    | 修改密码     | 设置 API 接口访问密码                      |
| 4    | 修改项目ID   | 更改 Google Cloud 项目 ID                  |
| 5    | 修改端口     | 调整服务监听端口（如 8888）                |
| 6    | 重新安装     | 一键清理当前目录并重新部署本项目           |

> **说明：** 首次运行脚本将自动检测并安装本项目，无需手动克隆仓库。

## ⚠️ 重要提醒

- **强烈建议**：除项目 ID 外，其他配置项请保持默认值。随意修改可能触发未知错误。
- ✅ 推荐修改：`GOOGLE_CLOUD_PROJECT`（项目 ID）
- ❌ 不建议修改：HOST、PORT 等其他配置项，除非有特殊需求

## 🔧 技术栈

- **运行环境**：Termux (Android)
- **编程语言**：Shell、Python
- **依赖工具**：Git, Rust, Pip, Python
- **核心项目**：[geminicli2api](https://github.com/gzzhongqi/geminicli2api)

## 🐛 常见问题与排查

1. **非 Termux 环境错误**
   - 脚本自动检测，非 Termux 环境将直接退出
2. **依赖安装失败**
   - 检查网络连接，可尝试更换 Termux 镜像源
3. **端口被占用**
   - 启动服务前自动检测端口占用，如被占用请修改端口或释放端口
4. **认证失败**
   - 使用菜单 2 重新登录，并确认 Google Cloud API 已正确启用

## 📄 许可证

本项目遵循 MIT 开源协议，保留原作者及本项目 LICENSE 文件和相关声明。详细条款见 [LICENSE](./LICENSE)。

## 🙏 致谢

- 核心功能来源：[gzzhongqi/geminicli2api](https://github.com/gzzhongqi/geminicli2api)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 📮 联系方式

如有问题或建议，请通过 [Issues](https://github.com/print-yuhuan/Gemini-CLI-API-Termux/issues) 页面反馈。

---

*最后更新：2025年8月19日*