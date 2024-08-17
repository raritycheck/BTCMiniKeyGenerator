from generator import generate_combined_random_key, public_key_to_address, encode_private_key_wif

def main():
    num_keys = int(input("Enter the number of keys to generate: "))
    
    for i in range(1, num_keys + 1):
        # Generate a secure random private key
        full_private_key = generate_combined_random_key()

        # Encode the private key in WIF format (optional)
        wif_private_key = encode_private_key_wif(full_private_key)

        # Generate the public key from the private key
        public_key = private_key_to_public_key(full_private_key)

        # Generate the Bitcoin address from the public key
        bitcoin_address = public_key_to_address(public_key)

        # Print the index, WIF private key, and public Bitcoin address
        print(f"{i}: {wif_private_key} -> {bitcoin_address}")

if __name__ == "__main__":
    main()
