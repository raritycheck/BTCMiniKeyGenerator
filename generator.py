import os
import hashlib
import time
from pynput import mouse
import ecdsa
import base58

# Global variable to store collected entropy from mouse movements
entropy = b''

# Mouse movement event handlers
def on_move(x, y):
    global entropy
    entropy += hashlib.sha256(f'{x},{y},{time.time()}'.encode()).digest()

def on_click(x, y, button, pressed):
    global entropy
    entropy += hashlib.sha256(f'{x},{y},{button},{pressed},{time.time()}'.encode()).digest()

def on_scroll(x, y, dx, dy):
    global entropy
    entropy += hashlib.sha256(f'{x},{y},{dx},{dy},{time.time()}'.encode()).digest()

# Function to generate additional randomness from system timings
def generate_random_key_from_timing(events=100):
    extra_entropy = b''
    for _ in range(events):
        time_entropy = hashlib.sha256(f'{time.time_ns()}'.encode() + os.urandom(8)).digest()
        extra_entropy += time_entropy
        time.sleep(0.01)
    return extra_entropy

# Combined function to generate a random private key
def generate_combined_random_key():
    # Step 1: Initial randomness from os.urandom()
    initial_entropy = os.urandom(32)

    # Step 2: Collect mouse movement entropy
    listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    listener.start()
    print("Move your mouse randomly for a few seconds to generate entropy...")
    time.sleep(5)
    listener.stop()

    # Step 3: Add system timing entropy
    timing_entropy = generate_random_key_from_timing()

    # Combine all sources of entropy
    combined_entropy = initial_entropy + entropy + timing_entropy
    final_private_key = hashlib.sha256(combined_entropy).digest()

    return final_private_key

# Convert the private key to a public key
def private_key_to_public_key(private_key_bytes):
    signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    verifying_key = signing_key.verifying_key
    public_key = b'\x04' + verifying_key.to_string()  # Uncompressed public key
    return public_key

# Convert the public key to a Bitcoin address
def public_key_to_address(public_key_bytes):
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

# Encode the private key in WIF format
def encode_private_key_wif(private_key_bytes):
    extended_key = b'\x80' + private_key_bytes  # Add 0x80 prefix for mainnet
    sha256_1 = hashlib.sha256(extended_key).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    checksum = sha256_2[:4]
    wif = base58.b58encode(extended_key + checksum).decode()
    return wif
