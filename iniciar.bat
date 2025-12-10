@echo off
REM Script para iniciar o Smart Heaven v2 com autenticação
REM Execute este arquivo quando o banco de dados estiver online

echo ================================
echo Smart Heaven v2 - Inicializacao
echo ================================
echo.

echo [1/4] Verificando conexao com banco de dados...
ping -n 1 192.168.31.153 >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Banco de dados em 192.168.31.153 nao esta acessivel!
    echo Por favor, verifique a conexao e tente novamente.
    pause
    exit /b 1
)
echo [OK] Banco de dados acessivel!
echo.

echo [2/4] Criando tabela de usuarios (se necessario)...
cd backend
alembic upgrade head
if errorlevel 1 (
    echo [AVISO] Erro ao criar tabela. Pode ja existir.
)
echo.

echo [3/4] Iniciando backend...
start "Smart Heaven Backend" cmd /k "python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo [OK] Backend iniciado na porta 8000
echo.

timeout /t 3 >nul

echo [4/4] Iniciando frontend...
cd ..\frontend
start "Smart Heaven Frontend" cmd /k "npm run dev"
echo [OK] Frontend iniciado na porta 5173
echo.

echo ================================
echo Sistema iniciado com sucesso!
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Para criar seu primeiro usuario:
echo 1. Acesse http://localhost:5173
echo 2. Clique em "Cadastre-se"
echo 3. Preencha os dados e crie sua conta
echo.
echo Pressione qualquer tecla para sair...
pause >nul
