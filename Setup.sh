#!/data/data/com.termux/files/usr/bin/bash
# =========================================================================
# Gemini-CLI-Termux 安装与管理脚本
# =========================================================================

# ==== 彩色输出定义 ====
YELLOW='\033[1;33m'
GREEN='\033[38;5;40m'
BLUE='\033[38;5;33m'
MAGENTA='\033[38;5;129m'
CYAN='\033[38;5;44m'
BRIGHT_BLUE='\033[38;5;39m'
BRIGHT_MAGENTA='\033[38;5;135m'
BRIGHT_CYAN='\033[38;5;51m'
BRIGHT_GREEN='\033[38;5;46m'
BRIGHT_RED='\033[38;5;196m'
BOLD='\033[1m'
NC='\033[0m'

# =========================================================================
# 全局变量
# =========================================================================
GEMINI_CLI_TERMUX_DIR="$HOME/Gemini-CLI-Termux"
GEMINI_CLI_TERMUX_REPO="https://github.com/print-yuhuan/Gemini-CLI-Termux.git"
FONT_URL="https://github.com/print-yuhuan/Gemini-CLI-Termux/raw/refs/heads/main/MapleMono.ttf"
FONT_DIR="$HOME/.termux"
FONT_PATH="$FONT_DIR/font.ttf"

# =========================================================================
# 通用函数
# =========================================================================

press_any_key() { echo -e "${CYAN}${BOLD}>> 按任意键返回菜单...${NC}"; read -n1 -s; }

check_file_exists() {
    if [ ! -f "$1" ]; then
        echo -e "${BRIGHT_RED}${BOLD}>> 缺少关键文件：$1，请检查仓库完整性。${NC}"
        press_any_key
        exit 1
    fi
}

# =========================================================================
# 字体配置
# =========================================================================
setup_font() {
    echo -e "${CYAN}${BOLD}==== 终端字体配置 ====${NC}"
    mkdir -p "$FONT_DIR"
    if [ -f "$FONT_PATH" ]; then
        echo -e "${YELLOW}${BOLD}>> 字体文件已存在，跳过下载。${NC}"
    else
        if curl -L --progress-bar -o "$FONT_PATH" "$FONT_URL"; then
            echo -e "${BRIGHT_GREEN}${BOLD}>> 字体已下载并保存为 .termux/font.ttf${NC}"
        else
            echo -e "${BRIGHT_RED}${BOLD}>> 字体下载失败，请检查网络或稍后重试。${NC}"
            echo -e "${YELLOW}${BOLD}>> 步骤 4/8 跳过：字体未配置成功。${NC}"
            return
        fi
    fi

    if [ -f "$FONT_PATH" ]; then
        if command -v termux-reload-settings >/dev/null 2>&1; then
            termux-reload-settings \
            && echo -e "${BRIGHT_GREEN}${BOLD}>> 配置已自动刷新，字体已生效。${NC}" \
            || echo -e "${YELLOW}${BOLD}>> 尝试刷新配置失败，请手动重启 Termux。${NC}"
        else
            echo -e "${YELLOW}${BOLD}>> 未检测到 termux-reload-settings，请手动重启 Termux 使字体生效。${NC}"
        fi
        echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 4/8 完成：终端字体已配置。${NC}"
    fi
}

