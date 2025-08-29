@echo off
title Gerenciador - BOT

:start

cls

echo.
echo ===================================================================
echo             GERENCIADOR DE BOT - v1.0
echo ===================================================================
echo.
echo  o INICIANDO O BOT...
echo.
echo  i Logs serao exibidos aqui e tambem salvos no arquivo 'bot.log'.
echo.
echo  ! Para reiniciar o bot por completo (util para quando mexer no
echo    bot.py), pressione Ctrl+C nesta janela e depois 'S'.
echo.
echo  ! Para recarregar funcionalidades (Cogs) sem desligar o bot,
echo    use o comando /reload diretamente no Discord.
echo.
echo ===================================================================
echo.

python bot.py

echo.
echo ===================================================================
echo  x O PROCESSO DO BOT FOI ENCERRADO.
echo  o Reiniciando automaticamente em 5 segundos...
echo ===================================================================

timeout /t 5 /nobreak >nul

goto start