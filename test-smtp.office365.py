import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from termcolor import colored
from dotenv import load_dotenv
import os

# Carica le variabili di ambiente dal file .env
load_dotenv('C:\\Users\\miavazzo\\OneDrive - Capgemini\\Documents\\T. 40276 parametri email portale clienti - fatture Newatt\\.env')

# Dati di accesso e configurazione
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
username = os.getenv('USERNAMEZ') # fatture@energylifegate
password = os.getenv('PASSWORD') # fatture@energylifegate

# Aggiungi anche questo per verificare se ci sono variabili già presenti nel sistema
print("Valori caricati dal .env:")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"USERNAMEZ: {os.getenv('USERNAMEZ')}")
print(f"PASSWORD: {os.getenv('PASSWORD')}")
print(f"Recipient Email: {os.getenv('recipientem')}")

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
    
'''    def ehlo(self, name='energylifegate.it'):
        """ SMTP 'EHLO' command """
        self.putcmd("ehlo", name)
        (code, msg) = self.getreply()
        if code != 250:
            raise smtplib.SMTPHeloError(code, msg)
        return (code, msg)'''

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
