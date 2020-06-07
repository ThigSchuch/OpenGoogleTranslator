import logging
import sqlite3
from googletrans import Translator
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Realiza alterções das linguagens no BD
def updateDB(userID, lang, option):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if option == "toLang": # Parâmetro passado toLang
        cursor.execute("""UPDATE users SET toLang = ? WHERE userID = ? """,(lang, int(userID)))
    else: # Se não, é o reverseLang
        cursor.execute("""UPDATE users SET reverseLang = ? WHERE userID = ? """,(lang, int(userID)))

    conn.commit()
    conn.close()

# Coleta os dados que o bot tem do usuário
def getUserInfo(userID):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE userID = "+str(userID))
    dados = str(cursor.fetchall()).replace("'","").replace(" ","").split('(')[1].split(')')[0].split(',')
    conn.close()
    return dados

# Ao iniciar o chat, guarda as informações com o padrão PT-EN
def keepID(userID):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO users (userID, toLang, reverseLang) VALUES (?,?,?)""",(int(userID), "pt", "en"))
        conn.commit()
    except: # Para caso aperte /start novamente
        pass
    conn.close()

# Comando Start, salva os dados e dá boas vindas
def start(update, context):
    keepID(update.effective_user.id)
    person = update.effective_user.first_name
    update.message.reply_text(
                            "Olá "+person+", tudo bem? Vou te ajudar a traduzir as coisas! "+
                            "\n\nPrimeiro, vamos arrumar a casa, digite /setLang e a sigla para definir "+
                            "seu idioma padrão."+
                            "\n\nExemplo: /setLang pt")

# Comando para definir o idioma nativo
def setLang(update, context):
    try:
        lang = update.message.text.split(" ")[1].lower() # Se o comando foi certo, o idioma é este
        updateDB(update.effective_user.id, lang, "toLang")
        update.message.reply_text('Certo! Seu idioma nativo é '+lang+'.\n\nAgora defina o inverso, vou usar ela quando você digitar em seu Idioma Nativo.\n\nExemplo: /setReverse en')
    except:
        update.message.reply_text('Você deve digitar /setLang + idioma.')

# Comando para definir o idioma reverso
def setReverse(update, context):
    try: 
        lang = update.message.text.split(" ")[1].lower() # Se o comando foi certo, o idioma é este
        updateDB(update.effective_user.id, lang, "reverseLang")
        update.message.reply_text('Certo! Seu idioma backup é '+lang+'\nAgora você já pode mandar qualquer texto para mim.')
    except:
        update.message.reply_text('Você deve digitar /setReverse + idioma.')

# Verifica o idioma nativo da pessoa
# Usado para fazer a tradução "reversa"
def checkLang(userID):
    return getUserInfo(userID)[1]

# Qualquer texto enviado será traduzido
def translate(update, context):
    userData = getUserInfo(update.effective_user.id)

    translator = Translator()
    lang = translator.detect(update.message.text) # Detecta o idioma da mensagem

    if lang.lang != userData[1]: # De qualquer idioma para o nativo
        msg = translator.translate(update.message.text, dest=userData[1]).text
        
    else: # Do nativo para o reverse
        msg = translator.translate(update.message.text, dest=userData[2]).text
    
    update.message.reply_text(msg)

# Usando filtro, ele traduzirá mensagens que possuem legenda
def filterCaption(update, context):
    userData = getUserInfo(update.effective_user.id)

    translator = Translator()
    lang = translator.detect(update.message.caption) # Detecta o idioma da mensagem

    if lang.lang != userData[1]: # De qualquer idioma para o nativo
        msg = translator.translate(update.message.caption, dest=userData[1]).text
        
    else: # Do nativo para o reverse
        msg = translator.translate(update.message.caption, dest=userData[2]).text

    update.message.reply_text(msg)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(token='INSIRA SEU TOKEN AQUI', use_context=True)
    dp = updater.dispatcher

    # Comandos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setLang", setLang))
    dp.add_handler(CommandHandler("setReverse", setReverse))
    dp.add_handler(MessageHandler(Filters.text, translate))
    dp.add_handler(MessageHandler(Filters.caption, filterCaption))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()