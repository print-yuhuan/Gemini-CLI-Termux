#!/data/data/com.termux/files/usr/bin/bash
# =========================================================================
# Gemini-CLI-Termux 自动化安装与管理脚本
# 用于在 Termux 环境中部署和管理 Gemini API 反向代理服务
# =========================================================================

# ==== 颜色定义(语义化配色方案) ====
# 成功与确认类信息
GREEN='\033[0;32m'
BRIGHT_GREEN='\033[1;32m'

# 警告与提示类信息
YELLOW='\033[0;33m'
BRIGHT_YELLOW='\033[1;33m'

# 错误与危险操作
RED='\033[0;31m'
BRIGHT_RED='\033[1;31m'

# 常规信息与步骤提示
CYAN='\033[0;36m'
BRIGHT_CYAN='\033[1;36m'

# 菜单选项与特殊项
BLUE='\033[0;34m'
BRIGHT_BLUE='\033[1;34m'

# 辅助功能与次要选项
MAGENTA='\033[0;35m'
BRIGHT_MAGENTA='\033[1;35m'

# 格式控制
BOLD='\033[1m'
NC='\033[0m'

# =========================================================================
# 全局变量配置
# =========================================================================
GEMINI_CLI_TERMUX_DIR="$HOME/Gemini-CLI-Termux"                  # 项目安装目录
GEMINI_CLI_TERMUX_REPO="https://github.com/print-yuhuan/Gemini-CLI-Termux.git"  # GitHub仓库地址
FONT_URL="https://github.com/print-yuhuan/Gemini-CLI-Termux/raw/refs/heads/main/MapleMono.ttf"  # 字体文件下载地址
FONT_DIR="$HOME/.termux"                                         # Termux配置目录
FONT_PATH="$FONT_DIR/font.ttf"                                   # 字体文件存放路径

# =========================================================================
# 通用工具函数
# =========================================================================

# 提示用户按键返回菜单
press_any_key() { echo -e "${CYAN}${BOLD}► 按任意键返回菜单...${NC}"; read -n1 -s; }

# 检查关键文件是否存在
check_file_exists() {
    if [ ! -f "$1" ]; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 缺少关键文件：$1${NC}"
        echo -e "${YELLOW}${BOLD}请检查项目文件完整性后重试${NC}"
        press_any_key
        exit 1
    fi
}

# 确保使用 Bash Shell 执行
ensure_bash_shell() {
    if [ -z "$BASH_VERSION" ]; then
        exec bash "$0" "$@"
    fi
}

# 检查命令是否存在
command_exists() { command -v "$1" >/dev/null 2>&1; }

# 智能安装软件包(已安装则跳过)
install_package_if_missing() {
    local check_cmd="$1"
    local package_name="$2"
    local display_name="${3:-$package_name}"

    if command_exists "$check_cmd"; then
        echo -e "${GREEN}${BOLD}✓ $display_name 已安装，跳过${NC}"
        return 0
    fi

    echo -e "${CYAN}${BOLD}► 正在安装 $display_name...${NC}"
    if pkg install -y "$package_name"; then
        echo -e "${BRIGHT_GREEN}${BOLD}✓ $display_name 安装成功${NC}"
        return 0
    fi

    echo -e "${BRIGHT_RED}${BOLD}✗ $display_name 安装失败${NC}"
    echo -e "${YELLOW}${BOLD}请检查网络连接或手动安装后重试${NC}"
    return 1
}

