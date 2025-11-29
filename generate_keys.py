from cobo_waas2.crypto.local_ed25519_signer import LocalEd25519Signer

def generate_keys():
    print("Generating Ed25519 Key Pair for Cobo API...")
    # The SDK doesn't have a direct 'generate' method exposed easily in the signer, 
    # but we can use the underlying library or just use a helper if available.
    # Actually, LocalEd25519Signer takes a private key.
    # Let's use nacl or similar if installed, or just os.urandom if we can format it.
    # Wait, let's check if we can use the SDK to generate.
    
    try:
        import naci.signing
        import binascii
        # This might not be installed.
    except ImportError:
        pass

    # Let's use a standard way or check if the user has a tool.
    # Actually, for simplicity, I will provide a script that uses `ed25519` or `nacl` if available, 
    # but since I don't know the env, I'll use the `cobo_waas2` dependency `cryptography` or similar.
    
    # Cobo WaaS 2 SDK depends on `cryptography`.
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization

    private_key = ed25519.Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    print("\n✅ Keys Generated Successfully!\n")
    print(f"API_PRIVATE_KEY={private_bytes.hex()}")
    print(f"API_PUBLIC_KEY={public_bytes.hex()}")
    print("\nInstructions:")
    print("1. Copy the API_PUBLIC_KEY and register it in Cobo Dashboard (Developers -> API Keys).")
    print("2. Copy the API_PRIVATE_KEY to your .env file as COBO_API_PRIVATE_KEY.")
    print("3. Update COBO_API_URL to https://api.cobo.com/v2")

if __name__ == "__main__":
    generate_keys()
