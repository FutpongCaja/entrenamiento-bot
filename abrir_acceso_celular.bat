@echo off
echo Abriendo puerto 8000 en el Firewall para el Celular...
powershell -Command "New-NetFirewallRule -DisplayName 'Chatbot PF' -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow"
echo.
echo LISTO! Ya deberias poder entrar desde tu celular a http://192.168.1.64:8000
pause