# 获取局域网 IPv4 地址(优先 WiFi/以太网，排除 VPN 和回环地址)
get_lan_ipv4() {
    local ip iface

    if command_exists ip; then
        # 优先获取 WiFi/以太网接口地址，排除 VPN(tun) 地址
        while IFS= read -r iface; do
            case "$iface" in
                wlan*|eth*|en*)
                    ip=$(ip -4 -o addr show dev "$iface" scope global 2>/dev/null | awk '{print $4}' | cut -d'/' -f1 | head -n1)
                    if [ -n "$ip" ]; then
                        echo "$ip"
                        return 0
                    fi
                    ;;
            esac
        done < <(ip -4 -o addr show scope global 2>/dev/null | awk '{print $2}' | uniq)

        # 备用方案：获取任意非 lo/tun/ppp 接口的地址
        ip=$(ip -4 -o addr show scope global 2>/dev/null | awk '!/ (lo|tun|ppp)/ {print $4}' | cut -d'/' -f1 | head -n1)
        if [ -n "$ip" ]; then
            echo "$ip"
            return 0
        fi
    fi

    if command_exists ifconfig; then
        # 遍历 wlan0-wlan5 接口
        for i in $(seq 0 5); do
            ip=$(ifconfig 2>/dev/null | grep -A 1 "wlan$i" | grep "inet " | awk '{print $2}' | head -n1)
            if [ -n "$ip" ]; then
                echo "$ip"
                return 0
            fi
        done

        # 获取第一个非回环、非 tun 接口的地址
        ip=$(ifconfig 2>/dev/null | awk '
            /^[a-zA-Z0-9]+:/ {
                iface=$1
                sub(":", "", iface)
            }
            /inet / && $2 != "127.0.0.1" && iface !~ /^tun/ {
                print $2
                exit
            }')
        if [ -n "$ip" ]; then
            echo "$ip"
            return 0
        fi
    fi
    return 1
}

ensure_bash_shell "$@"

