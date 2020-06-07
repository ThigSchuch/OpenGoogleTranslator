# -*- coding: UTF-8 -*-
import logging, re, sqlite3
from googletrans import Translator
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

languages = {
    'AF':'Afrikaans','SQ':'Albanian','AM':'Amharic','AR':'Arabic','HY':'Armenian','AZ':'Azerbaijani',
    'EU':'Basque','BE':'Belarusian','BN':'Bengali','BS':'Bosnian','BG':'Bulgarian','CA':'Catalan',
    'CEB':'Cebuano','NY':'Chichewa','ZH-CN':'Chinese(simplified)','ZH-TW':'Chinese(traditional)',
    'CO':'Corsican','HR':'Croatian','CS':'Czech','DA':'Danish','NL':'Dutch','EN':'English','EO':'Esperanto',
    'ET':'Estonian','TL':'Filipino','FI':'Finnish','FR':'French','FY':'Frisian','GL':'Galician','KA':'Georgian',
    'DE':'German','EL':'Greek','GU':'Gujarati','HT':'Haitiancreole','HA':'Hausa','HAW':'Hawaiian','IW':'Hebrew',
    'HI':'Hindi','HMN':'Hmong','HU':'Hungarian','IS':'Icelandic','IG':'Igbo','ID':'Indonesian','GA':'Irish',
    'IT':'Italian','JA':'Japanese','JW':'Javanese','KN':'Kannada','KK':'Kazakh','KM':'Khmer','KO':'Korean',
    'KU':'Kurdish(kurmanji)','KY':'Kyrgyz','LO':'Lao','LA':'Latin','LV':'Latvian','LT':'Lithuanian',
    'LB':'Luxembourgish','MK':'Macedonian','MG':'Malagasy','MS':'Malay','ML':'Malayalam','MT':'Maltese',
    'MI':'Maori','MR':'Marathi','MN':'Mongolian','MY':'Myanmar(burmese)','NE':'Nepali','NO':'Norwegian',
    'PS':'Pashto','FA':'Persian','PL':'Polish','PT':'Portuguese','PA':'Punjabi','RO':'Romanian','RU':'Russian',
    'SM':'Samoan','GD':'Scotsgaelic','SR':'Serbian','ST':'Sesotho','SN':'Shona','SD':'Sindhi','SI':'Sinhala',
    'SK':'Slovak','SL':'Slovenian','SO':'Somali','ES':'Spanish','SU':'Sundanese','SW':'Swahili','SV':'Swedish',
    'TG':'Tajik','TA':'Tamil','TE':'Telugu','TH':'Thai','TR':'Turkish','UK':'Ukrainian','UR':'Urdu','UZ':'Uzbek',
    'VI':'Vietnamese','CY':'Welsh','XH':'Xhosa','YI':'Yiddish','YO':'Yoruba','ZU':'Zulu'
    }

