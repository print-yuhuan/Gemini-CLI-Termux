#!/data/data/com.termux/files/usr/bin/bash

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
MAGENTA='\033[1;35m'
CYAN='\033[1;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

GEMINI_CLI_TERMUX_DIR="$HOME/Gemini-CLI-Termux"
GEMINI_CLI_TERMUX_REPO="https://github.com/print-yuhuan/Gemini-CLI-Termux.git"

press_any_key() { echo -e "${CYAN}${BOLD}>> 按任意键返回菜单...${NC}"; read -n1 -s; }

check_file_exists() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}${BOLD}>> 缺少关键文件：$1，请检查仓库完整性。${NC}"
        press_any_key
        exit 1
    fi
}

install_gemini_cli_termux() {
    echo -e "\n${CYAN}${BOLD}==== [自动安装 Gemini-CLI-Termux] ====${NC}"
    echo -e "${CYAN}${BOLD}>> 检查执行环境...${NC}"
    if [ -z "$PREFIX" ] || [[ "$PREFIX" != "/data/data/com.termux/files/usr" ]]; then
        echo -e "${RED}${BOLD}>> 检测到非 Termux 环境，请在 Termux 中执行此脚本！${NC}"
        exit 1
    fi

    echo -e "${CYAN}${BOLD}>> 同步 Termux 镜像设置并更新系统...${NC}"
    ln -sf /data/data/com.termux/files/usr/etc/termux/mirrors/europe/packages.termux.dev /data/data/com.termux/files/usr/etc/termux/chosen_mirrors
    if ! pkg update && pkg upgrade -y -o Dpkg::Options::="--force-confnew"; then
        echo -e "${RED}${BOLD}>> 系统更新失败，请检查网络连接。${NC}"
        exit 1
    fi

    for dep in python rustc git; do
        if ! command -v $dep >/dev/null 2>&1; then
            echo -e "${YELLOW}${BOLD}>> 未安装：$dep，正在安装...${NC}"
            if [ "$dep" = "rustc" ]; then
                pkg install -y rust
            else
                pkg install -y $dep
            fi
            if ! command -v $dep >/dev/null 2>&1; then
                echo -e "${RED}${BOLD}>> $dep 安装失败，请检查网络或手动安装后重试。${NC}"
                exit 1
            fi
            echo -e "${GREEN}${BOLD}>> $dep 安装成功。${NC}"
        else
            echo -e "${CYAN}${BOLD}>> $dep 已安装，跳过。${NC}"
        fi
    done

    if [ -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
        echo -e "${YELLOW}${BOLD}>> 检测到 Gemini-CLI-Termux 仓库已存在，跳过克隆。${NC}"
    else
        echo -e "${CYAN}${BOLD}>> 克隆 Gemini-CLI-Termux 仓库...${NC}"
        rm -rf "$GEMINI_CLI_TERMUX_DIR"
        if ! git clone "$GEMINI_CLI_TERMUX_REPO" "$GEMINI_CLI_TERMUX_DIR"; then
            echo -e "${RED}${BOLD}>> 仓库克隆失败，请检查网络连接。${NC}"
            exit 1
        fi
    fi

    echo -e "${CYAN}${BOLD}>> 进入 Gemini-CLI-Termux 目录...${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${RED}${BOLD}>> 进入目录失败！${NC}"; exit 1; }

    check_file_exists "requirements.txt"
    check_file_exists ".env"
    check_file_exists "run.py"

    echo -e "${CYAN}${BOLD}>> 检查或安装 pip ...${NC}"
    if ! python -m pip --version >/dev/null 2>&1; then
        pkg install -y python-pip
        if ! python -m pip --version >/dev/null 2>&1; then
            echo -e "${RED}${BOLD}>> pip 安装失败，请检查网络。${NC}"
            exit 1
        fi
    fi

    echo -e "${CYAN}${BOLD}>> 安装 Python 依赖...${NC}"
    if ! python -m pip install -r requirements.txt; then
        echo -e "${RED}${BOLD}>> Python 依赖安装失败！${NC}"
        exit 1
    fi

    echo -e "${GREEN}${BOLD}>> Gemini-CLI-Termux 安装及初始化完成！${NC}\n"
    press_any_key
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

get_env_port() {
    cd "$GEMINI_CLI_TERMUX_DIR" 2>/dev/null || return
    if [ -f ".env" ]; then
        grep "^PORT=" .env | head -n1 | cut -d'=' -f2 | xargs
    fi
}

start_reverse_proxy() {
    echo -e "${CYAN}${BOLD}>> 尝试启动 Gemini-CLI-Termux 服务...${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists "run.py"
    PORT="$(get_env_port)"
    if [ -n "$PORT" ]; then
        if check_port_in_use "$PORT"; then
            echo -e "${RED}${BOLD}>> 端口 $PORT 已被占用，请修改端口或释放后重试。${NC}"
            press_any_key
            return
        fi
    fi
    python run.py
}

relogin() {
    echo -e "${CYAN}${BOLD}>> 开始重新授权流程...${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    rm -f oauth_creds.json
    echo -e "${YELLOW}${BOLD}>> 已清理上次授权，准备重新授权...${NC}"
    start_reverse_proxy
}

change_env_keyvalue() {
    echo -e "${CYAN}${BOLD}>> 修改配置项 $1 ...${NC}"
    cd "$GEMINI_CLI_TERMUX_DIR" || { echo -e "${RED}${BOLD}>> 未找到 Gemini-CLI-Termux 目录。${NC}"; press_any_key; return; }
    check_file_exists ".env"
    old=$(grep "^$1=" .env | head -n1 | cut -d'=' -f2- | cut -d'#' -f1 | xargs)
    echo -e "${CYAN}${BOLD}$2 当前值：${YELLOW}${old}${NC}"
    echo -ne "${CYAN}${BOLD}请输入新的值（留空取消）：${NC}"; read ans
    if [ -n "$ans" ]; then
        sed -i "s/^$1=.*/$1=$ans/" .env
        echo -e "${GREEN}${BOLD}>> $2 已更新为：${ans}${NC}"
    else
        echo -e "${YELLOW}${BOLD}>> 未修改。${NC}"
    fi
    press_any_key
}

main_menu() {
    while true; do
        clear
        echo -e "${CYAN}${BOLD}==== Gemini-CLI-Termux 菜单 ====${NC}"
        echo -e "${YELLOW}${BOLD}0. 退出脚本${NC}"
        echo -e "${GREEN}${BOLD}1. 启动服务${NC}"
        echo -e "${BLUE}${BOLD}2. 重新授权${NC}"
        echo -e "${MAGENTA}${BOLD}3. 修改密码${NC}"
        echo -e "${CYAN}${BOLD}4. 修改项目${NC}"
        echo -e "${WHITE}${BOLD}5. 修改端口${NC}"
        echo -e "${RED}${BOLD}6. 重新安装${NC}"
        echo -e "${CYAN}${BOLD}==================================${NC}"
        echo -ne "${CYAN}${BOLD}请选择操作（0-6）：${NC}"
        read -n1 choice; echo
        case "$choice" in
            0) echo -e "${YELLOW}${BOLD}>> 脚本已退出。${NC}"; sleep 0.5; clear; exit 0 ;;
            1) start_reverse_proxy ;;
            2) relogin ;;
            3) change_env_keyvalue "GEMINI_AUTH_PASSWORD" "API 接口访问密码" ;;
            4) change_env_keyvalue "GOOGLE_CLOUD_PROJECT" "Google Cloud 项目ID" ;;
            5) change_env_keyvalue "PORT" "服务端口（如 8888）" ;;
            6)
                echo -e "${RED}${BOLD}>> 即将重新安装 Gemini-CLI-Termux，将删除当前目录并重新部署。${NC}"
                echo -ne "${YELLOW}${BOLD}确认继续？（y/N）：${NC}"
                read -n1 confirm; echo
                if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                    cd "$HOME" || exit 1
                    if [ -d "$GEMINI_CLI_TERMUX_DIR" ]; then
                        rm -rf "$GEMINI_CLI_TERMUX_DIR"
                    fi
                    install_gemini_cli_termux
                else
                    echo -e "${CYAN}${BOLD}>> 已取消重新安装。${NC}"
                    press_any_key
                fi
                ;;
            *) echo -e "${RED}${BOLD}>> 无效选项，请重新输入。${NC}"; sleep 1 ;;
        esac
    done
}

if [ ! -d "$GEMINI_CLI_TERMUX_DIR/.git" ]; then
    echo -e "${YELLOW}${BOLD}未检测到 Gemini-CLI-Termux，自动开始安装...${NC}"
    install_gemini_cli_termux
fi
main_menu
