import requests
import base64
import os
from msal import ConfidentialClientApplication
from colorama import init, Fore, Style
import os
from dotenv import load_dotenv

# Inizializza colorama
init()

load_dotenv()

# Configurazione OAuth2
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
tenant_id = os.getenv('TENANT_ID')
authority = f'https://login.microsoftonline.com/{tenant_id}'
scopes = ['https://graph.microsoft.com/.default']
username = os.getenv('USERNAME')

def print_request(method, url, headers, data=None):
    print(f"{Fore.BLUE}>>> Richiesta {method} a {url}")
    print(f">>> Headers:")
    for key, value in headers.items():
        if key.lower() == 'authorization':
            print(f">>>   {key}: Bearer [TOKEN NASCOSTO]")
        else:
            print(f">>>   {key}: {value}")
    if data:
        print(f">>> Body: [CONTENUTO OMESSO PER BREVITÀ]")
    print(Style.RESET_ALL)

def print_response(response):
    print(f"{Fore.RED}<<< Risposta dal server:")
    print(f"<<< Codice di stato: {response.status_code}")
    print(f"<<< Headers:")
    for key, value in response.headers.items():
        print(f"<<<   {key}: {value}")
    print(f"<<< Body: [CONTENUTO OMESSO PER BREVITÀ]")
    print(Style.RESET_ALL)

def get_access_token():
    app = ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    result = app.acquire_token_silent(scopes, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" in result:
        print(f"{Fore.GREEN}Token ottenuto con successo{Style.RESET_ALL}")
        return result['access_token']
    else:
        print(f"{Fore.RED}Errore nell'ottenimento del token:")
        print(f"  {result.get('error')}")
        print(f"  {result.get('error_description')}{Style.RESET_ALL}")
        return None

def send_email_with_attachment(subject, body, to_email, attachment_path):
    access_token = get_access_token()
    if not access_token:
        print("Impossibile ottenere il token di accesso.")
        return

    endpoint = 'https://graph.microsoft.com/v1.0/users/' + username + '/sendMail'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    # Leggi il file PDF e codificalo in base64
    with open(attachment_path, 'rb') as file:
        attachment_content = base64.b64encode(file.read()).decode('utf-8')

    # Ottieni il nome del file dall'path
    attachment_name = os.path.basename(attachment_path)

    email_msg = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': to_email
                    }
                }
            ],
            'attachments': [
                {
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': attachment_name,
                    'contentType': 'application/pdf',
                    'contentBytes': attachment_content
                }
            ]
        },
        'saveToSentItems': 'true'
    }

    print_request('POST', endpoint, headers, email_msg)
    response = requests.post(endpoint, headers=headers, json=email_msg)
    print_response(response)
    
    if response.status_code == 202:
        print(f'{Fore.GREEN}Email inviata con successo con allegato PDF!{Style.RESET_ALL}')
    else:
        print(f'{Fore.RED}Errore nell\'invio dell\'email. Codice di stato: {response.status_code}{Style.RESET_ALL}')

if __name__ == "__main__":
    subject = "Test Email con OAuth2, Graph API e allegato PDF"
    body = "Questo è un test di invio email usando Python, OAuth2 e Microsoft Graph API con un allegato PDF."
    to_email = os.getenv('recipientem')
    attachment_path = r"C:\Users\miavazzo\OneDrive - Capgemini\Documents\T. 40276 parametri email portale clienti - fatture Newatt\Crypto101.pdf"
    send_email_with_attachment(subject, body, to_email, attachment_path)