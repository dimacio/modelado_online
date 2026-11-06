@echo off
rem Levanta un servidor web local sobre esta carpeta y abre la pagina en el navegador.
rem Para cortarlo, cerra esta ventana o apreta Ctrl+C.
cd /d "%~dp0"
set PY=python
where python >nul 2>nul
if errorlevel 1 set PY=py
echo.
echo   Sirviendo esta carpeta en http://localhost:8000/
echo   Para cortar: Ctrl+C
echo.
start "" http://localhost:8000/
%PY% -m http.server 8000