# =========================================================================
# 安装/初始化
# =========================================================================
install_gemini_cli_termux() {
    # 步骤 1/8：环境检测
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 1/8：环境检测 ====${NC}"
    if [ -z "$PREFIX" ] || [[ "$PREFIX" != "/data/data/com.termux/files/usr" ]]; then
        echo -e "${BRIGHT_RED}${BOLD}>> 检测到非 Termux 环境，请在 Termux 中执行此脚本！${NC}"
        exit 1
    fi
    echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 1/8 完成：环境检测通过。${NC}"

    # 步骤 2/8：更新包管理器
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 2/8：更新包管理器 ====${NC}"
    ln -sf /data/data/com.termux/files/usr/etc/termux/mirrors/europe/packages.termux.dev /data/data/com.termux/files/usr/etc/termux/chosen_mirrors
    pkg update && pkg upgrade -y -o Dpkg::Options::="--force-confnew"
    echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 2/8 完成：包管理器已更新。${NC}"

    # 步骤 3/8：安装依赖
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 3/8：安装依赖 ====${NC}"
    for dep in python rustc git; do
        if ! command -v $dep >/dev/null 2>&1; then
            echo -e "${BRIGHT_CYAN}${BOLD}>> 未安装：$dep，正在安装...${NC}"
            if [ "$dep" = "rustc" ]; then
                pkg install -y rust
            else
                pkg install -y $dep
            fi
            if ! command -v $dep >/dev/null 2>&1; then
                echo -e "${BRIGHT_RED}${BOLD}>> $dep 安装失败，请检查网络或手动安装后重试。${NC}"
                exit 1
            fi
            echo -e "${BRIGHT_GREEN}${BOLD}>> $dep 安装成功。${NC}"
        else
            echo -e "${BRIGHT_GREEN}${BOLD}>> $dep 已安装，跳过。${NC}"
        fi
    done
    echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 3/8 完成：依赖已安装。${NC}"

    # 步骤 4/8：配置字体
    setup_font

    # 步骤 5/8：克隆仓库
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 5/8：克隆 Gemini-CLI-Termux 仓库 ====${NC}"
    if [ -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
        echo -e "${YELLOW}${BOLD}>> Gemini-CLI-Termux 仓库已存在，跳过克隆。${NC}"
    else
        rm -rf "$GEMINI_CLI_TERMUX_DIR"
        if git clone "$GEMINI_CLI_TERMUX_REPO" "$GEMINI_CLI_TERMUX_DIR"; then
            echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 5/8 完成：仓库已克隆。${NC}"
        else
            echo -e "${BRIGHT_RED}${BOLD}>> 仓库克隆失败，请检查网络连接。${NC}"
            exit 1
        fi
    fi

    # 步骤 6/8：进入目录并检查文件
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 6/8：检查关键文件 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 进入目录失败！${NC}"; exit 1; }
    check_file_exists "requirements.txt"
    check_file_exists ".env"
    check_file_exists "run.py"
    echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 6/8 完成：关键文件检测通过。${NC}"

    # 步骤 7/8：检查或安装 pip
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 7/8：检查或安装 pip ====${NC}"
    if ! python -m pip --version >/dev/null 2>&1; then
        pkg install -y python-pip
        if ! python -m pip --version >/dev/null 2>&1; then
            echo -e "${BRIGHT_RED}${BOLD}>> pip 安装失败，请检查网络。${NC}"
            exit 1
        fi
    fi
    echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 7/8 完成：pip 已就绪。${NC}"

    # 步骤 8/8：安装 Python 依赖
    echo -e "${BRIGHT_CYAN}${BOLD}==== 步骤 8/8：安装 Python 依赖 ====${NC}"
    if python -m pip install -r requirements.txt; then
        echo -e "${BRIGHT_GREEN}${BOLD}>> 步骤 8/8 完成：依赖已安装。${NC}"
    else
        echo -e "${BRIGHT_RED}${BOLD}>> Python 依赖安装失败！${NC}"
        exit 1
    fi
    echo -e "${BRIGHT_GREEN}${BOLD}==== Gemini-CLI-Termux 安装及初始化完成！=====${NC}"
    press_any_key
}

# =========================================================================
# 启动服务与授权
# =========================================================================

get_env_value() {
    cd "$GEMINI_CLI_TERMUX_DIR" 2>/dev/null || return
    if [ -f ".env" ]; then
        grep "^$1=" .env | head -n1 | cut -d'=' -f2 | xargs
    fi
}

check_port_in_use() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :"$1" | grep LISTEN >/dev/null 2>&1 && return 0 || return 1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -an | grep "LISTEN" | grep ":$1 " >/dev/null 2>&1 && return 0 || return 1
    else
        return 1
    fi
}

start_reverse_proxy() {
    echo -e "${CYAN}${BOLD}==== 启动服务 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists "run.py"
    PORT="$(get_env_value PORT)"
    if [ -n "$PORT" ]; then
        if check_port_in_use "$PORT"; then
            echo -e "${BRIGHT_RED}${BOLD}>> 端口 $PORT 已被占用，请修改端口或释放后重试。${NC}"
            press_any_key
            return
        fi
    fi
    pkill -f "python run.py"
    python run.py
    echo -e "${CYAN}${BOLD}==================${NC}"
}

relogin() {
    echo -e "${CYAN}${BOLD}==== 重新授权 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    rm -f oauth_creds.json
    echo -e "${YELLOW}${BOLD}>> 已清理上次授权，准备重新授权...${NC}"
    start_reverse_proxy
    echo -e "${CYAN}${BOLD}==================${NC}"
}

