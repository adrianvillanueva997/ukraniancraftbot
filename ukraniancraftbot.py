import requests
import telegram.chataction
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

api = r''


def get_public_ip():
	#Function that scrapes the website "miip.es" and returns your public IP
    url = r'https://miip.es/'
    re = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0)'})
    html = re.content
    soup = BeautifulSoup(html, 'html.parser')
    div_block = soup.find('div', {'class': '8u'})
    ip = None
    for div in div_block:
        soup2 = BeautifulSoup(str(div), 'html.parser')
        ip_code = soup2.find('h2')
        if ip_code is not None:
            ip = ip_code

    ip = str(ip).replace('<h2>', '')
    ip = ip.replace('</h2>', '')
    ip = ip.replace('Tu IP es ', '')
    print(ip)
    return ip


def minecraft_status(ip):
	#Function that returns a dictionary with all the data related with a minecraft server given your public IP, the default port is 25565
	#In case your port is not that one, just change it
    re = requests.get(url=f'https://mcapi.us/server/status?', params={
        'ip': ip,
        'port': '25565'
    }, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0)'})
    json_data = re.json()
    status = json_data['status']
    online = json_data['online']
    motd = json_data['motd']
    players = json_data['players']
    server = json_data['server']
    server_data = {
        'status': status,
        'online': online,
        'motd': motd,
        'players': players,
        'server': server,

    }
    return server_data


def start(bot, update):
    update.message.reply_text('Pues estoy funcionando')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def print_ip(bot, update):
	# public bot command interface
    try:
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        ip = get_public_ip()
        server_data = minecraft_status(ip)
        message = f"ip: {ip}:25565" \
            f"\nStatus: {server_data['status']} " \
            f"\nOnline: {server_data['online']}" \
            f"\nPlayers: {server_data['players']}" \
            f"\nVersion: {server_data['server']}" \
            f"\nMotd: {server_data['motd']}"
        bot.send_message(chat_id=update.message.chat_id,
                         text=str(message))
    except Exception as e:
        logger.warning('Update "%s" caused error "%s"' % (update, error))
        bot.send_message(chat_id=update.message.chat_id,
                         text=str(e))


if __name__ == '__main__':
    updater = Updater(api, workers=1)
    dp = updater.dispatcher
    start_handler = CommandHandler('start', start)

    dp.add_handler(start_handler)
    dp.add_handler(CommandHandler('get_ip', print_ip))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
