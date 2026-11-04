import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

def generate_salt()->bytes:
    return os.urandom(16) #vrátí náhodné 16-byte (128bit) číslo

def derive_key(password:str, salt: bytes)->bytes:

    kdf = Argon2id( #nastavení funkce pro derivaci klíče
        salt=salt,
        length = 32,
        iterations=1,
        lanes=4,
        memory_cost = 2**21, #2Gb
        ad=None,
        secret=None,
    )

    #derivace klice
    password_bin:bytes = password.encode('utf-8') #převedení do bytů
    key = kdf.derive(password_bin) #derivuje heslo do 256bitového klíče

    """
    #overeni
    kdf = Argon2id(
            salt=salt,
            length = 32,
            iterations=1,
            lanes=4,
            memory_cost = 2**21, #2Gb
            ad=None,
            secret=None,
        )
    kdf.verify(password_bin,key)
    """
    return key

def encrypt_data(key:bytes, plaintext:str)->bytes:
    aesgcm = AESGCM(key)  #příprava šifrovače
    nonce = os.urandom(12) #inicializační vektor, potřebuju i při dešifrování (Number used ONCE)
    data = plaintext.encode('utf-8') #převedení hesla do bytů
    encrypted = aesgcm.encrypt(nonce,data,associated_data=None) #samotné zašifrování
    return nonce + encrypted 

def decrypt_data(key:bytes, encrypted_data:bytes)->str:
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12] #slicing data na nonce a samotná data
    data = encrypted_data[12:]

    try:
        decrypted = aesgcm.decrypt(nonce,data,associated_data=None) #dešifrování
        plaintext = decrypted.decode('utf-8') #převedení do stringu
        return plaintext
    except InvalidTag:
        raise ValueError("Dešifrování selhalo, špatné heslo nebo poškozená data")