# =========================================================================
# 核心功能：自动安装与初始化
# =========================================================================
install_gemini_cli_termux() {
    # [1/8] 环境检测
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [1/8] 环境检测                  ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    if [ -z "$PREFIX" ] || [[ "$PREFIX" != "/data/data/com.termux/files/usr" ]]; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 检测到非 Termux 环境${NC}"
        echo -e "${YELLOW}${BOLD}请在 Termux 应用中执行此脚本${NC}"
        exit 1
    fi
    if ! command_exists pkg; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 未检测到 pkg 命令${NC}"
        echo -e "${YELLOW}${BOLD}请确认 Termux 环境是否完整${NC}"
        exit 1
    fi
    echo -e "${BRIGHT_GREEN}${BOLD}✓ 环境检测通过 - Termux 环境正常${NC}\n"

    # [2/8] 更新包管理器
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [2/8] 更新包管理器              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    local mirror_source="$PREFIX/etc/termux/mirrors/europe/packages.termux.dev"
    local mirror_target="$PREFIX/etc/termux/chosen_mirrors"
    if [ -f "$mirror_source" ]; then
        mkdir -p "$(dirname "$mirror_target")"
        ln -sf "$mirror_source" "$mirror_target"
        echo -e "${GREEN}${BOLD}✓ 已配置 Termux 官方镜像源${NC}"
    else
        echo -e "${YELLOW}${BOLD}⚠ 未检测到官方镜像配置，保留当前镜像设置${NC}"
    fi
    if ! pkg update; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 软件包索引更新失败${NC}"
        echo -e "${YELLOW}${BOLD}请检查网络连接后重试${NC}"
        exit 1
    fi
    if ! pkg upgrade -y -o Dpkg::Options::="--force-confnew"; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 软件包升级失败${NC}"
        echo -e "${YELLOW}${BOLD}请确认网络连接和磁盘空间后重试${NC}"
        exit 1
    fi
    echo -e "${BRIGHT_GREEN}${BOLD}✓ 包管理器更新完成${NC}\n"

    # [3/8] 安装系统依赖
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [3/8] 安装系统依赖              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    local install_errors=0
    install_package_if_missing "python" "python" "Python" || install_errors=1
    install_package_if_missing "git" "git" "Git" || install_errors=1
    install_package_if_missing "curl" "curl" "curl" || install_errors=1

    if [ "$install_errors" -ne 0 ]; then
        echo -e "${BRIGHT_RED}${BOLD}✗ 必要依赖安装失败${NC}"
        echo -e "${YELLOW}${BOLD}请修复上述错误后重新执行脚本${NC}"
        exit 1
    fi

    if ! install_package_if_missing "termux-reload-settings" "termux-api" "Termux:API"; then
        echo -e "${YELLOW}${BOLD}⚠ Termux:API 未能自动安装，字体热刷新功能将不可用${NC}"
        echo -e "${YELLOW}${BOLD}  可手动安装或稍后执行 termux-reload-settings${NC}"
    fi

    echo -e "${BRIGHT_GREEN}${BOLD}✓ 系统依赖安装完成${NC}\n"

    # [4/8] 配置终端字体
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [4/8] 配置终端字体              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    mkdir -p "$FONT_DIR"
    if [ -f "$FONT_PATH" ]; then
        echo -e "${YELLOW}${BOLD}⚠ 字体文件已存在，跳过下载${NC}"
    else
        echo -e "${CYAN}${BOLD}► 正在下载 MapleMono 字体...${NC}"
        if curl -L --progress-bar -o "$FONT_PATH" "$FONT_URL"; then
            echo -e "${GREEN}${BOLD}✓ 字体已保存至 ~/.termux/font.ttf${NC}"
        else
            echo -e "${RED}${BOLD}✗ 字体下载失败${NC}"
            echo -e "${YELLOW}${BOLD}请检查网络连接或稍后手动下载${NC}"
        fi
    fi

    if [ -f "$FONT_PATH" ]; then
        if command -v termux-reload-settings >/dev/null 2>&1; then
            termux-reload-settings \
            && echo -e "${BRIGHT_GREEN}${BOLD}✓ 配置已自动刷新，字体已生效${NC}" \
            || echo -e "${YELLOW}${BOLD}⚠ 自动刷新失败，请手动重启 Termux 应用${NC}"
        else
            echo -e "${YELLOW}${BOLD}⚠ 未检测到 termux-reload-settings${NC}"
            echo -e "${YELLOW}${BOLD}  请手动重启 Termux 应用使字体生效${NC}"
        fi
        echo -e "${BRIGHT_GREEN}${BOLD}✓ 终端字体配置完成${NC}\n"
    fi

    # [5/8] 克隆项目仓库
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [5/8] 克隆项目仓库              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    if [ -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
        echo -e "${YELLOW}${BOLD}⚠ 项目仓库已存在，跳过克隆${NC}"
    else
        rm -rf "$GEMINI_CLI_TERMUX_DIR"
        echo -e "${CYAN}${BOLD}► 正在从 GitHub 克隆项目...${NC}"
        if git clone "$GEMINI_CLI_TERMUX_REPO" "$GEMINI_CLI_TERMUX_DIR"; then
            echo -e "${BRIGHT_GREEN}${BOLD}✓ 项目仓库克隆成功${NC}\n"
        else
            echo -e "${BRIGHT_RED}${BOLD}✗ 仓库克隆失败${NC}"
            echo -e "${YELLOW}${BOLD}请检查网络连接或 GitHub 访问${NC}"
            exit 1
        fi
    fi

    # [6/8] 验证项目文件
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [6/8] 验证项目文件              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}✗ 无法进入项目目录${NC}"; exit 1; }
    check_file_exists "requirements.txt"
    check_file_exists ".env"
    check_file_exists "run.py"
    echo -e "${BRIGHT_GREEN}${BOLD}✓ 关键文件验证通过${NC}\n"

    # [7/8] 配置开机自启
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [7/8] 配置开机自启              ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    PROFILE_FILE=""
    for pf in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
        if [ -f "$pf" ]; then
            PROFILE_FILE="$pf"
            break
        fi
    done
    if [ -z "$PROFILE_FILE" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    fi
    touch "$PROFILE_FILE"
    if ! grep -qE 'bash[ ]+\$HOME/Gemini-CLI-Termux/Setup\.sh' "$PROFILE_FILE"; then
        if [ -s "$PROFILE_FILE" ]; then
            echo '' >> "$PROFILE_FILE"
        fi
        echo '# Gemini-CLI-Termux 菜单自启动' >> "$PROFILE_FILE"
        echo 'bash $HOME/Gemini-CLI-Termux/Setup.sh' >> "$PROFILE_FILE"
        echo -e "${GREEN}${BOLD}✓ 已添加至 $PROFILE_FILE${NC}"
        echo -e "${GREEN}${BOLD}  后续每次启动 Termux 将自动显示菜单${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}✓ 开机自启配置完成${NC}\n"
    else
        echo -e "${YELLOW}${BOLD}⚠ 开机自启已配置，跳过${NC}\n"
    fi

    # [8/8] 安装 Python 依赖包
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   [8/8] 安装 Python 依赖包        ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    if ! python -m pip --version >/dev/null 2>&1; then
        echo -e "${CYAN}${BOLD}► 正在安装 pip 包管理器...${NC}"
        pkg install -y python-pip
        if ! python -m pip --version >/dev/null 2>&1; then
            echo -e "${BRIGHT_RED}${BOLD}✗ pip 安装失败${NC}"
            echo -e "${YELLOW}${BOLD}请检查网络连接${NC}"
            exit 1
        fi
    fi
    export PIP_BREAK_SYSTEM_PACKAGES=1
    echo -e "${CYAN}${BOLD}► 正在安装 Python 依赖包（可能需要几分钟）...${NC}"
    local pip_cmd=(python -m pip install --no-cache-dir -r requirements.txt)
    if python -m pip help install 2>/dev/null | grep -q -- "--break-system-packages"; then
        pip_cmd+=(--break-system-packages)
    fi
    if "${pip_cmd[@]}"; then
        echo -e "${BRIGHT_GREEN}${BOLD}✓ Python 依赖包安装完成${NC}\n"
    else
        echo -e "${BRIGHT_RED}${BOLD}✗ Python 依赖包安装失败${NC}"
        echo -e "${YELLOW}${BOLD}请检查网络连接和磁盘空间${NC}"
        exit 1
    fi

    echo -e "${BRIGHT_GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BRIGHT_GREEN}${BOLD}  ✓ Gemini-CLI-Termux 安装成功！${NC}"
    echo -e "${BRIGHT_GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    press_any_key
}

# =========================================================================
# 服务启动与授权管理
# =========================================================================

# 从 .env 文件读取配置值
get_env_value() {
    cd "$GEMINI_CLI_TERMUX_DIR" 2>/dev/null || return
    if [ -f ".env" ]; then
        grep "^$1=" .env | head -n1 | cut -d'=' -f2 | xargs
    fi
}

# 启动 Gemini API 反向代理服务
start_reverse_proxy() {
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   启动 Gemini API 服务            ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || {
        echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
        echo -e "${YELLOW}${BOLD}请确认项目已正确安装${NC}"
        press_any_key
        return
    }
    check_file_exists "run.py"
    pkill -f "python run.py"
    echo -e "${GREEN}${BOLD}► 正在启动服务...${NC}\n"
    python run.py
    echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 重新进行 Google 账号授权
relogin() {
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   重新授权 Google 账号            ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || {
        echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
        press_any_key
        return
    }
    rm -f oauth_creds.json
    echo -e "${YELLOW}${BOLD}⚠ 已清除旧的授权凭证${NC}"
    echo -e "${CYAN}${BOLD}► 即将启动服务并进行重新授权...${NC}\n"
    start_reverse_proxy
    echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# =========================================================================
# 配置文件修改功能
# =========================================================================

# 修改服务监听地址
change_env_host() {
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   修改监听地址                    ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || {
        echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
        press_any_key
        return
    }
    check_file_exists ".env"
    old=$(grep "^HOST=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${CYAN}当前监听地址：${BRIGHT_YELLOW}${BOLD}$old${NC}"
    echo -e "${YELLOW}${BOLD}提示：127.0.0.1=仅本机访问, 0.0.0.0=允许局域网访问${NC}"
    while true; do
        echo -ne "${CYAN}请输入新的 IPv4 地址（留空取消）：${NC}"
        read ans
        [ -z "$ans" ] && echo -e "${YELLOW}${BOLD}✓ 已取消修改${NC}" && press_any_key && return
        if [[ "$ans" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
            valid=1
            for seg in $(echo $ans | tr '.' ' '); do
                if (( seg < 0 || seg > 255 )); then valid=0; break; fi
            done
            if [ $valid -eq 1 ]; then
                break
            fi
        fi
        echo -e "${RED}${BOLD}✗ 地址格式无效，请输入标准 IPv4 地址${NC}"
    done
    sed -i "s/^HOST=.*/HOST=$ans/" .env
    echo -e "${BRIGHT_GREEN}${BOLD}✓ 监听地址已更新为：$ans${NC}"
    press_any_key
}

# 修改服务监听端口
change_env_port() {
    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   修改监听端口                    ┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || {
        echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
        press_any_key
        return
    }
    check_file_exists ".env"
    old=$(grep "^PORT=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${CYAN}当前监听端口：${BRIGHT_YELLOW}${BOLD}$old${NC}"
    echo -e "${YELLOW}${BOLD}提示：有效端口范围 1-65535${NC}"
    while true; do
        echo -ne "${CYAN}请输入新的端口号（留空取消）：${NC}"
        read ans
        [ -z "$ans" ] && echo -e "${YELLOW}${BOLD}✓ 已取消修改${NC}" && press_any_key && return
        if ! [[ "$ans" =~ ^[0-9]+$ ]] || [ "$ans" -lt 1 ] || [ "$ans" -gt 65535 ]; then
            echo -e "${RED}${BOLD}✗ 端口无效，请输入 1-65535 之间的数字${NC}"
            continue
        fi
        break
    done
    sed -i "s/^PORT=.*/PORT=$ans/" .env
    echo -e "${BRIGHT_GREEN}${BOLD}✓ 监听端口已更新为：$ans${NC}"
    press_any_key
}

# 通用配置项修改函数
change_env_keyvalue() {
    local title="修改 $2"
    local title_len=$(echo -n "$title" | wc -m)
    local total_width=35
    local padding=$((total_width - title_len - 3))
    local spaces=$(printf '%*s' "$padding" '')

    echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┃   ${title}${spaces}┃${NC}"
    echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || {
        echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
        press_any_key
        return
    }
    check_file_exists ".env"
    old=$(grep "^$1=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${CYAN}当前 $2：${BRIGHT_YELLOW}${BOLD}$old${NC}"
    echo -ne "${CYAN}请输入新的值（留空取消）：${NC}"; read ans
    if [ -n "$ans" ]; then
        sed -i "s/^$1=.*/$1=$ans/" .env
        echo -e "${BRIGHT_GREEN}${BOLD}✓ $2 已更新为：${ans}${NC}"
    else
        echo -e "${YELLOW}${BOLD}✓ 已取消修改${NC}"
    fi
    press_any_key
}

# 局域网访问配置菜单
lan_config_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   局域网访问配置                  ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级菜单${NC}"
        echo -e "${GREEN}${BOLD}1. 开启网络监听${NC}"
        echo -e "${RED}${BOLD}2. 关闭网络监听${NC}"
        echo -e "${BLUE}${BOLD}3. 获取内网地址${NC}"
        echo -e "${MAGENTA}${BOLD}4. 查看连接帮助${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-4）：${NC}"
        read -n1 lan_choice; echo
        case "$lan_choice" in
            0) break ;;
            1)
                cd "$GEMINI_CLI_TERMUX_DIR" || {
                    echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
                    press_any_key
                    continue
                }
                sed -i "s/^HOST=.*/HOST=0.0.0.0/" .env
                echo -e "${BRIGHT_GREEN}${BOLD}✓ 网络监听已开启${NC}"
                echo -e "${GREEN}${BOLD}  现在允许局域网内其他设备访问${NC}"
                press_any_key
                ;;
            2)
                cd "$GEMINI_CLI_TERMUX_DIR" || {
                    echo -e "${BRIGHT_RED}${BOLD}✗ 未找到项目目录${NC}"
                    press_any_key
                    continue
                }
                sed -i "s/^HOST=.*/HOST=127.0.0.1/" .env
                echo -e "${BRIGHT_GREEN}${BOLD}✓ 网络监听已关闭${NC}"
                echo -e "${YELLOW}${BOLD}  现在仅限本机访问${NC}"
                press_any_key
                ;;
            3)
                ip=$(get_lan_ipv4)
                if [ -n "$ip" ]; then
                    PORT=$(get_env_value PORT)
                    echo -e "${GREEN}${BOLD}检测到局域网地址：${NC}"
                    echo -e "${BRIGHT_GREEN}${BOLD}http://$ip:${PORT:-8888}/${NC}"
                    echo -e "\n${CYAN}${BOLD}请在同一局域网的其他设备上访问该地址${NC}"
                else
                    echo -e "${YELLOW}${BOLD}⚠ 未检测到有效的局域网 IPv4 地址${NC}"
                    echo -e "${CYAN}${BOLD}请确认设备已连接 WiFi 或热点后重试${NC}"
                fi
                press_any_key
                ;;
            4)
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━ 局域网连接使用指南 ━━━━${NC}\n"
                echo -e "${BRIGHT_CYAN}${BOLD}【准备工作】${NC}"
                echo -e "${CYAN}${BOLD}  1.${NC}${BOLD} 确保本项目已正确安装${NC}"
                echo -e "${CYAN}${BOLD}  2.${NC}${BOLD} 确保本机和访问设备连接同一 WiFi 或热点${NC}\n"
                echo -e "${BRIGHT_CYAN}${BOLD}【操作步骤】${NC}"
                echo -e "${CYAN}${BOLD}  1.${NC}${BOLD} 在上级菜单选择 ${GREEN}1. 开启网络监听${NC}"
                echo -e "${CYAN}${BOLD}  2.${NC}${BOLD} 选择 ${BLUE}3. 获取内网地址${NC}${BOLD} 获取访问地址${NC}"
                echo -e "${CYAN}${BOLD}  3.${NC}${BOLD} 返回主菜单选择 ${GREEN}1. 启动服务${NC}${BOLD} 并保持运行${NC}"
                echo -e "${CYAN}${BOLD}  4.${NC}${BOLD} 在其他设备浏览器输入获取的地址访问${NC}\n"
                echo -e "${BRIGHT_CYAN}${BOLD}【常见问题】${NC}"
                echo -e "${YELLOW}${BOLD}  ●${NC}${BOLD} 获取不到内网IP？${NC}"
                echo -e "${BOLD}     ${CYAN}→${NC}${BOLD} 确认 WiFi/热点已连接，尝试断开重连${NC}"
                echo -e "${YELLOW}${BOLD}  ●${NC}${BOLD} 外部设备无法访问？${NC}"
                echo -e "${BOLD}     ${CYAN}→${NC}${BOLD} 确保已开启网络监听，且设备在同一局域网${NC}"
                echo -e "${YELLOW}${BOLD}  ●${NC}${BOLD} 设备重启或网络切换？${NC}"
                echo -e "${BOLD}     ${CYAN}→${NC}${BOLD} 需重新获取内网 IP 地址${NC}\n"
                echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                press_any_key
                ;;
            *)
                echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1
                ;;
        esac
    done
}

# 配置修改主菜单
reverse_proxy_config_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   服务配置管理                    ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级菜单${NC}"
        echo -e "${BLUE}${BOLD}1. 修改监听地址${NC}"
        echo -e "${GREEN}${BOLD}2. 修改监听端口${NC}"
        echo -e "${MAGENTA}${BOLD}3. 修改项目标识${NC}"
        echo -e "${BRIGHT_MAGENTA}${BOLD}4. 修改连接秘钥${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}5. 局域网配置项${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-5）：${NC}"
        read -n1 rev_choice; echo
        case "$rev_choice" in
            0) break ;;
            1) change_env_host ;;
            2) change_env_port ;;
            3) change_env_keyvalue "GOOGLE_CLOUD_PROJECT" "Google Cloud 项目ID" ;;
            4) change_env_keyvalue "GEMINI_AUTH_PASSWORD" "API 接口访问秘钥" ;;
            5) lan_config_menu ;;
            *) echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# Google Cloud 快速访问菜单
