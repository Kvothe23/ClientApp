This is an application that contains a branch "Vulnerable" that is vulnerable to XSS reflected, stored and Dom-based, SQL injections and Sensitive Information disclosure.
The branch "Secure" has been mitigated agains these vulnerabilities.

Python 3.12.8
SQLite

Libraries that are needed to run the project:
pip install flask bleach

Configure de database:
python create_database.py

Run:
python app.py
