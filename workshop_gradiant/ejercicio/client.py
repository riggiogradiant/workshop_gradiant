import socket
import json
from time import time
import threading
from client_function import ClientFunctions
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

console = Console()


class Cliente:
    def __init__(self, host="127.0.0.1", port=65433):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.functions = ClientFunctions()
        self.received_packets = []  # Shared list to store packets
        self.method_count = {}  # Shared dictionary for method count
        self.lock = threading.Lock()  # Lock to synchronize access to shared resources
        self.running = True  # To control the listening thread

    def conectar(self):
        self.client_socket.connect((self.host, self.port))

        listener_thread = threading.Thread(target=self.listen_for_packets)
        listener_thread.daemon = True
        listener_thread.start()

        self.display_menu()  # Display the menu in the main thread

        # Stop the listener when exiting
        self.running = False
        listener_thread.join()
        self.client_socket.close()

    def listen_for_packets(self):
        first_packet = True  # Flag to track the first packet

        while self.running:
            try:
                data = self.client_socket.recv(1024)  # Receive up to 1024 bytes
                if not data:
                    break

                messages = data.decode().splitlines()  # Separate by lines using '\n'
                for message in messages:
                    try:
                        with self.lock:  # Lock to safely access shared resources
                            
                            self.received_packets = self.functions.process_end_packet(
                                message, self.received_packets, self.method_count
                            )
                            if first_packet:
                                first_packet = False
                                console.print(
                                    f"\n[green]New packet received! Total packets: {len(self.received_packets)}[/green]"
                                )  # Extra newline for the first message
                            else:
                                packet = json.loads(message)
                                if packet["method"]!= "END":
                                    console.print(
                                        f"[green]New packet received! Total packets: {len(self.received_packets)}[/green]"
                                    )
                                else :
                                    first_packet = True # reset after all packets are received after receivinf END for the next batch
                                    self.functions.refresh_menu()
                    except json.JSONDecodeError as e:
                        console.print(f"[red]Error decoding message: {e}[/red]")

            except Exception as e:
                console.print(f"[red]Error in listener thread: {e}[/red]")


    def display_menu(self):
        while True:
            console.print(
                Panel.fit("[bold magenta]--- Main Menu ---[/bold magenta]")
            )
            console.print("[blue]1.[/blue] See all packets")
            console.print("[blue]2.[/blue] Decrypt a packet")
            console.print("[blue]3.[/blue] Break Caesar Cipher")
            console.print("[blue]4.[/blue] Break TLS version 1 cipher")
            console.print("[blue]5.[/blue] Quit")

            choice = Prompt.ask("[cyan]Choose an option[/cyan]")

            if choice == "1":
                with self.lock:  # Lock to safely access shared resources
                    self.functions.display_packets_table(self.received_packets)
            elif choice == "2":
                self.functions.decrypt_packets_submenu(self.received_packets)
            elif choice == "3":
                self.functions.break_caesar_cipher(self.received_packets)
            elif choice == "4":
                self.timing_attack()
            elif choice == "5":
                console.print("[red]Exiting the client.[/red]")
                self.running = False
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
    # def timing_attack(self):
    #     """
    #     Perform a mock timing attack against the server using self.client_socket.
    #     """
    #     console.print(Panel("[bold magenta]Starting Mock Timing Attack[/bold magenta]"))

    #     # Simulated ciphertext to attack
    #     ciphertext = "HE"  # Ciphertext length is known
    #     guessed_plaintext = ""
    #     charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789! "  # Possible characters

    #     console.print(
    #         Panel(f"[bold cyan]Ciphertext to attack:[/bold cyan] {ciphertext}"),
    #         style="bold green",
    #     )

    #     # Loop to guess each byte of the plaintext
    #     for position in range(len(ciphertext)):
    #         console.print(
    #             Panel(f"[yellow]Guessing byte {position + 1}/{len(ciphertext)}[/yellow]"),
    #             style="bold yellow",
    #         )
    #         best_guess = None
    #         best_time = 0

    #         for char in charset:
    #             # Create a "partial plaintext" guess
    #             partial_guess = guessed_plaintext + char + "?" * (len(ciphertext) - position - 1)
    #             console.print(f"Trying '{partial_guess}'...", style="dim")

    #             # Create attack packet
    #             attack_packet = {"data": guessed_plaintext + char}
    #             attack_packet = f"MOCK_ATTACK{json.dumps(attack_packet)}"

    #             # Send the mock attack request
    #             start_time = time()
    #             self.client_socket.sendall(attack_packet.encode())
    #             print("1")
    #             # Receive server response
    #             try:
    #                 response = self.client_socket.recv(1024).decode()
    #                 print("2 - Raw server response:", response)
    #                 elapsed_time = time() - start_time
    #                 print("3 - Time elapsed:", elapsed_time)
                    
    #                 # Parse server response
    #                 response_data = json.loads(response)
    #                 print("4 - Parsed server response:", response_data)
                    
    #                 # Handle possible missing keys in the response
    #                 if 'status' in response_data:
    #                     print(f"Server Response: {response_data['status']}")
    #                 else:
    #                     print("Server Response: Invalid format or missing 'status' key.")
                    
    #             except json.JSONDecodeError as e:
    #                 print(f"[red]Error decoding JSON response: {e}[/red]")
    #                 # Log server response and timing
    #                 console.print(
    #                     f"Character '{char}' took {elapsed_time:.4f} seconds to process.",
    #                     style="dim cyan",
    #                 )
    #                 console.print(f"Server Response: {response_data}", style="dim green")

    #                 # Check if this character caused the longest delay
    #                 if elapsed_time > best_time:
    #                     best_time = elapsed_time
    #                     best_guess = char
    #             except Exception as e:
    #                 console.print(
    #                     f"[red]Error during attack: {e}[/red]\n[red]Skipping this character...[/red]"
    #                 )
    #                 continue

    #         # Update the guessed plaintext with the best guess for this byte
    #         guessed_plaintext += best_guess

    #         # Show progress with detailed timing information
    #         console.print(
    #             Panel(
    #                 f"[bold green]Best guess so far:[/bold green] {guessed_plaintext}\n"
    #                 f"[cyan]Longest delay for byte {position + 1}: {best_time:.4f} seconds[/cyan]",
    #                 title="Progress",
    #                 style="green",
    #             )
    #         )

    #     # Attack complete
    #     console.print(
    #         Panel(
    #             f"[bold magenta]Attack Complete![/bold magenta]\n"
    #             f"Recovered Plaintext: [bold green]{guessed_plaintext}[/bold green]",
    #             style="green",
    #         )
    #     )
    def timing_attack(self):
        guessed_plaintext = ""
        best_time = 0
        best_guess = ""
        charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789! "
        for char in charset:
                partial_guess = guessed_plaintext + char
                console.print(f"Trying '{partial_guess}'...", style="dim")

                # Create attack packet
                attack_packet = {"data":partial_guess}
                attack_packet = f"MOCK_ATTACK{json.dumps(attack_packet)}"
                self.client_socket.sendall(attack_packet.encode())
                start_time = time()
                try:
                    response = self.client_socket.recv(1024).decode()
                    print("2 - Raw server response:", response)
                    elapsed_time = time() - start_time
                    print("3 - Time elapsed:", elapsed_time)
                    response_data = json.loads(response)
                    print("4 - Parsed server response:", response_data) 
                    if elapsed_time > best_time:
                        best_time = elapsed_time
                        best_guess = char               
                except Exception as e:
                    console.print(
                        f"[red]Error during attack: {e}[/red]\n[red]Skipping this character...[/red]"
                    )
                    continue
        guessed_plaintext += best_guess

        # Show progress with detailed timing information
        console.print(
            Panel(
                f"[bold green]Best guess so far:[/bold green] {guessed_plaintext}\n",
                title="Progress",
                style="green",
            )
        )        
if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()
