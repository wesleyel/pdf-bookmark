@echo off

REM PDF Bookmark Tool Launcher Script

set SCRIPT_DIR=%~dp0
set LIB_DIR=%SCRIPT_DIR%lib

REM Check if Java is available
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Java is not installed or not in PATH
    echo Please install Java 17 or later to run this application
    exit /b 1
)

REM Build classpath
set CLASSPATH=
for %%i in ("%LIB_DIR%\*.jar") do (
    if defined CLASSPATH (
        set CLASSPATH=!CLASSPATH!;%%i
    ) else (
        set CLASSPATH=%%i
    )
)

REM Enable delayed variable expansion for the loop above
setlocal enabledelayedexpansion

REM Rebuild classpath with delayed expansion
set CLASSPATH=
for %%i in ("%LIB_DIR%\*.jar") do (
    if defined CLASSPATH (
        set CLASSPATH=!CLASSPATH!;%%i
    ) else (
        set CLASSPATH=%%i
    )
)

REM Run the application
java -cp "!CLASSPATH!" com.ifnoelse.pdf.gui.Main %*