@echo off
chcp 65001 >nul 2>&1
title API SINAPI

echo ============================================================
echo   API SINAPI - Instalacao e Inicializacao
echo ============================================================
echo.

REM --- Verificar se Python esta instalado ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale o Python 3.8+ em: https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado
echo.

REM --- Criar ambiente virtual se nao existir ---
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado
) else (
    echo [OK] Ambiente virtual ja existe
)
echo.

REM --- Ativar ambiente virtual ---
call .venv\Scripts\activate.bat

REM --- Instalar dependencias ---
echo Instalando dependencias...
pip install -e . --quiet
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM --- Criar pasta de dados se nao existir ---
if not exist "data" (
    mkdir data
    echo [OK] Pasta "data" criada para arquivos SINAPI
) else (
    echo [OK] Pasta "data" encontrada
)
echo.

REM --- Iniciar servidor ---
echo ============================================================
echo   Iniciando API SINAPI...
echo ============================================================
echo.
echo   Swagger UI:  http://localhost:8000/docs
echo   ReDoc:       http://localhost:8000/redoc
echo.
echo   Para carregar dados, faca upload do arquivo SINAPI em:
echo   POST http://localhost:8000/upload
echo.
echo   Pressione Ctrl+C para parar o servidor.
echo ============================================================
echo.

REM --- Abrir navegador no Swagger (com atraso para o servidor iniciar) ---
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8000/docs"

REM --- Definir variavel de ambiente para dados ---
set SINAPI_DATA_DIR=data

REM --- Iniciar uvicorn ---
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000

pause
