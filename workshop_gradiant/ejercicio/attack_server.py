import socket
import json
import time
from rich.console import Console
from rich.panel import Panel

console = Console()


class TimingAttackServer:
    def __init__(self, host="127.0.0.1", port=65433):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secret_plaintext = "HELLO"  # The secret plaintext the client is trying to guess

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            console.print(Panel(f"[green]Server listening on {self.host}:{self.port}[/green]"))

            conn, addr = self.server_socket.accept()
            console.print(Panel(f"[blue]Connection established with {addr}[/blue]"))

            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                console.print(Panel(f"[cyan]Received request: {data}[/cyan]"))
                if data.startswith("MOCK_ATTACK"):
                    payload = json.loads(data[len("MOCK_ATTACK"):])
                    self.handle_timing_attack(conn, payload)
                else:
                    conn.sendall(
                        json.dumps({"status": "Invalid request"}).encode() + b"\n"
                    )

        except KeyboardInterrupt:
            console.print("\n[bold red]Server shutting down...[/bold red]")
        finally:
            self.server_socket.close()

    def handle_timing_attack(self, conn, payload):
        guessed_text = payload.get("data", "")
        console.print(f"[yellow]Processing guess: {guessed_text}[/yellow]")

        if guessed_text == self.secret_plaintext[: len(guessed_text)]:
            time.sleep(0.05)  # Simulate longer response time for a correct guess
        else:
            time.sleep(0.005)  # Simulate shorter response time for an incorrect guess

        # Always send a generic "Decryption failed" response
        conn.sendall(json.dumps({"status": "Decryption failed"}).encode() + b"\n")


if __name__ == "__main__":
    server = TimingAttackServer()
    server.start()
