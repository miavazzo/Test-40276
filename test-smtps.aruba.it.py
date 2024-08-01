import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from termcolor import colored
import os
from dotenv import load_dotenv

# Carica le variabili di ambiente dal file .env
load_dotenv()

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('587')
username = os.getenv('USERNAMES')
password = os.getenv('PASSWORDY')

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
    

# Funzione per inviare email
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
        # Connessione al server SMTP
        server = CustomSMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Abilita il debug per vedere tutte le interazioni
        server.ehlo()  # Invia il comando EHLO con il dominio specificato
        server.starttls()  # Abilita TLS
        server.ehlo()  # Invia nuovamente EHLO dopo aver iniziato TLS
        server.login(username, password)  # Autenticazione

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
