import sqlite3
from contextlib import contextmanager
from core.crypto import generate_salt, derive_key, encrypt_data, decrypt_data


class DatabaseManager:

    def __init__(self, db_path: str = "vault.db"):
        self.db_path = db_path
        self.key: bytes | None = None
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    

    def _init_db(self) ->None:   #vytvoří tabulky

        with self._connect() as conn:
            cursor = conn.cursor()

            create_vault_query = """
                CREATE TABLE IF NOT EXISTS vault_meta (
                    id INTEGER PRIMARY KEY,
                    salt BLOB NOT NULL,
                    verification_token BLOB NOT NULL
                );
            """

            create_entries_query = """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password BLOB NOT NULL,
                    notes BLOB
                );
            """

            cursor.execute(create_vault_query)
            cursor.execute(create_entries_query)
            conn.commit()

    def is_vault_initialized(self)->bool: #Ověřuje, jestli je trezor existuje
        with self._connect() as conn:
            cursor = conn.cursor()

            select_query = "SELECT id FROM vault_meta LIMIT 1"
            cursor.execute(select_query)
            return cursor.fetchone() is not None

    def create_vault(self, master_password:str)->None: #První nastavení hesla
        with self._connect() as conn:
            cursor = conn.cursor()

            salt = generate_salt()
            key = derive_key(master_password,salt)
            control = encrypt_data(key, "VALID_VAULT")

            insert_query = """
                INSERT INTO vault_meta(salt, verification_token)
                VALUES(?,?);
                """
            data = (salt, control)
            cursor.execute(insert_query,data)
            conn.commit()
            self.key = key

    def unlock_vault(self, master_password:str)->bool: #Přihlášení do trezoru
        with self._connect() as conn:
            cursor = conn.cursor()

            select_query = "SELECT salt, verification_token FROM vault_meta LIMIT 1"
            cursor.execute(select_query)
            data = cursor.fetchone()
            if data is None:
                return False

            key = derive_key(master_password,data[0])

            try:
                control = decrypt_data(key,data[1])
                if control == "VALID_VAULT":
                    self.key = key
                    return True
            except ValueError:
                return False

    #Následují CRUD operace

    def add_entry(self, service:str, username:str, password:str, notes:str="")->None: #Create
        if self.key is None:
            raise RuntimeError("Trezor je zamčený! Nelze pracovat s daty")
        with self._connect() as conn:
            cursor = conn.cursor()

            password_enc = encrypt_data(self.key, password)
            notes_enc = encrypt_data(self.key, notes)

            insert_query = """
                INSERT INTO entries (service, username, password, notes)
                VALUES (?,?,?,?);
                """
            data = (service, username, password_enc, notes_enc)
            cursor.execute(insert_query,data)
            conn.commit()

    def get_all_entries(self) -> list[dict]: #Read (všechny zápisy)
        if self.key is None:
            raise RuntimeError("Trezor je zamčený! Nelze pracovat s daty")
        with self._connect() as conn:
            cursor = conn.cursor()

            select_query = "SELECT id, service, username, password, notes FROM entries ORDER BY service ASC"
            cursor.execute(select_query)
            data_enc = cursor.fetchall()
            data = []
            for entry in data_enc:
                password_dec = decrypt_data(self.key,entry[3])
                notes_dec = decrypt_data(self.key,entry[4])
                temp = {"id":entry[0],
                        "service": entry[1],
                        "username":entry[2],
                        "password":password_dec,
                        "notes":notes_dec 
                        }
                data.append(temp)
            return data

    def get_entry_by_id(self, entry_id:int)->dict | None: #Read (jeden zápis na základě id)
        if self.key is None:
            raise RuntimeError("Trezor je zamčený! Nelze pracovat s daty")
        with self._connect() as conn:
            cursor = conn.cursor()

            select_query = "SELECT service, username, password, notes FROM entries WHERE id = ?"

            cursor.execute(select_query,(entry_id,))
            data_enc = cursor.fetchone()
            if data_enc is None:
                return None
            
            password_dec = decrypt_data(self.key,data_enc[2])
            notes_dec = decrypt_data(self.key,data_enc[3])
            data = {"id":entry_id,
                    "service": data_enc[0],
                    "username":data_enc[1],
                    "password":password_dec,
                    "notes":notes_dec 
                    }
            return data
            
    def update_entry(self, entry_id:int, service:str, username:str, password:str, notes:str="")->None: #Update (updatne zápis)
        if self.key is None:
            raise RuntimeError("Trezor je zamčený! Nelze pracovat s daty")

        password_enc = encrypt_data(self.key, password)
        notes_enc = encrypt_data(self.key, notes)

        with self._connect() as conn:
            cursor = conn.cursor()

            update_query = "UPDATE entries SET service = ?, username = ?, password = ?, notes = ? WHERE id = ?"
            cursor.execute(update_query,(service, username, password_enc, notes_enc, entry_id))
            conn.commit()

    def delete_entry(self, entry_id:int)->None:  #Delete (odstraní zápis)
        if self.key is None:
            raise RuntimeError("Trezor je zamčený! Nelze pracovat s daty")
        with self._connect() as conn:
            cursor = conn.cursor()

            delete_query = "DELETE FROM entries WHERE id = ?"
            cursor.execute(delete_query,(entry_id,))
            conn.commit()
