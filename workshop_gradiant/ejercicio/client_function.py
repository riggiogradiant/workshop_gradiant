from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

console = Console()
class ClientFunctions:
    def caesar_decrypt(self, text, shift):
        return "".join(chr((ord(c) - 32 - shift) % 95 + 32) for c in text)

    def xor_decrypt(self, text, key):
        return "".join(chr(ord(c) ^ key) for c in text)

    def aes_decrypt(self, encrypted_data, key, iv):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted_padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
        return unpadder.update(decrypted_padded_data) + unpadder.finalize()

    def process_end_packet(self, message, received_packets, method_count):
        """
        Process the messages received when the END message arrives, count them, print them, and return the list of them.
        """
        packet = json.loads(message)
        received_packets.append(packet)
        method = packet["method"]

        if method == "END":
            received_packets.pop()

        return received_packets

    def see_all_packets(self, received_packets):
        for i, packet in enumerate(received_packets, start=1):
            method = packet["method"]
            data = packet["data"].replace("\n", "\\n")  # To display \n instead of line breaks
            print(f"Packet {i} Method [{method}] Data [{data}]")
            
    def break_caesar_cipher(self, received_packets):
        if not received_packets:
            console.print("[red]No packets available to break Caesar cipher![/red]")
            return

        # Display packets in a table
        table = Table(title="Available Packets")
        table.add_column("No.", style="cyan", justify="center")
        table.add_column("Method", style="green", justify="center")
        table.add_column("Data (Preview)", style="white")

        for i, packet in enumerate(received_packets, start=1):
            method = packet["method"]
            data_preview = (
                packet["data"][:30] + "..." if len(packet["data"]) > 30 else packet["data"]
            )
            table.add_row(str(i), method, data_preview)

        console.print(table)

        # Prompt user to select a packet
        choices = [str(i) for i in range(1, len(received_packets) + 1)]
        choice = Prompt.ask("Choose a packet to break", choices=choices, default="1")
        packet = received_packets[int(choice) - 1]

        if packet["method"] != "Caesar":
            console.print("[red]Selected packet is not encrypted with Caesar cipher![/red]")
            return

        ciphertext = packet["data"]
        console.print(f"\n[bold blue]Breaking Caesar Cipher for the packet data: {ciphertext}[/bold blue]\n")

        # Brute force all possible shifts
        for shift in range(95):  # 95 ASCII printable characters
            plaintext = self.caesar_decrypt(ciphertext, shift)
            console.print(f"[green]Shift {shift}: {plaintext}[/green]")

        console.print("[bold magenta]All possible shifts have been tried. Observe why Caesar cipher is insecure![/bold magenta]")
        
    def refresh_menu(self):
        console.print(
            Panel.fit("[bold magenta]--- Main Menu ---[/bold magenta]")
        )
        console.print("[blue]1.[/blue] See all packets")
        console.print("[blue]2.[/blue] Decrypt a packet")
        console.print("[blue]3.[/blue] Break Caesar Cipher")
        console.print("[blue]5.[/blue] Quit")
        console.print("[cyan]Choose an option: [/cyan]", end="")
    
    def decrypt_packet(self, packet):
        console.print(
            Panel.fit("[bold magenta]--- Choose Decryption Method ---[/bold magenta]")
        )
        console.print("[blue]1.[/blue] Caesar Cipher")
        console.print("[blue]2.[/blue] XOR")
        console.print("[blue]3.[/blue] AES")
        console.print("[blue]4.[/blue] Back")

        choice = Prompt.ask("[cyan]Choose an option[/cyan]")

        # Default values from the code
        shift = 3
        xor_key = 42
        key = b"0123456789abcdef"
        iv = b"abcdef0123456789"

        if choice == "1":
            decrypted_data = self.caesar_decrypt(packet["data"], shift)
            console.print(
                f"\n[green]Decrypted Data (Caesar Cipher, Shift={shift}):[/green]\n{decrypted_data}"
            )
        elif choice == "2":
            decrypted_data = self.xor_decrypt(packet["data"], xor_key)
            console.print(
                f"\n[green]Decrypted Data (XOR, Key={xor_key}):[/green]\n{decrypted_data}"
            )
        elif choice == "3":
            try:
                decrypted_data = self.aes_decrypt(packet["data"], key, iv)
                console.print(
                    f"\n[green]Decrypted Data (AES, Key={key}, IV={iv}):[/green]\n{decrypted_data}"
                )
            except Exception as e:
                console.print(f"[red]Error decrypting AES: {e}[/red]")
        elif choice == "4":
            return
        else:
            console.print("[red]Invalid choice. Returning to the menu.[/red]")
            
    def decrypt_packets_submenu(self, received_packets):
        if not received_packets:
            console.print("[yellow]No packets available to decrypt.[/yellow]")
            return

        self.display_packets_table(received_packets)
        console.print(
            Panel.fit("[magenta]--- Decrypt a Packet ---[/magenta]")
        )
        packet_index = IntPrompt.ask(
            "[cyan]Choose a packet number to decrypt (or 0 to go back)[/cyan]"
        )

        if packet_index == 0:
            return

        if 1 <= packet_index <= len(received_packets):
            packet = received_packets[packet_index - 1]
            self.decrypt_packet(packet)
        else:
            console.print("[red]Invalid packet number. Returning to the menu.[/red]")
            
    def display_packets_table(self, received_packets):
        if not received_packets:
            console.print("[yellow]No packets available to display.[/yellow]")
            return

        table = Table(title="Received Packets")
        table.add_column("No.", style="cyan", justify="center")
        table.add_column("Method", style="green", justify="center")
        table.add_column("Data (Preview)", style="white")

        for i, packet in enumerate(received_packets, start=1):
            method = packet["method"]
            data_preview = (
                packet["data"][:30] + "..." if len(packet["data"]) > 30 else packet["data"]
            )
            table.add_row(str(i), method, data_preview)

        console.print(table)

    