# =========================================================================

# Google Cloud 控制台快速访问
cloud_config_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   Google Cloud 控制台             ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级菜单${NC}"
        echo -e "${GREEN}${BOLD}1. 获取项目 ID${NC}"
        echo -e "${BLUE}${BOLD}2. 管理 Gemini for Google Cloud${NC}"
        echo -e "${MAGENTA}${BOLD}3. 管理 Gemini Cloud Assist API${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-3）：${NC}"
        read -n1 cloud_choice; echo
        case "$cloud_choice" in
            0) break ;;
            1)
                echo -e "${GREEN}${BOLD}► 正在打开 Google Cloud 控制台...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fwelcome%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                echo -e "${CYAN}${BOLD}请在浏览器中查看项目 ID${NC}"
                press_any_key
                ;;
            2)
                echo -e "${BLUE}${BOLD}► 正在打开 Gemini for Google Cloud API 管理页...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Flibrary%2Fcloudaicompanion.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                echo -e "${CYAN}${BOLD}请在浏览器中启用该 API${NC}"
                press_any_key
                ;;
            3)
                echo -e "${MAGENTA}${BOLD}► 正在打开 Gemini Cloud Assist API 管理页...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Fapi%2Fgeminicloudassist.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                echo -e "${CYAN}${BOLD}请在浏览器中启用该 API${NC}"
                press_any_key
                ;;
            *)
                echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 系统维护与管理