# =========================================================================
# 反代配置（含局域网配置）
# =========================================================================

change_env_host() {
    echo -e "${CYAN}${BOLD}==== 修改监听地址 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists ".env"
    old=$(grep "^HOST=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${BRIGHT_CYAN}${BOLD}监听地址当前值：${YELLOW}${old}${NC}"
    while true; do
        echo -ne "${BRIGHT_CYAN}${BOLD}请输入新的监听地址（标准IPv4，留空取消）：${NC}"
        read ans
        [ -z "$ans" ] && echo -e "${YELLOW}${BOLD}>> 未修改。${NC}" && press_any_key && echo -e "${CYAN}${BOLD}==================${NC}" && return
        if [[ "$ans" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
            valid=1
            for seg in $(echo $ans | tr '.' ' '); do
                if (( seg < 0 || seg > 255 )); then valid=0; break; fi
            done
            if [ $valid -eq 1 ]; then
                break
            fi
        fi
        echo -e "${BRIGHT_RED}${BOLD}>> 地址格式无效，仅支持标准IPv4数字地址。${NC}"
    done
    sed -i "s/^HOST=.*/HOST=$ans/" .env
    echo -e "${BRIGHT_GREEN}${BOLD}>> 监听地址已更新为：$ans${NC}"
    echo -e "${CYAN}${BOLD}======================${NC}"
    press_any_key
}

change_env_port() {
    echo -e "${CYAN}${BOLD}==== 修改服务端口 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists ".env"
    old=$(grep "^PORT=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    while true; do
        echo -e "${BRIGHT_CYAN}${BOLD}服务端口当前值：${YELLOW}${old}${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请输入新的端口（1-65535，留空取消）：${NC}"
        read ans
        [ -z "$ans" ] && echo -e "${YELLOW}${BOLD}>> 未修改。${NC}" && press_any_key && echo -e "${CYAN}${BOLD}==================${NC}" && return
        if ! [[ "$ans" =~ ^[0-9]+$ ]] || [ "$ans" -lt 1 ] || [ "$ans" -gt 65535 ]; then
            echo -e "${BRIGHT_RED}${BOLD}>> 端口格式无效，请输入 1-65535 的数字。${NC}"
            continue
        fi
        if check_port_in_use "$ans"; then
            echo -e "${BRIGHT_RED}${BOLD}>> 端口 $ans 已被占用，请换一个端口。${NC}"
            continue
        fi
        break
    done
    sed -i "s/^PORT=.*/PORT=$ans/" .env
    echo -e "${BRIGHT_GREEN}${BOLD}>> 服务端口已更新为：$ans${NC}"
    echo -e "${CYAN}${BOLD}======================${NC}"
    press_any_key
}

change_env_keyvalue() {
    echo -e "${CYAN}${BOLD}==== 修改 $2 ====${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists ".env"
    old=$(grep "^$1=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${BRIGHT_CYAN}${BOLD}$2 当前值：${YELLOW}${old}${NC}"
    echo -ne "${BRIGHT_CYAN}${BOLD}请输入新的值（留空取消）：${NC}"; read ans
    if [ -n "$ans" ]; then
        sed -i "s/^$1=.*/$1=$ans/" .env
        echo -e "${BRIGHT_GREEN}${BOLD}>> $2 已更新为：${ans}${NC}"
    else
        echo -e "${YELLOW}${BOLD}>> 未修改。${NC}"
    fi
    echo -e "${CYAN}${BOLD}===============================${NC}"
    press_any_key
}

lan_config_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== 局域网项 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}1. 开启监听${NC}"
        echo -e "${BRIGHT_RED}${BOLD}2. 关闭监听${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}3. 获取地址${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}4. 连接帮助${NC}"
        echo -e "${CYAN}${BOLD}==================${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请选择操作（0-4）：${NC}"
        read -n1 lan_choice; echo
        case "$lan_choice" in
            0) break ;;
            1)
                cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到目录，无法操作。${NC}"; press_any_key; continue; }
                sed -i "s/^HOST=.*/HOST=0.0.0.0/" .env
                echo -e "${BRIGHT_GREEN}${BOLD}>> 已开启监听，允许外部设备访问。${NC}"
                press_any_key
                ;;
            2)
                cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 未找到目录，无法操作。${NC}"; press_any_key; continue; }
                sed -i "s/^HOST=.*/HOST=127.0.0.1/" .env
                echo -e "${BRIGHT_RED}${BOLD}>> 已关闭监听，仅限本机访问。${NC}"
                press_any_key
                ;;
            3)
                ip_found=0
                for i in $(seq 0 5); do
                    ip=$(ifconfig 2>/dev/null | grep -A 1 "wlan$i" | grep "inet " | awk '{print $2}' | head -n1)
                    if [ -n "$ip" ]; then
                        PORT=$(get_env_value PORT)
                        echo -e "请在局域网内其他设备："
                        echo -e "${BRIGHT_GREEN}${BOLD}http://$ip:${PORT:-8888}/${NC}"
                        ip_found=1
                        break
                    fi
                done
                if [ "$ip_found" -eq 0 ]; then
                    echo -e "${YELLOW}${BOLD}未检测到可用的 wlan 接口IP。${NC}"
                    echo -e "${BRIGHT_RED}${BOLD}请确保本机已连接WiFi，并重试。${NC}"
                fi
                press_any_key
                ;;
            4)
                echo -e "${CYAN}${BOLD}==== Gemini-CLI-Termux 局域网连接指南 ====${NC}"
                echo -e "${CYAN}${BOLD}一、准备工作${NC}"
                echo -e "  1. 确保服务已正确安装。"
                echo -e "  2. 本机和其它访问设备需连接同一局域网（如同一个WiFi或热点）。\n"
                echo -e "${CYAN}${BOLD}二、操作建议${NC}"
                echo -e "  1. 开启网络监听"
                echo -e "  2. 获取内网地址"
                echo -e "  3. 启动服务并保持窗口运行"
                echo -e "  4. 其他设备输入上一步获取的网址访问\n"
                echo -e "${CYAN}${BOLD}三、常见问题${NC}"
                echo -e "  · 获取不到内网IP：请确认本机WiFi/热点已连接，可尝试断开重连。"
                echo -e "  · 外部设备无法访问：请确保监听已开启，且两台设备在同一局域网。"
                echo -e "  · 设备重启或网络切换：需重新获取内网IP并用新地址访问。\n"
                echo -e "${CYAN}${BOLD}===========================================${NC}"
                press_any_key
                ;;
            *)
                echo -e "${BRIGHT_RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1
                ;;
        esac
    done
}

