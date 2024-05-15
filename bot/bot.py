# python-telegram-bot==13.7
# urllib3==1.26.15
import logging
import re
import os
import paramiko
import os
import psycopg2
import subprocess

from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

user_sql = os.getenv('DB_USER')
pass_sql = os.getenv('DB_PASSWORD')
host_sql = os.getenv('DB_HOST')
port_sql = os.getenv('DB_PORT')
database = os.getenv('DB_DATABASE')


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    update.message.reply_text("Какую команду выполнить?\n"
                                "/find_email\n"
                                "/find_phone_number\n"
                                "/verify_password\n"
                                "/get_release\n"
                                "/get_uname\n"
                                "/get_uptime\n"
                                "/get_df\n"
                                "/get_free\n"
                                "/get_mpstat\n"
                                "/get_w\n"
                                "/get_auths\n"
                                "/get_critical\n"
                                "/get_ps\n"
                                "/get_ss\n"
                                "/get_apt_list\n"
                                "/get_services\n"
                                "/get_repl_logs\n"
                                "/get_emails\n"
                                "/get_phone_numbers\n")


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

AWAITING_PACKAGE = 1
def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    context.user_data['phone_numbers'] = phoneNumberList  # Записываем номера телефонов в user_data
    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер
    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text('Хотите записать номер в БД?')
    return AWAITING_PACKAGE


