# Password_Manager
Vývoj desktopové aplikace pro správu přihlašovacích údajů s lokálním uchováváním dat.

Cílem projektu je vývoj desktopové aplikace pro bezpečnou správu přihlašovacích údajů s lokálním uchováváním dat. K zabezpečení databáze využívá moderní kryptografické standardy, konkrétně algoritmus Argon2 pro derivaci klíče z hlavního hesla (které se nikam neukládá) a šifrování AES-256 v režimu GCM pro ochranu samotných záznamů proti přečtení i neoprávněné manipulaci. Aplikace uživatelům poskytne standardní správu hesel (CRUD operace), integrovaný generátor silných hesel a dodatečné bezpečnostní mechanismy, jako je automatické promazávání systémové schránky po zkopírování hesla a časový zámek trezoru při neaktivitě.
