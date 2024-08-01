import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from termcolor import colored
import msal
from msal import ConfidentialClientApplication
from colorama import init, Fore, Style
import os
from dotenv import load_dotenv

# Inizializza colorama
init()

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Configurazione OAuth2
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
tenant_id = os.getenv('TENANT_ID')
authority = f'https://login.microsoftonline.com/{tenant_id}'
scopes = ['https://graph.microsoft.com/.default']
username = os.getenv('USERNAME')

# Dati di accesso e configurazione SMTP
smtp_server = os.getenv('smtp_server')
smtp_port = os.getenv('smtp_port')

# Dati dei mittenti
senders = {
    'Argon': username
}

class CustomSMTP(smtplib.SMTP):
    def send(self, s):
        print(colored(f"SENT: {s}", 'blue'))
        super().send(s)

    def getreply(self):
        code, msg = super().getreply()
        print(colored(f"RECEIVED: {msg}", 'red'))
        return code, msg

def get_oauth2_token():
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=scopes)
    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception("Could not acquire token")

def send_email(sender_name, recipient, subject, body):
    sender_email = senders[sender_name]

    # Crea il messaggio MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Aggiungi il corpo dell'email
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Ottieni il token OAuth2
        access_token = get_oauth2_token()
        auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
        auth_string_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Connessione al server SMTP
        server = CustomSMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Abilita il debug per vedere tutte le interazioni
        server.ehlo()  # Invia il comando EHLO con il dominio specificato
        server.starttls()  # Abilita TLS
        server.ehlo()  # Invia nuovamente EHLO dopo aver iniziato TLS

        # Autenticazione con il token OAuth2
        code, response = server.docmd('AUTH XOAUTH2', auth_string_base64)
        if code != 235:
            raise Exception(f"Autenticazione fallita: {response}")

        # Invia l'email
        server.sendmail(sender_email, recipient, msg.as_string())
        print(f"Email inviata con successo da {sender_email} a {recipient}")

    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")

    finally:
        server.quit()

# Esempio di utilizzo
if __name__ == "__main__":
    recipient_email = os.getenv('recipientem')
    subject = 'Test Email'
    body = 'Questo è un messaggio di test.'

    # Invia email da ciascun mittente
    for sender_name in senders:
        send_email(sender_name, recipient_email, subject, body)
