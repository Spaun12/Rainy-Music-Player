from cryptography.fernet import Fernet

# Example test to encrypt and then immediately decrypt a message
def test_encryption():
    # Load the key from 'secret.key'
    with open("secret.key", "rb") as key_file:
        key = key_file.read()

    f = Fernet(key)

    # Test message
    message = "Hello, World!"
    encrypted = f.encrypt(message.encode())
    decrypted = f.decrypt(encrypted).decode()

    print("Original:", message)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)

test_encryption()
