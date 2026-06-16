#!/usr/bin/env python3
"""
Bitcoin Private Key to Public Address Converter

Converts a WIF-format private key into BOTH:
  - Legacy P2PKH address      (starts with '1')
  - Native SegWit P2WPKH addr (starts with 'bc1q')

This demonstrates that ONE private key produces multiple valid
address formats. Two addresses looking totally different does NOT
mean different owners -- they can be the same key in two clothes.
"""

import hashlib
import base58


# ---------------------------------------------------------------------------
# WIF decoding
# ---------------------------------------------------------------------------
def decode_wif(wif_key):
    """Decode a WIF private key to raw private key bytes + compressed flag."""
    decoded = base58.b58decode(wif_key)

    # Layout: [version 1B][priv key 32B][optional 0x01 1B][checksum 4B]
    private_key = decoded[1:-4]

    compressed = len(private_key) == 33
    if compressed:
        private_key = private_key[:-1]

    return private_key, compressed


# ---------------------------------------------------------------------------
# Public key derivation (secp256k1)
# ---------------------------------------------------------------------------
def private_key_to_public_key(private_key_bytes, compressed=True):
    """Generate the public key from a private key using secp256k1."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ec import (
            derive_private_key,
            SECP256K1,
        )

        private_int = int.from_bytes(private_key_bytes, "big")
        sk = derive_private_key(private_int, SECP256K1())
        pub = sk.public_key().public_numbers()

        if compressed:
            prefix = b"\x02" if pub.y % 2 == 0 else b"\x03"
            return prefix + pub.x.to_bytes(32, "big")
        return b"\x04" + pub.x.to_bytes(32, "big") + pub.y.to_bytes(32, "big")

    except ImportError:
        print("Error: cryptography library not found.")
        print("Install with: pip install cryptography")
        raise


# ---------------------------------------------------------------------------
# HASH160 helper (SHA-256 then RIPEMD-160) -- shared by both address types
# ---------------------------------------------------------------------------
def hash160(data):
    sha256_hash = hashlib.sha256(data).digest()
    return hashlib.new("ripemd160", sha256_hash).digest()


# ---------------------------------------------------------------------------
# Legacy P2PKH address  (starts with '1')
# ---------------------------------------------------------------------------
def public_key_to_p2pkh(public_key):
    pubkey_hash = hash160(public_key)
    versioned = b"\x00" + pubkey_hash  # 0x00 = mainnet P2PKH
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58.b58encode(versioned + checksum).decode("utf-8")


# ---------------------------------------------------------------------------
# Native SegWit P2WPKH address  (starts with 'bc1q')  -- Bech32
# ---------------------------------------------------------------------------
# Self-contained Bech32 implementation (BIP-0173) so there are no extra deps.
_BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _bech32_polymod(values):
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _bech32_create_checksum(hrp, data):
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def _bech32_encode(hrp, data):
    combined = data + _bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([_BECH32_CHARSET[d] for d in combined])


def _convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    return ret


def public_key_to_p2wpkh(public_key, hrp="bc"):
    """Native SegWit v0 address. Requires a COMPRESSED public key."""
    if public_key[0] not in (0x02, 0x03):
        raise ValueError(
            "SegWit (bc1q) requires a compressed public key. "
            "This WIF decoded as uncompressed."
        )
    pubkey_hash = hash160(public_key)
    # witness version 0, then the 20-byte program (5-bit converted)
    data = [0] + _convertbits(list(pubkey_hash), 8, 5)
    return _bech32_encode(hrp, data)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def wif_to_addresses(wif_key):
    private_key, compressed = decode_wif(wif_key)

    print(f"Private Key (hex): {private_key.hex()}")
    print(f"Compressed:        {compressed}")

    public_key = private_key_to_public_key(private_key, compressed)
    print(f"Public Key (hex):  {public_key.hex()}")
    print("-" * 60)

    p2pkh = public_key_to_p2pkh(public_key)
    print(f"Legacy  (P2PKH)  : {p2pkh}")

    if compressed:
        p2wpkh = public_key_to_p2wpkh(public_key)
        print(f"SegWit  (P2WPKH) : {p2wpkh}")
    else:
        p2wpkh = None
        print("SegWit  (P2WPKH) : n/a (key is uncompressed; bc1q "
              "needs a compressed key)")

    return p2pkh, p2wpkh


if __name__ == "__main__":
    # Random example key -- never put a real private key in a script.
    example_wif = "L3dwadwabC18FcwAjQxzt9pmq"

    print("Bitcoin WIF -> All Addresses")
    print("=" * 60)
    print(f"WIF Private Key: {example_wif[0:5]}... (truncated for display)")
    print("-" * 60)

    try:
        wif_to_addresses(example_wif)
        print("=" * 60)
        print("\nNote: both addresses above belong to the SAME key.")
        print("Different format != different owner.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nInstall required libraries:")
        print("  pip install base58 cryptography")
 