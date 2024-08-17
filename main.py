import generator

def main():
    num_keys = int(input("Enter the number of keys to generate: "))

    for i in range(1, num_keys + 1):
        # Generate a mini key and corresponding private key
        mini_key, private_key_bytes = generator.generate_mini_key()
        private_key_from_mini = generator.mini_key_to_private_key(mini_key)
        
        # Convert private key to public key
        public_key = generator.private_key_to_public_key(private_key_from_mini)
        bitcoin_address = generator.public_key_to_address(public_key)

        # Print the index, mini key, and public Bitcoin address
        print(f"{i}: Mini Key: {mini_key} -> Bitcoin Address: {bitcoin_address}")

if __name__ == "__main__":
    main()
