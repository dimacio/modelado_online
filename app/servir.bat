@echo off
rem Levanta la aplicacion con las cabeceras que habilitan el docking.
rem Para cortarlo, cerra esta ventana o apreta Ctrl+C.
cd /d "%~dp0"
set PY=python
where python >nul 2>nul
if errorlevel 1 set PY=py
start "" http://localhost:8000/
%PY% servidor.py 8000