# =========================================================================

# 系统管理菜单
maintenance_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   系统管理                        ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级菜单${NC}"
        echo -e "${GREEN}${BOLD}1. 更新服务${NC}"
        echo -e "${BLUE}${BOLD}2. 重新部署${NC}"
        echo -e "${MAGENTA}${BOLD}3. 卸载服务${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-3）：${NC}"
        read -n1 main_choice; echo
        case "$main_choice" in
            0) break ;;
            1)
                echo -e "${GREEN}${BOLD}► 正在更新项目...${NC}"
                cd "$GEMINI_CLI_TERMUX_DIR" || {
                    echo -e "${BRIGHT_RED}${BOLD}✗ 项目目录不存在${NC}"
                    press_any_key
                    continue
                }

                echo -e "${CYAN}${BOLD}► 备份配置文件...${NC}"
                if [ -f .env ]; then cp .env .env.bak; fi
                if [ -f oauth_creds.json ]; then cp oauth_creds.json oauth_creds.json.bak; fi

                echo -e "${CYAN}${BOLD}► 拉取最新代码...${NC}"
                git fetch origin
                git reset --hard origin/main

                echo -e "${CYAN}${BOLD}► 恢复配置文件...${NC}"
                if [ -f .env.bak ]; then mv -f .env.bak .env; fi
                if [ -f oauth_creds.json.bak ]; then mv -f oauth_creds.json.bak oauth_creds.json; fi

                echo -e "${CYAN}${BOLD}► 更新 Python 依赖...${NC}"
                python -m pip install -r requirements.txt \
                    && echo -e "${BRIGHT_GREEN}${BOLD}✓ 更新完成${NC}" \
                    || echo -e "${BRIGHT_RED}${BOLD}✗ 更新失败，请检查网络连接${NC}"

                press_any_key
                ;;
            2)
                echo -e "${BRIGHT_RED}${BOLD}⚠ 警告：即将完全重新部署项目${NC}"
                echo -e "${YELLOW}${BOLD}此操作将删除当前目录并重新安装${NC}"
                echo -ne "${CYAN}确认继续？（y/N）：${NC}"
                read -n1 confirm; echo
                if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                    cd "$HOME" || exit 1
                    [ -d "$GEMINI_CLI_TERMUX_DIR" ] && rm -rf "$GEMINI_CLI_TERMUX_DIR"
                    echo -e "${GREEN}${BOLD}► 开始重新部署...${NC}\n"
                    install_gemini_cli_termux
                else
                    echo -e "${YELLOW}${BOLD}✓ 已取消重新部署${NC}"
                    press_any_key
                fi
                ;;
            3)
                echo -e "${BRIGHT_RED}${BOLD}⚠ 警告：即将卸载 Gemini-CLI-Termux${NC}"
                echo -e "${YELLOW}${BOLD}此操作不可逆，将删除所有项目文件${NC}"
                echo -ne "${CYAN}确认继续？（y/N）：${NC}"
                read -n1 confirm; echo
                if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                    [ -d "$GEMINI_CLI_TERMUX_DIR" ] && rm -rf "$GEMINI_CLI_TERMUX_DIR"
                    echo -e "${BRIGHT_GREEN}${BOLD}✓ 已卸载 Gemini-CLI-Termux${NC}"
                    echo -e "${CYAN}${BOLD}感谢使用，再见！${NC}"
                    press_any_key
                    exit 0
                else
                    echo -e "${YELLOW}${BOLD}✓ 已取消卸载${NC}"
                    press_any_key
                fi
                ;;
            *) echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 帮助与反馈
