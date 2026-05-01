@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    ACTUALIZANDO CEREBRO DEL CHATBOT
echo ==========================================
echo.
echo Extrayendo texto de tus archivos de Entrenamiento...
echo (Esto puede tardar dependiendo de la cantidad de archivos)
echo.

set OUTPUT_FILE=conocimiento_entrenamiento.txt
echo BASE DE CONOCIMIENTO PF HERNAN ALVAREZ > %OUTPUT_FILE%
echo FECHA: %DATE% %TIME% >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

powershell -Command "$files = Get-ChildItem -Path Entrenamiento -Recurse -Include *.txt, *.docx; foreach ($file in $files) { Write-Host 'Procesando: ' $file.Name; Add-Content %OUTPUT_FILE% \"`n--- ARCHIVO: $($file.FullName) ---`n\"; if ($file.Extension -eq '.docx') { try { $word = New-Object -ComObject Word.Application; $doc = $word.Documents.Open($file.FullName, $false, $true); Add-Content %OUTPUT_FILE% $doc.Content.Text; $doc.Close(); $word.Quit(); } catch { Write-Host 'Error en Word: ' $_.Exception.Message } } else { Add-Content %OUTPUT_FILE% (Get-Content $file.FullName -Raw) } }"

echo.
echo ==========================================
echo    CEREBRO ACTUALIZADO CON EXITO!
echo ==========================================
echo El archivo 'conocimiento_entrenamiento.txt' ha sido generado.
echo.
pause
