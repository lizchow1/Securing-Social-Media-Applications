import os
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from datetime import datetime, timedelta, timezone
from models import User, RevokedCertificate

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize the private key to PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize the public key to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Return the serialized private and public keys
    return private_key_pem, public_key_pem

def create_certificate(user_id):
    # Generate the user's key pair
    user_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    user_public_key = user_private_key.public_key()

    # Create a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, user_id),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        user_public_key
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=1)  
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).sign(user_private_key, hashes.SHA256())

    # Serialize private key to PEM format
    private_key_pem = user_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize public key to PEM format
    public_key_pem = user_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    certificate_pem = cert.public_bytes(Encoding.PEM)

    return private_key_pem, public_key_pem, certificate_pem

def encrypt_message(public_key_pem, message):
    # Load the public key from PEM format
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
    
    # Encrypt the message
    encrypted_message = public_key.encrypt(
        message.encode(),  # Ensure the message is bytes
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message

def decrypt_message(private_key_pem, encrypted_message):
    # Deserialize the private key from PEM format
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,  # If your key is password-protected, provide it here
        backend=default_backend()
    )
    
    # Decrypt the message using the private key
    original_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return original_message.decode()

def validate_certificate(certificate_pem):
    """
    Validates a certificate's validity period and checks if it's revoked.
    """
    certificate = x509.load_pem_x509_certificate(certificate_pem, default_backend())

    # Use not_valid_before_utc and not_valid_after_utc
    current_time_utc = datetime.now(timezone.utc)  # Ensure current time is timezone-aware, in UTC
    if current_time_utc < certificate.not_valid_before_utc or current_time_utc > certificate.not_valid_after_utc:
        print("Certificate is outside its validity period.")
        return False

    if RevokedCertificate.query.filter_by(user_id=str(certificate.serial_number)).first():
        print("Certificate has been revoked.")
        return False

    return True

def get_certificate_serial_number_for_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user and user.certificate:
        certificate = x509.load_pem_x509_certificate(user.certificate, default_backend())
        return certificate.serial_number
    return None


def generate_ca_key_pair():
    if not os.path.exists("ca_private_key.pem") or not os.path.exists("ca_public_key.pem"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Save the private key
        with open("ca_private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the public key
        with open("ca_public_key.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

def load_ca_private_key():
    with open("ca_private_key.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,  # Update if you use encryption
            backend=default_backend()
        )

def load_ca_public_key():
    with open("ca_public_key.pem", "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )


# Ensure CA keys are generated at module import time
generate_ca_key_pair()