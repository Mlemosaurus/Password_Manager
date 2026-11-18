from storage.database import DatabaseManager
import os

def run_tests():
    print("Testování databáze")

    if os.path.exists("test_vault.db"):
        os.remove("test_vault.db")

    db = DatabaseManager("test_vault.db")

     #Otestuje vytvoření trezoru
    if db.is_vault_initialized() == True:  
        print("Vytvořil se trezor, i když ještě neměl")

    db.create_vault("NereknuHeslo123")

    if db.is_vault_initialized() == False:
            print("Nevytvořil se trezor, i když měl")

     #Testování přístupu do zamčeného trezoru
    db_locked = DatabaseManager("test_vault.db")

    if db_locked.unlock_vault("ReknuHeslo123") == True:
         print("Trezor odemčen i přes špatné heslo")

    try:
        data = db_locked.get_all_entries()
    except RuntimeError as e:
         print(f"Nešlo vytáhnout data ze zamčeného trezoru: {e}")

    if db_locked.unlock_vault("NereknuHeslo123") == True:
         print("Trezor odemčen")

     #Testování CRUD operací
    db_locked.add_entry("Google","mujemai.@seznam.cz","GoogleHeslo2","vedlejsi ucet")
    db_locked.add_entry("Outlook","skolnimail@email.com","SkolaniOutlook3")

    zaznamy = db_locked.get_all_entries()

    for zaznam in zaznamy:
         print(zaznam)

    zaznam1 = zaznamy[0]
    id1 = zaznam1["id"]

    zaznam2 = db_locked.get_entry_by_id(id1)

    if zaznam1 == zaznam2:
         print("Zazamy jsou stejné")
    else:
         print("Zaznamy se liší")

    db_locked.update_entry(id1,"Google","mujemail@seznam.cz","HesloGoogle2","hlavni ucet")
    zaznam1_novy = db_locked.get_entry_by_id(id1)

    if zaznam1 != zaznam1_novy:
         print("Úspěšně změnen záznam")
    else:
         print("Zaznam se nezměnil")

    db_locked.delete_entry(id1)

    zaznamy = db_locked.get_all_entries()

    if len(zaznamy) == 1:
         print("Zaznam se smazal")
    else:
         print("Záznam se nesmazal")

    os.remove("test_vault.db")
    


if __name__ == ("__main__"):

     run_tests()

