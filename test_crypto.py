from core.crypto import generate_salt, derive_key, encrypt_data, decrypt_data

def run_tests():
    print("--- Testování kryptografického jádra ---")
    
    # Simulace vstupů od uživatele
    master_password = "MojeSuperTajneHeslo123"
    tajna_poznamka = "Tajny login: admin, heslo: 12345"
    
    # 1. Příprava klíče
    print("\n[KROK 1] Odvození klíče")
    salt = generate_salt()
    print(f"Vygenerovaná sůl (16 bajtů HEX): {salt.hex()}")
    
    # Zde program chvilku počká, protože Argon2id úmyslně pálí procesorový čas
    key = derive_key(master_password, salt)
    print(f"Odvozený AES klíč (32 bajtů HEX): {key.hex()}")
    
    # 2. Šifrování
    print("\n[KROK 2] Šifrování poznámky")
    print(f"Původní text: {tajna_poznamka}")
    encrypted = encrypt_data(key, tajna_poznamka)
    print(f"Zašifrovaná data (Nonce + Ciphertext HEX): {encrypted.hex()}")
    
    # 3. Dešifrování
    print("\n[KROK 3] Dešifrování poznámky")
    decrypted = decrypt_data(key, encrypted)
    print(f"Dešifrovaný text: {decrypted}")
    
    # Jednoduchý test funkčnosti (podobné assertům v C++)
    if tajna_poznamka == decrypted:
        print("-> ÚSPĚCH: Texty se shodují!")
    else:
        print("-> CHYBA: Texty se neshodují!")
        
    # 4. Test integrity (pokus o úpravu dat)
    print("\n[KROK 4] Test GCM ochrany proti modifikaci")
    # Převedeme bytes na bytearray, abychom mohli data měnit (bytes jsou v Pythonu immutable/neměnné)
    tampered_data = bytearray(encrypted)
    # Změníme poslední bit pomocí XOR operace
    tampered_data[-1] ^= 0x01  
    
    try:
        print("Pokouším se dešifrovat poškozená data...")
        decrypt_data(key, bytes(tampered_data))
        print("-> KRITICKÁ CHYBA: GCM neochránil modifikovaná data!")
    except ValueError as e:
        # Zde zachytáváme tvůj vyhozený ValueError s výjimkou InvalidTag z crypto.py
        print(f"-> ÚSPĚCH: Zásah do dat byl odhalen. Vyhozena chyba: {e}")

if __name__ == "__main__":
    run_tests()