# Remove os emojis :)
def deEmojify(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"
                           u"\U0001F300-\U0001F5FF"
                           u"\U0001F680-\U0001F6FF"
                           u"\U0001F1E0-\U0001F1FF"
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

# Realiza alterções das linguagens no BD
def updateDB(userID, lang, option):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if option == "native":
        cursor.execute("""UPDATE users SET native = ? WHERE userID = ? """,(lang, int(userID)))
    else:
        cursor.execute("""UPDATE users SET destination = ? WHERE userID = ? """,(lang, int(userID)))

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
        cursor.execute("""INSERT INTO users (userID, native, destination) VALUES (?,?,?)""",(int(userID), "PT", "EN"))
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
    update.message.reply_markdown(
                            f"""Olá {person}, tudo bem? Vou te ajudar a traduzir as coisas!
                            \nPrimeiro, vamos arrumar a casa, digite `/setLang` e a sigla para definir seu idioma nativo.
                            \nExemplo: `/setLang pt`""")

# Comando para definir o idioma nativo
def setLang(update, context):
    try:
        lang = update.message.text.split(" ")[1].upper() # Se o comando foi certo, o idioma é este
        if checkLang(lang):
            updateDB(update.effective_user.id, lang, "native")
            update.message.reply_markdown(f"""Certo! Seu idioma nativo é *{lang}*.
                                        \nAgora defina o destino, vou usar ele quando você digitar em seu Idioma Nativo.
                                        \nExemplo: `/toLang en`""")
        else:
            update.message.reply_markdown(f'Não encontrei esse idioma *{lang}*, você deve digitar a sigla.\nNão sabe qual? Clique aqui /langs')
    except:
        update.message.reply_markdown('Você deve digitar `/setLang + sigla do idioma.`')

# Comando para definir o idioma destino
def toLang(update, context):
    try: 
        lang = update.message.text.split(" ")[1].upper() # Se o comando foi certo, o idioma é este
        if checkLang(lang):
            updateDB(update.effective_user.id, lang, "destination")
            update.message.reply_markdown(f"""Certo! Seu idioma destino é *{lang}*.
                                        \nAgora você já pode mandar qualquer texto para mim.""")
        else:
            update.message.reply_markdown(f'Não encontrei esse idioma *{lang}*, você deve digitar a sigla.\nNão sabe qual? Clique aqui /langs')
    except:
        update.message.reply_markdown('Você deve digitar `/toLang + sigla do idioma`.')
    
# Qualquer texto enviado será traduzido
def translate(update, context):
    userData = getUserInfo(update.effective_user.id)
    
    if update.message.text != None: # Se for texto normal
        text = deEmojify(update.message.text)
    else:
        text = deEmojify(update.message.caption) # Se for algo com legenda

    translator = Translator()
    lang = translator.detect(text).lang.upper() # Detecta o idioma da mensagem

    if lang != userData[1]: # De qualquer idioma para o nativo
        msg = f'{languages[lang]} ➡️ {languages[userData[1]]}\n\n`{translator.translate(text, dest=userData[1]).text}`'
        
    else: # Do nativo para o reverse
        msg = f'{languages[userData[1]]} ➡️ {languages[userData[2]]}\n\n`{translator.translate(text, dest=userData[2]).text}`'
    
    update.message.reply_markdown(msg)

# Langs
def langs(update, context):
    msg = "Eu consigo entender todos esses idiomas aqui:\n\n"

    for key, value in languages.items():
        msg += f'| {key} - {value}\n'

    update.message.reply_text(msg)

# User info
def myInfo(update, context):
    userData = getUserInfo(update.effective_user.id)

    msg = f"Tudo o que tenho de você é isto:\n\nSeu ID: `{userData[0]}`\nSeu idioma nativo: *{userData[1]}*\nSeu idioma destino: *{userData[2]}*"
    
    update.message.reply_markdown(msg)

# Help
def helpCommand(update, context):
    msg = """Olá, tudo bem? Precisa de uma mãozinha?
    
`/setLang` - Defina seu Idioma Nativo
`/toLang` - Usarei para traduzir quando você digitar em seu Idioma Nativo\n
`/langs` - Veja os idiomas em que consigo traduzir
`/myInfo` - Quem é você? Só sei seus idiomas e ID
`/help` - É esta mensagem aqui
        
[Ajude no meu desenvolvimento!](https://github.com/ThigSchuch/OpenGoogleTranslator)"""
    update.message.reply_markdown(msg)
    
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(token='INSIRA SEU TOKEN AQUI', use_context=True)
    dp = updater.dispatcher

    # Comandos
    dp.add_handler(CommandHandler("start", start)) # Start
    dp.add_handler(CommandHandler("setLang", setLang)) # Definir nativo
    dp.add_handler(CommandHandler("toLang", toLang)) # Definir destino
    dp.add_handler(CommandHandler("help", helpCommand)) # Ajuda
    dp.add_handler(CommandHandler("langs", langs)) # Línguas suportadas
    dp.add_handler(CommandHandler("myInfo", myInfo)) # Informações do usuário
    dp.add_handler(MessageHandler(Filters.text, translate)) # Filtro apenas texto
    dp.add_handler(MessageHandler(Filters.caption, translate)) # Filtro legendas

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
