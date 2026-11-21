#!/бин/баш
SCRIPT_DIR="$(компактный диск "$(dirname "${BASH_SOURCE[0]}")" && пароль)"
CURRENT_DIR="$(пару)"
if [ -f "$CURRENT_DIR/gitlab-mcp.env" ]; then
    echo "Загрузка переменных среды из $CURRENT_DIR/gitlab-mcp.env"
    set -a
    source "$CURRENT_DIR/gitlab-mcp.env"
    set +a
else
    echo "В $CURRENT_DIR не найден gitlab-mcp.env с использованием существующих переменных среды."
fi
source "$SCRIPT_DIR/.venv/bin/активировать"
python "$SCRIPT_DIR/main.py" 2>&1 | tee /tmp/gitlab-mcp-server.log