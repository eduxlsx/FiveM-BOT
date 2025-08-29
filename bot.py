import discord
import os
import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

log_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler = logging.handlers.RotatingFileHandler(
    filename='bot.log',
    encoding='utf-8',
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

TOKEN = ""

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot conectado como {bot.user}')
    logger.info('Carregando Cogs...')
    logger.info('------')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'Cog {filename} carregado com sucesso.')
        except Exception as e:
            logger.error(f'Erro ao carregar o Cog {filename}: {e}', exc_info=True)

logger.info("Iniciando a conexão com o Discord...")
bot.run(TOKEN)