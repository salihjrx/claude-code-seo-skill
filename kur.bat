@echo off
chcp 65001 >nul
setlocal
echo ==============================================
echo   SEO paketi kurulumu (Claude Code)
echo ==============================================
echo.
set /p HEDEF=Sitenizin ana klasor yolunu yapistirin ve Enter'a basin: 
set HEDEF=%HEDEF:"=%
if not exist "%HEDEF%\" (
  echo HATA: Klasor bulunamadi: %HEDEF%
  pause
  exit /b 1
)
set KAYNAK=%~dp0

echo.
echo Skill kopyalaniyor: %HEDEF%\.claude\skills\seo
mkdir "%HEDEF%\.claude\skills\seo" 2>nul
xcopy "%KAYNAK%seo-skill\*" "%HEDEF%\.claude\skills\seo\" /E /I /Y >nul

if exist "%HEDEF%\CLAUDE.md" (
  echo Mevcut CLAUDE.md bulundu: yedek aliniyor ve SEO bolumu sona ekleniyor.
  copy /Y "%HEDEF%\CLAUDE.md" "%HEDEF%\CLAUDE.md.yedek" >nul
  echo.>>"%HEDEF%\CLAUDE.md"
  type "%KAYNAK%CLAUDE.md">>"%HEDEF%\CLAUDE.md"
) else (
  copy /Y "%KAYNAK%CLAUDE.md" "%HEDEF%\CLAUDE.md" >nul
)

echo.
set /p GENEL=Skill'i tum projelerinizde de kullanmak ister misiniz? (E/H): 
if /I "%GENEL%"=="E" (
  mkdir "%USERPROFILE%\.claude\skills\seo" 2>nul
  xcopy "%KAYNAK%seo-skill\*" "%USERPROFILE%\.claude\skills\seo\" /E /I /Y >nul
  echo Kisisel skill kuruldu: %USERPROFILE%\.claude\skills\seo
)

echo.
echo TAMAM. Simdi site klasorunde terminal acip "claude" yazin, sonra:
echo     Siteyi incele ve SEO'yu uygula
echo.
pause
