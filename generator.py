import os
import hashlib
import time
import ecdsa
import base58
import audio_randomness
import secrets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEBUG = False

def generate_random_key_from_timing(events=10):
    try:
        return b''.join(
            hashlib.sha256(f'{time.time_ns()}'.encode() + secrets.token_bytes(8)).digest()
            for _ in range(events)
        )
    except Exception as e:
        logger.error(f"Error generating timing-based randomness: {e}")
        raise

def generate_combined_random_key(audio_entropy):
    try:
        combined_entropy = audio_entropy
        # Step 1: Initial randomness from secrets.token_bytes()
        combined_entropy += secrets.token_bytes(32)

        # Step 2: Add system timing entropy
        combined_entropy += generate_random_key_from_timing()

        # Generate final private key
        final_private_key = hashlib.sha256(combined_entropy).digest()
        return final_private_key
    except Exception as e:
        logger.error(f"Error generating combined random key: {e}")
        raise

def test_candidate(candidate):
    try:
        return hashlib.sha256((candidate + "?").encode()).digest()[0] == 0
    except Exception as e:
        logger.error(f"Error testing candidate: {e}")
        raise

def generate_mini_key():
    try:
        audio_entropy = audio_randomness.generate_random_key_from_audio()
        while True:
            private_key_bytes = generate_combined_random_key(audio_entropy)
            base58_encoded = base58.b58encode(private_key_bytes).decode()

            if len(base58_encoded) >= 29:
                mini_key = 'S' + base58_encoded[1:29]

                if test_candidate(mini_key):
                    if DEBUG:
                        logger.info(f"Mini key generated: {mini_key}")
                    return mini_key, private_key_bytes
                elif DEBUG:
                    logger.info(f"Invalid mini key: {mini_key}")
    except Exception as e:
        logger.error(f"Error generating mini key: {e}")
        raise

def mini_key_to_private_key(mini_key):
    """ Derive a private key from a mini key using SHA-256 """
    try:
        return hashlib.sha256(mini_key.encode('utf-8')).digest()
    except Exception as e:
        logger.error(f"Error deriving private key from mini key: {e}")
        raise

def private_key_to_public_key(private_key_bytes):
    try:
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.verifying_key
        public_key = b'\x04' + verifying_key.to_string()  # Uncompressed public key
        return public_key
    except Exception as e:
        logger.error(f"Error converting private key to public key: {e}")
        raise

def public_key_to_address(public_key_bytes):
    try:
        sha256_bpk = hashlib.sha256(public_key_bytes).digest()
        ripemd160_bpk = hashlib.new('ripemd160', sha256_bpk).digest()
        network_byte = b'\x00'  # Main network prefix for Bitcoin
        ripemd160_bpk = network_byte + ripemd160_bpk
        sha256_nbpk = hashlib.sha256(ripemd160_bpk).digest()
        sha256_2_nbpk = hashlib.sha256(sha256_nbpk).digest()
        checksum = sha256_2_nbpk[:4]
        binary_address = ripemd160_bpk + checksum
        address = base58.b58encode(binary_address).decode()
        return address
    except Exception as e:
        logger.error(f"Error converting public key to address: {e}")
        raise

def encode_private_key_wif(private_key_bytes):
    try:
        extended_key = b'\x80' + private_key_bytes  # Add 0x80 prefix for mainnet
        sha256_1 = hashlib.sha256(extended_key).digest()
        sha256_2 = hashlib.sha256(sha256_1).digest()
        checksum = sha256_2[:4]
        wif = base58.b58encode(extended_key + checksum).decode()
        return wif
    except Exception as e:
        logger.error(f"Error encoding private key to WIF: {e}")
        raise
