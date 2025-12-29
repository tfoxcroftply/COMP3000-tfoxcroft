set "DIR=%cd%"
ECHO %DIR%

cd ..\React
call npx vite build

cd /d "%DIR%"
npm start
