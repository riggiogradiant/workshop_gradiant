import socket
import json
from time import time
from rich.console import Console
from rich.panel import Panel

console = Console()


class TimingAttackClient:
    def __init__(self, host="127.0.0.1", port=65433):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789! "
        self.guessed_plaintext = ""

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            console.print(Panel(f"[green]Connected to server at {self.host}:{self.port}[/green]"))
        except Exception as e:
            console.print(f"[red]Error connecting to server: {e}[/red]")
            exit(1)

    def timing_attack(self):
        while True:
            best_time = 0
            best_guess = ""
            console.print(Panel(f"[yellow]Current plaintext guess: '{self.guessed_plaintext}'[/yellow]"))

            for char in self.charset:
                partial_guess = self.guessed_plaintext + char
                console.print(f"Trying '{partial_guess}'...", style="dim")

                # Create attack packet
                attack_packet = {"data": partial_guess}
                attack_packet = f"MOCK_ATTACK{json.dumps(attack_packet)}"
                self.client_socket.sendall(attack_packet.encode())

                # Measure response time
                start_time = time()
                try:
                    response = self.client_socket.recv(1024).decode()
                    elapsed_time = time() - start_time

                    response_data = json.loads(response)
                    console.print(f"Server response: {response_data}", style="blue")
                    console.print(f"Response time: {elapsed_time:.5f} seconds", style="cyan")

                    # Record the best guess based on response time
                    if elapsed_time > best_time:
                        best_time = elapsed_time
                        best_guess = char

                except Exception as e:
                    console.print(f"[red]Error during attack: {e}[/red]\n[red]Skipping this character...[/red]")
                    continue

            self.guessed_plaintext += best_guess
            console.print(f"[green]Best guess for current position: '{best_guess}'[/green]")

            if len(self.guessed_plaintext) == 5:  # Stop when the plaintext length is known
                console.print(f"[bold green]Decryption successful! Plaintext: '{self.guessed_plaintext}'[/bold green]")
                break

    def close(self):
        self.client_socket.close()


if __name__ == "__main__":
    client = TimingAttackClient()
    client.connect()
    client.timing_attack()
    client.close()
