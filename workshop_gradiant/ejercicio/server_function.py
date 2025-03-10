import random
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

class ServerFunctions:

    def send_random_packets(self, conn):
        """
        Function to send a random number of encrypted packets with random messages and methods to the client.
        This will continue until the user decides to stop by pressing "Ctrl+C".
        Finally, sends a packet with the value "END".
        """
        encryption_methods = ["Caesar", "XOR", "AES"]
        messages = [
            "HELLO FROM SERVER",
            "FORO TECNOLÓGICO XXV",
            "WORKSHOP GRADIANT",
            "CELTA DE VIGO",
        ]

        key = b"0123456789abcdef"
        iv = b"abcdef0123456789"
        shift = 3
        xor_key = 42

        try:
            while True:
                try:
                    input(
                        "Press Enter to send the packets..."
                    )  # Wait for Enter key press

                    num_packets = random.randint(5, 10)
                    print(f"Sending {num_packets} random packets...")

                    for _ in range(num_packets):
                        # Randomly select a message and encryption method
                        message = random.choice(messages)
                        method = random.choice(encryption_methods)

                        # Encrypt the message based on the selected method
                        if method == "Caesar":
                            encrypted_message = self.caesar_encrypt(message, shift)
                        elif method == "XOR":
                            encrypted_message = self.xor_encrypt(message, xor_key)
                        elif method == "AES":
                            encrypted_message = self.aes_encrypt(message, key, iv).hex()

                        # Create a packet with the selected method and encrypted message
                        packet = {"method": method, "data": encrypted_message}

                        # Send the packet to the client
                        conn.sendall(json.dumps(packet).encode() + b"\n")
                        #print(f"Packet sent with method {method}: {encrypted_message}")

                        # Optional: Add a 1-second pause between packets
                        time.sleep(1)

                    # Send the "END" packet after all the random packets have been sent
                    end_packet = {"method": "END", "data": "END"}
                    conn.sendall(json.dumps(end_packet).encode() + b"\n")
                    print("END packet sent.")

                except KeyboardInterrupt:
                    print("\nInterrupted by user. Closing connection...")
                    break  # Exit the loop if Ctrl+C is pressed

        finally:
            # Close the connection properly in case of interruption or when done
            conn.close()
            print("Connection closed.")

    def caesar_encrypt(self, text, shift):
        """
        Encrypt the text using Caesar Cipher.
        """
        return "".join(chr((ord(c) - 32 + shift) % 95 + 32) for c in text)

    def xor_encrypt(self, text, key):
        """
        Encrypt the text using XOR encryption.
        """
        return "".join(chr(ord(c) ^ key) for c in text)

    def aes_encrypt(self, text, key, iv):
        """
        Encrypt the text using AES encryption.
        """
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding
        from cryptography.hazmat.backends import default_backend

        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode()) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()
    
    def tls_vulnerable_decrypt(self, ciphertext, secret_plaintext):
        """
        Simulate a vulnerable TLS 1.0 decryption process with timing leaks.
        """
        start_time = time.time()  # Track time for debugging
        for i in range(len(ciphertext)):
            # Simulate processing time for a correct byte match
            if i >= len(secret_plaintext) or ciphertext[i] != secret_plaintext[i]:
                time.sleep(0.01)  # Short delay for incorrect guess
                console.print(f"[yellow]Decryption failed at byte {i+1}[/yellow]")
                return False  # Decryption failed
            time.sleep(0.05)  # Longer delay for correct guess

        elapsed_time = time.time() - start_time
        console.print(f"[green]Decryption successful! Time: {elapsed_time:.4f} seconds[/green]")
        return True  # Decryption successful

    def handle_timing_attack(self, conn, data):
        secret_plaintext = "HE"
        ciphertext = data.get("data")
        response = {}
        if ciphertext == secret_plaintext[0] or ciphertext == secret_plaintext[1]:
            response = {"status": "Decryption complete"}
            console.print("[green]Decryption complete[/green]")
            time.sleep(0.05)
        else:
            response = {"status": "Decryption failed"}
            console.print("[red]Decryption failed[/red]")
            time.sleep(0.005)
        conn.sendall(json.dumps(response).encode() + b"\n")