# =========================================================================

# 关于脚本与反馈菜单
about_script_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   关于与反馈                      ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级菜单${NC}"
        echo -e "${GREEN}${BOLD}1. 作者信息${NC}"
        echo -e "${BLUE}${BOLD}2. 加群交流${NC}"
        echo -e "${MAGENTA}${BOLD}3. 邮件反馈${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-3）：${NC}"
        read -n1 about_choice; echo
        case "$about_choice" in
            0) break ;;
            1)
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━ 作者信息 ━━━━${NC}\n"
                echo -e "${GREEN}作者：${BOLD}欤歡${NC}"
                echo -e "${MAGENTA}QQ群：${BOLD}807134015${NC}"
                echo -e "${BLUE}邮箱：${BOLD}print.yuhuan@gmail.com${NC}\n"
                echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                press_any_key
                ;;
            2)
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━ 加群交流 ━━━━${NC}\n"
                echo -e "${GREEN}欢迎加入 ${BOLD}SillyTavern-Termux${NC}${GREEN} 用户交流群！${NC}"
                echo -e "${MAGENTA}QQ 群号：${BOLD}807134015${NC}\n"
                if command -v am >/dev/null 2>&1; then
                    am start -a android.intent.action.VIEW -d "mqqapi://card/show_pslcard?src_type=internal&version=1&uin=807134015&card_type=group&source=qrcode" >/dev/null 2>&1 \
                        && echo -e "${GREEN}${BOLD}✓ 已尝试调用 QQ 客户端打开加群页面${NC}" \
                        || echo -e "${YELLOW}${BOLD}⚠ 无法自动打开 QQ，请手动搜索群号加入${NC}"
                else
                    echo -e "${YELLOW}${BOLD}⚠ 当前环境不支持自动打开 QQ${NC}"
                    echo -e "${CYAN}${BOLD}  请手动在 QQ 中搜索群号：807134015${NC}"
                fi
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                press_any_key
                ;;
            3)
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━ 邮件反馈 ━━━━${NC}\n"
                echo -e "${BLUE}收件人：${BOLD}print.yuhuan@gmail.com${NC}\n"
                if command -v am >/dev/null 2>&1; then
                    am start -a android.intent.action.SENDTO -d mailto:print.yuhuan@gmail.com >/dev/null 2>&1 \
                        && echo -e "${GREEN}${BOLD}✓ 已调用系统邮件应用${NC}" \
                        || echo -e "${YELLOW}${BOLD}⚠ 无法自动打开邮件应用${NC}\n${CYAN}${BOLD}  请手动发送邮件至：print.yuhuan@gmail.com${NC}"
                else
                    echo -e "${YELLOW}${BOLD}⚠ 当前环境不支持自动打开邮件应用${NC}"
                    echo -e "${CYAN}${BOLD}  请手动发送邮件至：print.yuhuan@gmail.com${NC}"
                fi
                echo -e "\n${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                press_any_key
                ;;
            *) echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 主菜单
