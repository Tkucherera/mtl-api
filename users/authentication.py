import scrypt
import os

def secure_password(password, datalength=64, maxtime=0.5):
    return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)


def verify_password(hashed_password, guessed_password, maxtime=0.5):
    """Verify a password against its hash with better error handling.

    Args:
        hashed_password: The stored password hash from hash_password()
        guessed_password: The password to verify
        maxtime: Maximum time to spend in verification

    Returns:
        tuple: (is_valid, status_code) where:
            - is_valid: True if password is correct, False otherwise
            - status_code: One of "correct", "wrong_password", "time_limit_exceeded",
              "memory_limit_exceeded", or "error"

    Raises:
        scrypt.error: Only raised for resource limit errors, which you may want to
                    handle by retrying with higher limits or force=True
    """
    try:
        scrypt.decrypt(hashed_password, guessed_password, maxtime, encoding=None)
        return True, "correct"
    except scrypt.error as e:
        # Check the specific error message to differentiate between causes
        error_message = str(e)
        if error_message == "password is incorrect":
            # Wrong password was provided
            return False, "wrong_password"
        elif error_message == "decrypting file would take too long":
            # Time limit exceeded
            raise  # Re-raise so caller can handle appropriately
        elif error_message == "decrypting file would take too much memory":
            # Memory limit exceeded
            raise  # Re-raise so caller can handle appropriately
        else:
            # Some other error occurred (corrupted data, etc.)
            return False, "error"
        





