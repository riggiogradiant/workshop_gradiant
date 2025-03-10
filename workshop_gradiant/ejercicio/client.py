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
            console.print("[blue]4.[/blue] Quit")

            choice = Prompt.ask("[cyan]Choose an option[/cyan]")

            if choice == "1":
                with self.lock:  # Lock to safely access shared resources
                    self.functions.display_packets_table(self.received_packets)
            elif choice == "2":
                self.functions.decrypt_packets_submenu(self.received_packets)
            elif choice == "3":
                self.functions.break_caesar_cipher(self.received_packets)
            elif choice == "4":
                console.print("[red]Exiting the client.[/red]")
                self.running = False
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
      
if __name__ == "__main__":
    cliente = Cliente()
    cliente.conectar()
