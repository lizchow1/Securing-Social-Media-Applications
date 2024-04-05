# Securing-Social-Media-Applications
Advanced Computer Networks Assignment 2

python3 -m venv venv
source venv/bin/activate
pip install Flask
pip install Flask-SQLAlchemy
pip install cryptography


cd instance
rm userdatabase.db


For Report
1. set up flask, user database, making registration and login routes
2. choose Cryptographic library
    - Cryptography or PyCryptodome or OpenSSL
    - decided to use Cryptography
3. add in key management system, functions to generate key pair, encrypt and decrypt and create certificate
    - store key in database but as BLOB
4. add in sending message, receiving message, create/add/remove to group
    - user will join a group, then they can post messages, like a forum, if another use is in the group then they are able to see but if they are not they cannot see the decrypted messages
    - user can also send private messages? 
5. certificate management
    - only one certificate per user
    - when join group or sending message the certificate is checked
    - created a Certificate Revocation List (CRL)
