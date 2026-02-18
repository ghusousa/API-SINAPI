#!/usr/bin/env bash
# API SINAPI - Instalação e Inicialização
set -e

echo "============================================================"
echo "  API SINAPI - Instalação e Inicialização"
echo "============================================================"
echo ""

# --- Verificar se Python está instalado ---
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERRO] Python não encontrado!"
    echo ""
    echo "Instale o Python 3.8+:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS:         brew install python3"
    echo ""
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON --version 2>&1)
echo "[OK] $PYTHON_VERSION encontrado"
echo ""

# --- Criar ambiente virtual se não existir ---
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    $PYTHON -m venv .venv
    echo "[OK] Ambiente virtual criado"
else
    echo "[OK] Ambiente virtual já existe"
fi
echo ""

# --- Ativar ambiente virtual ---
source .venv/bin/activate

# --- Instalar dependências ---
echo "Instalando dependências..."
pip install -e . --quiet
echo "[OK] Dependências instaladas"
echo ""

# --- Criar pasta de dados se não existir ---
if [ ! -d "data" ]; then
    mkdir -p data
    echo "[OK] Pasta 'data' criada para arquivos SINAPI"
else
    echo "[OK] Pasta 'data' encontrada"
fi
echo ""

# --- Iniciar servidor ---
echo "============================================================"
echo "  Iniciando API SINAPI..."
echo "============================================================"
echo ""
echo "  Swagger UI:  http://localhost:8000/docs"
echo "  ReDoc:       http://localhost:8000/redoc"
echo ""
echo "  Para carregar dados, faça upload do arquivo SINAPI em:"
echo "  POST http://localhost:8000/upload"
echo ""
echo "  Pressione Ctrl+C para parar o servidor."
echo "============================================================"
echo ""

# --- Abrir navegador com atraso (para o servidor iniciar) ---
(sleep 3 && {
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8000/docs"
    elif command -v open &> /dev/null; then
        open "http://localhost:8000/docs"
    fi
}) &

# --- Definir variável de ambiente para dados ---
export SINAPI_DATA_DIR=data

# --- Iniciar uvicorn ---
$PYTHON -m uvicorn api.app:app --host 0.0.0.0 --port 8000
