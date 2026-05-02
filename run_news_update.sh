#!/usr/bin/env bash
# Instala dependências (se necessário) e executa a atualização de notícias.
#
# Uso:
#   ./run_news_update.sh            # execução única
#   ./run_news_update.sh --schedule 30  # loop a cada 30 minutos
#
# Cron (exemplo — executa a cada hora):
#   0 * * * * /caminho/para/run_news_update.sh >> /var/log/uol_news.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cria e ativa virtualenv se ainda não existir
if [ ! -d ".venv" ]; then
    echo "[setup] Criando ambiente virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Instala/atualiza dependências
pip install --quiet -r requirements.txt

# Repassa todos os argumentos para o script Python
python uol_politics_news.py "$@"
