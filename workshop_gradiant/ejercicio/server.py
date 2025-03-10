import socket
import threading
from server_function import ServerFunctions
from rich.console import Console
from rich.panel import Panel

console = Console()


class Server:
    def __init__(self, host="127.0.0.1", port=65433):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_functions = ServerFunctions()
        self.is_running = True
        self.clients = []

    def handle_client(self, conn, addr):
        """Handle client connection and store it for sending packets."""
        try:
            console.print(Panel(f"[green]Connection established with {addr}[/green]"))
            self.clients.append(conn)

            while self.is_running:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break
        except Exception as e:
            console.print(f"[red]Error handling client: {e}[/red]")
        finally:
            self.clients.remove(conn)
            conn.close()
            console.print(Panel(f"[red]Connection closed with {addr}[/red]"))

    def send_packets_interactively(self):
        """Allow admin to send random packets interactively to all connected clients."""
        while self.is_running:
            console.print(Panel("[bold blue]Press Enter to send random packets to all clients...[/bold blue]"))
            input()  # Wait for Enter
            for conn in self.clients:
                try:
                    self.server_functions.send_random_packets(conn)
                except Exception as e:
                    console.print(f"[red]Failed to send packet: {e}[/red]")

    def start(self):
        """Start the server and manage client connections."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            console.print(Panel(f"[green]Server listening on {self.host}:{self.port}[/green]"))

            # Start the interactive packet-sending thread *after printing the message*
            threading.Thread(target=self.send_packets_interactively, daemon=True).start()

            while self.is_running:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutting down server...[/bold red]")
            self.is_running = False
        finally:
            for conn in self.clients:
                conn.close()
            self.server_socket.close()
            console.print("[red]Server socket closed.[/red]")


if __name__ == "__main__":
    server = Server()
    console.print(Panel("[bold yellow]Waiting for connections...[/bold yellow]"))  # Ensure the message appears first
    server.start()