reverse_proxy_config_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== 反代配置 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}1. 修改地址${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}2. 修改端口${NC}"
        echo -e "${BRIGHT_MAGENTA}${BOLD}3. 修改项目${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}4. 修改密码${NC}"
        echo -e "${BRIGHT_RED}${BOLD}5. 局域网项${NC}"
        echo -e "${CYAN}${BOLD}==================${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请选择操作（0-5）：${NC}"
        read -n1 rev_choice; echo
        case "$rev_choice" in
            0) break ;;
            1) change_env_host ;;
            2) change_env_port ;;
            3) change_env_keyvalue "GOOGLE_CLOUD_PROJECT" "Google Cloud 项目ID" ;;
            4) change_env_keyvalue "GEMINI_AUTH_PASSWORD" "API 接口访问秘钥" ;;
            5) lan_config_menu ;;
            *) echo -e "${BRIGHT_RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 云端配置
# =========================================================================

cloud_config_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== 云端配置 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}1. 获取 Google Cloud 项目ID${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}2. 管理 Gemini for Google Cloud${NC}"
        echo -e "${BRIGHT_MAGENTA}${BOLD}3. 管理 Gemini Cloud Assist API${NC}"
        echo -e "${CYAN}${BOLD}==================${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请选择操作（0-3）：${NC}"
        read -n1 cloud_choice; echo
        case "$cloud_choice" in
            0) break ;;
            1)
                echo -e "${BRIGHT_GREEN}${BOLD}>> 打开 Google Cloud 控制台...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fwelcome%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                press_any_key
                ;;
            2)
                echo -e "${BRIGHT_BLUE}${BOLD}>> 打开 Gemini for Google Cloud API 管理页...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Flibrary%2Fcloudaicompanion.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                press_any_key
                ;;
            3)
                echo -e "${BRIGHT_MAGENTA}${BOLD}>> 打开 Gemini Cloud Assist API 管理页...${NC}"
                termux-open-url "https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fapis%2Fapi%2Fgeminicloudassist.googleapis.com%3Fhl=zh_CN&service=cloudconsole&flowName=GlifWebSignIn&flowEntry=AccountChooser"
                press_any_key
                ;;
            *)
                echo -e "${BRIGHT_RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 系统维护
