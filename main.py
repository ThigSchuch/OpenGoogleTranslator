import logging
import sqlite3
from googletrans import Translator
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

languages = {
    'af':'Afrikaans','sq':'Albanian','am':'Amharic','ar':'Arabic','hy':'Armenian','az':'Azerbaijani',
    'eu':'Basque','be':'Belarusian','bn':'Bengali','bs':'Bosnian','bg':'Bulgarian','ca':'Catalan',
    'ceb':'Cebuano','ny':'Chichewa','zh-cn':'Chinese(simplified)','zh-tw':'Chinese(traditional)',
    'co':'Corsican','hr':'Croatian','cs':'Czech','da':'Danish','nl':'Dutch','en':'English','eo':'Esperanto',
    'et':'Estonian','tl':'Filipino','fi':'Finnish','fr':'French','fy':'Frisian','gl':'Galician','ka':'Georgian',
    'de':'German','el':'Greek','gu':'Gujarati','ht':'Haitiancreole','ha':'Hausa','haw':'Hawaiian','iw':'Hebrew',
    'hi':'Hindi','hmn':'Hmong','hu':'Hungarian','is':'Icelandic','ig':'Igbo','id':'Indonesian','ga':'Irish',
    'it':'Italian','ja':'Japanese','jw':'Javanese','kn':'Kannada','kk':'Kazakh','km':'Khmer','ko':'Korean',
    'ku':'Kurdish(kurmanji)','ky':'Kyrgyz','lo':'Lao','la':'Latin','lv':'Latvian','lt':'Lithuanian',
    'lb':'Luxembourgish','mk':'Macedonian','mg':'Malagasy','ms':'Malay','ml':'Malayalam','mt':'Maltese',
    'mi':'Maori','mr':'Marathi','mn':'Mongolian','my':'Myanmar(burmese)','ne':'Nepali','no':'Norwegian',
    'ps':'Pashto','fa':'Persian','pl':'Polish','pt':'Portuguese','pa':'Punjabi','ro':'Romanian','ru':'Russian',
    'sm':'Samoan','gd':'Scotsgaelic','sr':'Serbian','st':'Sesotho','sn':'Shona','sd':'Sindhi','si':'Sinhala',
    'sk':'Slovak','sl':'Slovenian','so':'Somali','es':'Spanish','su':'Sundanese','sw':'Swahili','sv':'Swedish',
    'tg':'Tajik','ta':'Tamil','te':'Telugu','th':'Thai','tr':'Turkish','uk':'Ukrainian','ur':'Urdu','uz':'Uzbek',
    'vi':'Vietnamese','cy':'Welsh','xh':'Xhosa','yi':'Yiddish','yo':'Yoruba','zu':'Zulu'
    }

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

# Verifica o idioma escolhido existe
def checkLang(lang):
    try:
        languages[lang]
    except:
        return False
    return True

# Comando Start, salva os dados e dá boas vindas
def start(update, context):
    keepID(update.effective_user.id)
    person = update.effective_user.first_name
    update.message.reply_text(
                            f"""Olá {person}, tudo bem? Vou te ajudar a traduzir as coisas!
                            \nPrimeiro, vamos arrumar a casa, digite /setLang e a sigla para definir
                            seu idioma padrão.
                            \nExemplo: /setLang pt""")

# Comando para definir o idioma nativo
def setLang(update, context):
    try:
        lang = update.message.text.split(" ")[1].lower() # Se o comando foi certo, o idioma é este
        if checkLang(lang):
            updateDB(update.effective_user.id, lang, "toLang")
            update.message.reply_text(f"""Certo! Seu idioma nativo é "{lang}".
                                        \nAgora defina o inverso, vou usar ela quando você digitar em seu Idioma Nativo.
                                        \nExemplo: /setReverse en""")
        else:
            update.message.reply_text(f'Não encontrei essa língua "{lang}", você deve digitar a sigla.\nNão sabe qual? Clique aqui /langs')
    except:
        update.message.reply_text('Você deve digitar /setLang + idioma.')

# Comando para definir o idioma reverso
def setReverse(update, context):
    try: 
        lang = update.message.text.split(" ")[1].lower() # Se o comando foi certo, o idioma é este
        if checkLang(lang):
            updateDB(update.effective_user.id, lang, "reverseLang")
            update.message.reply_text(f"""Certo! Seu idioma backup é "{lang}".
                                        \nAgora você já pode mandar qualquer texto para mim.""")
        else:
            update.message.reply_text(f'Não encontrei essa língua "{lang}", você deve digitar a sigla.\nNão sabe qual? Clique aqui /langs')
    except:
        update.message.reply_text('Você deve digitar /setReverse + idioma.')
    
# Qualquer texto enviado será traduzido
def translate(update, context):
    userData = getUserInfo(update.effective_user.id)
    
    if update.message.text != None: # Se for texto normal
        text = update.message.text
    else:
        text = update.message.caption # Se for algo com legenda

    translator = Translator()
    lang = translator.detect(text).lang # Detecta o idioma da mensagem

    if lang != userData[1]: # De qualquer idioma para o nativo
        msg = f'{languages[lang]} detectado\n\n{translator.translate(text, dest=userData[1]).text}'
        
    else: # Do nativo para o reverse
        msg = f'{languages[userData[2]]}\n\n{translator.translate(text, dest=userData[2]).text}'
    
    update.message.reply_text(msg)

# Langs
def langs(update, context):
    msg = "Eu consigo entender todos esses idiomas aqui:\n\n"

    for key, value in languages.items():
        msg += f'| {key} - {value}\n'

    update.message.reply_text(msg)

# User info
def myInfo(update, context):
    userData = getUserInfo(update.effective_user.id)

    msg = f"Tudo o que tenho de você é isto:\n\nSeu ID: {userData[0]}\nSua língua nativa: {userData[1]}\nE sua língua reversa: {userData[2]}"
    
    update.message.reply_text(msg)

# Help
def helpCommand(update, context):
    msg = """Olá, tudo bem? Precisa de uma mãozinha?
    
/setLang - Defina seu Idioma Nativo
/setReverse - Usarei para traduzir quando você digitar em sua língua nativa\n
/langs - Veja os idiomas em que consigo traduzir
/myInfo - Quem é você? Só sei seus idiomas e ID
/help - É esta mensagem aqui
        
Ajude no meu desenvolvimento!\nhttps://github.com/ThigSchuch/OpenGoogleTranslator"""
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
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("langs", langs))
    dp.add_handler(CommandHandler("myInfo", myInfo))
    dp.add_handler(MessageHandler(Filters.text, translate))
    dp.add_handler(MessageHandler(Filters.caption, translate))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()