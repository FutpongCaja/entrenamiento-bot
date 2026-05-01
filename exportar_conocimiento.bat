@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    EXPORTANDO INFO DE ENTRENAMIENTO
echo ==========================================
echo.
echo Esto puede tardar unos minutos...
echo.

set NOTEBOOK_ID=2b5c9fb6-5d6d-4dd8-84d3-01bcd091e048
set OUTPUT_FILE=conocimiento_entrenamiento.txt

echo Creando archivo de conocimiento... > %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

:: Usamos query para obtener un resumen completo de todo el conocimiento
echo Consultando NotebookLM para extraer toda la base tecnica...
C:\Users\herna\.local\bin\nlm.exe query notebook %NOTEBOOK_ID% "Genera un resumen tecnico extremadamente detallado de todo el conocimiento contenido en este cuaderno. Incluye todos los ejercicios, protocolos, tests, logica de fatiga, intensidades y cualquier detalle relevante para un PF. No te guardes nada." > temp_content.txt

if %ERRORLEVEL% EQU 0 (
    type temp_content.txt >> %OUTPUT_FILE%
    del temp_content.txt
    echo.
    echo ==========================================
    echo    EXPORTACION EXITOSA!
    echo ==========================================
    echo Ya podes cerrar esta ventana y avisarme.
) else (
    echo.
    echo Error al exportar. Asegurate de estar logueado con nlm login.
)

pause