# =========================================================================

# 主菜单 - 程序入口
main_menu() {
    while true; do
        clear
        echo -e "${BRIGHT_CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┃   Gemini-CLI-Termux 主菜单        ┃${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
        echo -e "${RED}${BOLD}0. 退出脚本${NC}"
        echo -e "${GREEN}${BOLD}1. 启动服务${NC}"
        echo -e "${BLUE}${BOLD}2. 重新授权${NC}"
        echo -e "${MAGENTA}${BOLD}3. 修改配置${NC}"
        echo -e "${BRIGHT_MAGENTA}${BOLD}4. 谷歌云项${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}5. 系统管理${NC}"
        echo -e "${CYAN}${BOLD}6. 关于脚本${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-6）：${NC}"
        read -n1 choice; echo
        case "$choice" in
            0)
                echo -e "${YELLOW}${BOLD}✓ 感谢使用，再见！${NC}"
                sleep 0.5
                clear
                exit 0
                ;;
            1) start_reverse_proxy ;;
            2) relogin ;;
            3) reverse_proxy_config_menu ;;
            4) cloud_config_menu ;;
            5) maintenance_menu ;;
            6) about_script_menu ;;
            *) echo -e "${RED}${BOLD}✗ 无效选项${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 脚本启动入口
# =========================================================================

# 检查项目是否已安装，未安装则自动执行安装流程
if [ ! -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
    echo -e "${YELLOW}${BOLD}⚠ 未检测到 Gemini-CLI-Termux 项目${NC}"
    echo -e "${CYAN}${BOLD}► 即将开始自动安装...${NC}\n"
    install_gemini_cli_termux
fi

# 进入主菜单循环
main_menu
