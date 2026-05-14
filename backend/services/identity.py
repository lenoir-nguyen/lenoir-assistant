import bcrypt
from config import get_settings

settings = get_settings()

OWNER_PASSPHRASE = "i am lenoir"


def contains_passphrase(message: str) -> bool:
    """Check if message contains the owner passphrase (case-insensitive)."""
    return OWNER_PASSPHRASE in message.lower().strip()


def verify_pin(provided_pin: str) -> bool:
    """Verify the provided PIN against the stored hash in environment."""
    if not settings.OWNER_PIN_HASH:
        raise ValueError("OWNER_PIN_HASH not configured in environment")

    try:
        # Verify PIN against the bcrypt hash stored in environment
        return bcrypt.checkpw(
            provided_pin.encode('utf-8'),
            settings.OWNER_PIN_HASH.encode('utf-8')
        )
    except (ValueError, TypeError) as e:
        # Invalid hash format or other bcrypt error
        return False


def hash_pin(pin: str) -> str:
    """Generate bcrypt hash for a PIN (for setup only, not used at runtime)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')
