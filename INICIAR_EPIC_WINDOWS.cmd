@echo off
setlocal
cd /d "%~dp0"
echo =======================================
echo Wasteland NX - Fallout New Vegas (Epic)
echo =======================================
echo Diagnostico local, sem modificar o jogo ou os saves.
where py >nul 2>&1
if not errorlevel 1 (
  py -3 tools\fnv_preflight.py --epic --report newvegas-relatorio.json %*
  goto finished
)
where python >nul 2>&1
if not errorlevel 1 (
  python tools\fnv_preflight.py --epic --report newvegas-relatorio.json %*
  goto finished
)
echo ERRO: Python 3 nao encontrado.
goto end
:finished
if errorlevel 1 (
  echo ERRO: Jogo nao encontrado ou instalacao incompleta.
  echo Execute INICIAR_EPIC_WINDOWS.cmd --data "D:\Epic Games\FalloutNewVegas"
) else (
  echo Arquivo newvegas-relatorio.json gerado.
)
:end
pause