def savePhoneNumbers(update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        connection = None
        phoneNumbers = context.user_data.get('phone_numbers')
        try:
            connection = psycopg2.connect(user=user_sql,
                                          password=pass_sql,
                                          host=host_sql,
                                          port=port_sql, 
                                          database=database)
            cursor = connection.cursor()
            for phone_number in phoneNumbers: 
                try:
                    cursor.execute("INSERT INTO phone_numbers (phone_number) VALUES (%s) ON CONFLICT DO NOTHING;", (phone_number,))
                    connection.commit()
                except psycopg2.IntegrityError as e:
                    logging.error("Не удалось добавить номер телефона: %s", e)
                
            update.message.reply_text('Операция успешно выполнена')
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            update.message.reply_text('Произошла ошибка при выполнении операции')
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
        return ConversationHandler.END
    else:
        update.message.reply_text('Данные в БД не были записаны')
        return ConversationHandler.END


def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email: ')

    return 'find_email'

def find_email (update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b') # Регулярное выражение для поиска email адресов

    emailsList = emailRegex.findall(user_input)

    if not emailsList: 
        update.message.reply_text('Emails не найдены')
        return ConversationHandler.END
    
    context.user_data['emails'] = emailsList
    emails = '' 
    for i in range(len(emailsList)):
        emails += f'{i+1}. {emailsList[i]}\n'
        
    update.message.reply_text(emails)
    update.message.reply_text('Хотите записать email в БД?')
    return AWAITING_PACKAGE

def saveEmails(update, context):
    user_input = update.message.text
    if user_input.lower() == 'да':
        connection = None
        emails = context.user_data.get('emails')
        try:
            connection = psycopg2.connect(user=user_sql,
                                          password=pass_sql,
                                          host=host_sql,
                                          port=port_sql, 
                                          database=database)
            cursor = connection.cursor()
            for email in emails: 
                try:
                    cursor.execute("INSERT INTO emails (email) VALUES (%s) ON CONFLICT DO NOTHING;", (email,))
                    connection.commit()
                except psycopg2.IntegrityError as e:
                    logging.error("Не удалось добавить email: %s", e)
                
            update.message.reply_text('Операция успешно выполнена')
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            update.message.reply_text('Произошла ошибка при выполнении операции')
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
        return ConversationHandler.END
    else:
        update.message.reply_text('Данные в БД не были записаны')
        return ConversationHandler.END



def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verifyPassword'

def verifyPassword (update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

    password = passwordRegex.search(user_input)

    if password:
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
        
    return ConversationHandler.END # Завершаем работу обработчика диалога



def getRelease(update: Update, context):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('lsb_release -a')
        data = stdout.read().decode()
        client.close()
        update.message.reply_text(data)
        return ConversationHandler.END 
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")
        return ConversationHandler.END

def getUname(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -a; cat /proc/cpuinfo | grep "model name"; cat /etc/hostname; uname -r')
    data = stdout.read().decode()
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getUptime(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getDf(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getFree(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getMpstat(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getW(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('who')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getAuths(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getСritical(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -r -p crit -n 5')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getPs(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getSs(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('netstat -tulpn')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 

def getServices(update: Update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service --state=running')
    data = stdout.read().decode('utf-8')
    client.close()
    update.message.reply_text(data)
    return ConversationHandler.END 


def getReplLogs(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=user_sql,
                                        password=pass_sql,
                                        host=host_sql,
                                        port=port_sql, 
                                        database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT pg_read_file('/var/log/postgresql/postgresql.log')")
        row = cursor.fetchone()
        if row:
            logs = row[0]
            if isinstance(logs, bytes):
                logs = logs.decode('utf-8')
            update.message.reply_text(f'Логи о репликации:\n{logs[-2000:]}')
            logging.info("Команда успешно выполнена")
        else:
            update.message.reply_text("Логи о репликации не найдены")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

def getEmails(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=user_sql,
                                        password=pass_sql,
                                        host=host_sql,
                                        port=port_sql, 
                                        database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()

        emails_list = [f'{row[0]}. {row[1]}' for row in data]
        emails_str = '\n'.join(emails_list)

        update.message.reply_text(f'Emails:\n{emails_str}')
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

def getPhoneNumbers(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=user_sql,
                                        password=pass_sql,
                                        host=host_sql,
                                        port=port_sql, 
                                        database=database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_numbers;")
        data = cursor.fetchall()

        phone_numbers_list = [f'{row[0]}. {row[1]}' for row in data]
        phone_numbers_str = '\n'.join(phone_numbers_list)

        update.message.reply_text(f'Номера телефонов:\n{phone_numbers_str}')
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

def getAptList(update: Update, context):
    update.message.reply_text('Введите "all", чтобы увидеть все установленные пакеты,\n'
                              'или введите название пакета для получения информации о нем:')
    return AWAITING_PACKAGE

def getAptListInput(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'all':
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('dpkg --get-selections | head -n 100') # Тут я поставил ограничение,
        data = stdout.read().decode('utf-8')                                               # так как телеграм не дает больше вывести
        client.close()
        update.message.reply_text(data)
    else:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(f'dpkg -s {user_input}')
        data = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(data)

    return ConversationHandler.END 


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            AWAITING_PACKAGE: [MessageHandler(Filters.text & ~Filters.command, savePhoneNumbers)],
        },
        fallbacks=[]
    )


    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            AWAITING_PACKAGE: [MessageHandler(Filters.text & ~Filters.command, saveEmails)],
        },
        fallbacks=[]
    )

    convHandlerVerify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetRelease = ConversationHandler(
        entry_points=[CommandHandler('get_release', getRelease)],
        states={
            'getRelease': [MessageHandler(Filters.text & ~Filters.command, getRelease)],
        },
        fallbacks=[]
    )

    convHandlerGetUname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', getUname)],
        states={
            'getUname': [MessageHandler(Filters.text & ~Filters.command, getUname)],
        },
        fallbacks=[]
    )

    convHandlerGetUptime = ConversationHandler(
        entry_points=[CommandHandler('get_uptime', getUptime)],
        states={
            'getUptime': [MessageHandler(Filters.text & ~Filters.command, getUptime)],
        },
        fallbacks=[]
    )

    convHandlerGetDf = ConversationHandler(
        entry_points=[CommandHandler('get_df', getDf)],
        states={
            'getDf': [MessageHandler(Filters.text & ~Filters.command, getDf)],
        },
        fallbacks=[]
    )

    convHandlerGetFree = ConversationHandler(
        entry_points=[CommandHandler('get_free', getFree)],
        states={
            'getFree': [MessageHandler(Filters.text & ~Filters.command, getFree)],
        },
        fallbacks=[]
    )

    convHandlerGetMpstat = ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', getMpstat)],
        states={
            'getMpstat': [MessageHandler(Filters.text & ~Filters.command, getMpstat)],
        },
        fallbacks=[]
    )

    convHandlerGetW = ConversationHandler(
        entry_points=[CommandHandler('get_w', getW)],
        states={
            'getW': [MessageHandler(Filters.text & ~Filters.command, getW)],
        },
        fallbacks=[]
    )
	
    convHandlerGetAuths = ConversationHandler(
        entry_points=[CommandHandler('get_auths', getAuths)],
        states={
            'getAuths': [MessageHandler(Filters.text & ~Filters.command, getAuths)],
        },
        fallbacks=[]
    )

    convHandlerGetСritical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', getСritical)],
        states={
            'getСritical': [MessageHandler(Filters.text & ~Filters.command, getСritical)],
        },
        fallbacks=[]
    )

    convHandlerGetPs = ConversationHandler(
        entry_points=[CommandHandler('get_ps', getPs)],
        states={
            'getPs': [MessageHandler(Filters.text & ~Filters.command, getPs)],
        },
        fallbacks=[]
    )

    convHandlerGetSs = ConversationHandler(
        entry_points=[CommandHandler('get_ss', getSs)],
        states={
            'getSs': [MessageHandler(Filters.text & ~Filters.command, getSs)],
        },
        fallbacks=[]
    )

    convHandlerGetServices = ConversationHandler(
        entry_points=[CommandHandler('get_services', getServices)],
        states={
            'getServices': [MessageHandler(Filters.text & ~Filters.command, getServices)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptList)],
        states={
            AWAITING_PACKAGE: [MessageHandler(Filters.text & ~Filters.command, getAptListInput)],
        },
        fallbacks=[]
    )

    convHandlerGetReplLogs = ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', getReplLogs)],
        states={
            'getReplLogs': [MessageHandler(Filters.text & ~Filters.command, getReplLogs)],
        },
        fallbacks=[]
    )

    convHandlerGetEmails = ConversationHandler(
        entry_points=[CommandHandler('get_emails', getEmails)],
        states={
            'getEmails': [MessageHandler(Filters.text & ~Filters.command, getEmails)],
        },
        fallbacks=[]
    )

    convHandlerGetPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', getPhoneNumbers)],
        states={
            'getPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, getPhoneNumbers)],
        },
        fallbacks=[]
    )


	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerify_password)
    dp.add_handler(convHandlerGetRelease)
    dp.add_handler(convHandlerGetUname)
    dp.add_handler(convHandlerGetUptime)
    dp.add_handler(convHandlerGetDf)
    dp.add_handler(convHandlerGetFree)
    dp.add_handler(convHandlerGetMpstat)
    dp.add_handler(convHandlerGetW)
    dp.add_handler(convHandlerGetAuths)
    dp.add_handler(convHandlerGetСritical)
    dp.add_handler(convHandlerGetPs)
    dp.add_handler(convHandlerGetSs)
    dp.add_handler(convHandlerGetServices)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(convHandlerGetReplLogs)
    dp.add_handler(convHandlerGetEmails)
    dp.add_handler(convHandlerGetPhoneNumbers)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