# =========================================================================

maintenance_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== 系统维护 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 返回上级${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}1. 更新反代${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}2. 重新部署${NC}"
        echo -e "${BRIGHT_RED}${BOLD}3. 卸载服务${NC}"
        echo -e "${CYAN}${BOLD}==================${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请选择操作（0-3）：${NC}"
        read -n1 main_choice; echo
        case "$main_choice" in
            0) break ;;
            1)
                echo -e "${BRIGHT_GREEN}${BOLD}>> 正在拉取 Gemini-CLI-Termux 最新代码并安装依赖...${NC}"
                cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${BRIGHT_RED}${BOLD}>> 目录不存在。${NC}"; press_any_key; continue; }
                if git status --porcelain | grep -q "^ M .env"; then
                    echo -e "${YELLOW}${BOLD}>> 检测到本地 .env 已修改，自动暂存以防丢失...${NC}"
                    git stash push .env
                    git pull --rebase
                    git stash pop || echo -e "${YELLOW}${BOLD}>> .env 已安全保留。${NC}"
                else
                    git pull --rebase
                fi
                python -m pip install -r requirements.txt \
                    && echo -e "${BRIGHT_GREEN}${BOLD}>> 更新完成。${NC}" \
                    || echo -e "${BRIGHT_RED}${BOLD}>> 更新失败，请检查网络。${NC}"
                press_any_key
                ;;
            2)
                echo -e "${BRIGHT_RED}${BOLD}>> 即将重新部署 Gemini-CLI-Termux，将删除当前目录并重新安装。${NC}"
                echo -ne "${YELLOW}${BOLD}确认继续？（y/N）：${NC}"
                read -n1 confirm; echo
                if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                    cd "$HOME" || exit 1
                    [ -d "$GEMINI_CLI_TERMUX_DIR" ] && rm -rf "$GEMINI_CLI_TERMUX_DIR"
                    install_gemini_cli_termux
                else
                    echo -e "${BRIGHT_CYAN}${BOLD}>> 已取消重新部署。${NC}"
                    press_any_key
                fi
                ;;
            3)
                echo -e "${BRIGHT_RED}${BOLD}>> 即将卸载 Gemini-CLI-Termux，操作不可逆！${NC}"
                echo -ne "${YELLOW}${BOLD}确认继续？（y/N）：${NC}"
                read -n1 confirm; echo
                if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                    [ -d "$GEMINI_CLI_TERMUX_DIR" ] && rm -rf "$GEMINI_CLI_TERMUX_DIR"
                    echo -e "${BRIGHT_GREEN}${BOLD}>> 已卸载 Gemini-CLI-Termux。${NC}"
                    press_any_key
                    exit 0
                else
                    echo -e "${BRIGHT_CYAN}${BOLD}>> 已取消卸载。${NC}"
                    press_any_key
                fi
                ;;
            *) echo -e "${BRIGHT_RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 主菜单
# =========================================================================

main_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== Gemini-CLI-Termux 菜单 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 退出脚本${NC}"
        echo -e "${BRIGHT_GREEN}${BOLD}1. 启动服务${NC}"
        echo -e "${BRIGHT_BLUE}${BOLD}2. 重新授权${NC}"
        echo -e "${BRIGHT_MAGENTA}${BOLD}3. 反代配置${NC}"
        echo -e "${BRIGHT_CYAN}${BOLD}4. 云端配置${NC}"
        echo -e "${BRIGHT_RED}${BOLD}5. 系统维护${NC}"
        echo -e "${CYAN}${BOLD}================================${NC}"
        echo -ne "${BRIGHT_CYAN}${BOLD}请选择操作（0-5）：${NC}"
        read -n1 choice; echo
        case "$choice" in
            0) echo -e "${YELLOW}${BOLD}>> 脚本已退出，欢迎再次使用。${NC}"; sleep 0.5; clear; exit 0 ;;
            1) start_reverse_proxy ;;
            2) relogin ;;
            3) reverse_proxy_config_menu ;;
            4) cloud_config_menu ;;
            5) maintenance_menu ;;
            *) echo -e "${BRIGHT_RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1 ;;
        esac
    done
}

# =========================================================================
# 启动入口
# =========================================================================

if [ ! -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
    echo -e "${YELLOW}${BOLD}>> 未检测到 Gemini-CLI-Termux，自动开始安装...${NC}"
    install_gemini_cli_termux
fi
main_menu
