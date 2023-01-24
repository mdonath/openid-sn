import imaplib
import email
from time import sleep

IMAP_URL = 'imap.gmail.com'
ACCOUNT_SUPPORT_EMAIL = 'account@support.scouting.nl'
MARKER = '"text-align: center; font-size: 2em;">'
MAX_RETRIES = 10

def get_emails_from(user, password, sender, label='Inbox'):
    """
    Haalt alle mails van sender op uit de mailbox van user.
    """
    imap = imaplib.IMAP4_SSL(IMAP_URL)

    (status, result) = imap.login(user, password)
    if (status != 'OK'):
        print(f'ERROR: Status: {status}, result: {result}')
        return []

    (status, message_count) = imap.select(label)
    if (status != 'OK'):
        print(f'ERROR: Status: {status}, #messages: {message_count}')
        return []

    tries_left = MAX_RETRIES
    msgnums2 = []
    while tries_left > 0:
        (status, data) = imap.recent()
        if (status != 'OK'):
            print(f'recent-ERROR: Status: {status}, data: {data}')
            return []

        (status, msgnums) = imap.search(None, 'FROM', f'"{sender}"', '(UNSEEN)')
        if (status != 'OK'):
            print(f'SEARCH-ERROR: Status: {status}, msgnums: {msgnums}')
            return []

        if msgnums != [b'']:
            msgnums2 = msgnums
            tries_left = 0
        else:
            sleep(5)
            print('>', end=' ', flush=True)
            tries_left = tries_left - 1

    msgs = []
    if msgnums != [b'']:
        for num in msgnums2[0].split():
            (status, msg) = imap.fetch(num, '(RFC822)')
            if (status != 'OK'):
                print(f'FETCH-ERROR: Status: {status}, msg: {msg}')

            for response in msg:
                if isinstance(response, tuple):
                    message = email.message_from_bytes(response[1])
                    msgs.append((num, message))
            (status, data) = imap.store(num, '+FLAGS', '\\Seen')
            if (status != 'OK'):
                print(f'STORE-ERROR: Status: {status}, msgnums: {msgnums}')

    (status, data) = imap.close()
    if (status != 'OK'):
        print(f'ERROR: Status: {status}, data: {data}')
        return []

    (status, data) = imap.logout()
    if (status != 'BYE'):
        print(f'ERROR: Status: {status}, data: {data}')
        return []

    return msgs


def find_code(message):
    """
    Zoekt de eenmalige code in de mail en geeft deze terug.
    """
    try:
        # verwijder alle encoded enters zodat het zoeken naar de marker makkelijker kan
        data = message.as_string().replace("=\n", '')
        
        # Zoek de marker en daarmee het begin van de code
        pos = data.find(MARKER) + len(MARKER)

        # De code is altijd lengte 6
        return data[pos : pos + 6]
        
    except UnicodeEncodeError as e:
        pass


def extract_codes(messages):
    """
    Doorzoekt alle gevonden mails en geef daarvan de code terug.
    """
    codes = []
    if len(messages) > 0:
        for num, message in messages:
            codes.append(find_code(message))
            
    return codes


def get_mfa_token_from_mailbox(user: str, password: str, label: str) -> str:
    """
    Haalt het laatst ontvangen MFA-token op uit een mailbox.
    """
    msgs = get_emails_from(user, password, ACCOUNT_SUPPORT_EMAIL, label)
    return extract_codes(msgs)[-1]
