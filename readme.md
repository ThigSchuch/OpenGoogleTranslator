# OpenGoogleTranslate
Aqui você conseguirá rodar seu próprio bot tradutor usando o [Telegram](https://telegram.org) e o [Python](https://python.org), fazendo uso de duas bibliotecas, a [GoogleTrans](https://py-googletrans.readthedocs.io/en/latest/) e o [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/en/stable/), além de salvar apenas o necessário usando [SQLite3](https://sqlite.org/index.html).

Um projeto simples de final de semana, venha comigo!
Quer conferir? [@OpenGoogleTranslatorBot](https://t.me/OpenGoogleTranslatorBot)
## Requirements
    googletrans==2.4.0
    python-telegram-bot==12.7

Clone o repositório e então execute `pip install -r requirements.txt`

*SQLite3 vem com o Python 3, se você ainda usa o 2, atualize 😅

## Criando o BD
Abra o terminal Python e execute:

    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
	    CREATE TABLE users (
	    userID INTEGER NOT NULL PRIMARY KEY,
	    native TEXT,
	    destination TEXT);
    """)
    conn.close()

Se tudo ocorreu bem, você verá um arquivo chamado **users.db** na raíz do projeto.
Você consegue visualizar as informações com o SQLite Manager, mas não é este o foco.

## Rodando o bot

Na função **main** você encontrará uma linha dizendo `INSIRA SEU TOKEN AQUI`, bem, faça o que ela manda e tudo ficará bem.

Agora é só rodar o arquivo **`main.py`**

# Contribua!