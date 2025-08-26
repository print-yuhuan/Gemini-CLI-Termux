# Gemini-CLI-Termux 自动化部署工具

> ⚠️ 本项目基于 [gzzhongqi/geminicli2api](https://github.com/gzzhongqi/geminicli2api) 进行二次开发，提供 Termux 环境下的自动化部署和管理功能。

## 📌 项目简介

为 Android Termux 用户提供一键部署 Gemini-CLI 反向代理服务的解决方案，通过交互式菜单实现服务的安装、配置和管理，无需复杂操作即可使用 OpenAI 兼容接口调用 Google Gemini。

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

## 🎯 核心功能

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

## 🔧 默认配置

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| API 地址 | `http://127.0.0.1:8888` | OpenAI 兼容接口地址 |
| API 密钥 | `123` | 访问密钥 |
| 监听地址 | `127.0.0.1` | 仅本机访问 |
| 监听端口 | `8888` | 服务端口 |

⚠️ **重要提示：** 除项目 ID 外，其他配置建议保持默认值！

## 🐛 故障排查

### 常见错误代码

| 错误代码 | 问题描述 | 解决方案 |
|---------|---------|---------|
| **401** | 认证失败 | 检查 API 密钥是否正确（默认：`123`） |
| **403** | 权限拒绝 | 1. 检查项目 ID 是否正确<br>2. 确认登录账号与项目匹配<br>3. 验证两个 API 均已启用 |
| **404** | 资源未找到 | 检查模型名称拼写 |
| **连接错误** | 无法访问服务 | 不要修改监听地址和端口，如已修改请恢复默认 |

### 排查建议

1. **首先查看视频教程** - 大部分问题都有演示
2. **使用菜单功能** - 不要手动修改配置文件
3. **保持默认配置** - 仅修改必要的项目 ID
4. **检查 API 启用** - 两个 API 都必须启用

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
└── src/                 # 源代码目录
```

## 📄 许可证

本项目遵循 MIT 协议，详见 [LICENSE](./LICENSE)

## 🙏 致谢

- 核心功能：[geminicli2api](https://github.com/gzzhongqi/geminicli2api)
- 自动化脚本：[Gemini-CLI-Termux](https://github.com/print-yuhuan/Gemini-CLI-Termux)

## 📮 问题反馈

1. 先查看[视频教程](https://b23.tv/JKAqkEv)
2. 阅读常见问题解答
3. 提交 [Issue](https://github.com/print-yuhuan/Gemini-CLI-Termux/issues)

---

*最后更新：2025年8月26日*
