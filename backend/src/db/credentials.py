"""
Encrypted credential storage management.

Handles secure storage and retrieval of user credentials using Fernet encryption.
"""

import os
from cryptography.fernet import Fernet
from typing import Optional, Tuple


class CredentialManager:
    """
    Manage encrypted credential storage in SQLite.
    """

    def __init__(self, db_session, encryption_key: Optional[str] = None):
        """
        Initialize CredentialManager.

        Args:
            db_session: SQLAlchemy database session
            encryption_key: Optional encryption key. If None, loads from BELLWEAVER_ENCRYPTION_KEY env var
        """
        self.db_session = db_session
        self.cipher = self._init_cipher(encryption_key)

    def _init_cipher(self, encryption_key: Optional[str]) -> Fernet:
        """Initialize Fernet cipher with key."""
        if encryption_key is None:
            encryption_key = os.getenv('BELLWEAVER_ENCRYPTION_KEY')

        if encryption_key is None:
            # Generate new key and save to .env
            key = Fernet.generate_key().decode()
            print(f"Generated encryption key: {key}")
            print("Save this to .env as BELLWEAVER_ENCRYPTION_KEY")
            encryption_key = key

        return Fernet(encryption_key.encode())

    def save_compass_credentials(self, username: str, password: str) -> None:
        """Encrypt and store Compass credentials."""
        encrypted_password = self.cipher.encrypt(password.encode()).decode()

        # Store in database (replace if exists)
        from src.db.models import Credential

        cred = self.db_session.query(Credential).filter_by(source='compass').first()
        if cred:
            cred.username = username
            cred.password_encrypted = encrypted_password
        else:
            cred = Credential(
                source='compass',
                username=username,
                password_encrypted=encrypted_password
            )
            self.db_session.add(cred)

        self.db_session.commit()

    def load_compass_credentials(self) -> Optional[Tuple[str, str]]:
        """Load and decrypt Compass credentials."""
        from src.db.models import Credential

        cred = self.db_session.query(Credential).filter_by(source='compass').first()
        if not cred:
            return None

        decrypted_password = self.cipher.decrypt(cred.password_encrypted.encode()).decode()
        return (cred.username, decrypted_password)
