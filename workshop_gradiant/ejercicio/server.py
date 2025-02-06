import socket
import threading
from server_function import ServerFunctions
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


class Server:
    def __init__(self, host="127.0.0.1", port=65433):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_functions = ServerFunctions()
        self.is_running = True
        self.threads = []

    def handle_client(self, conn, addr):
        """
        Handle client communication. Supports:
        1. Mock timing attack handling.
        """
        try:
            console.print(Panel(f"[green]Connection established with {addr}[/green]"))

            while self.is_running:
                try:
                    # Listen for incoming data
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break

                    console.print(Panel(f"[cyan]Received request: {data}[/cyan]"))
                    if data.startswith("MOCK_ATTACK"):
                        # Handle timing attack
                        request = eval(data[len("MOCK_ATTACK"):])  # Parse the payload
                        self.server_functions.handle_timing_attack(conn, request)
                    else:
                        error_message = "Invalid request. Please try again."
                        console.print(f"[red]{error_message}[/red]")
                        conn.sendall(f"{error_message}\n".encode())
                except Exception as e:
                    console.print(f"[red]Error handling client data: {e}[/red]")
                    break
        finally:
            conn.close()
            console.print(Panel(f"[red]Connection closed with {addr}[/red]"))

    def send_random_packets_interactively(self):
        """
        Allow the server admin to send random packets interactively.
        """
        while self.is_running:
            try:
                console.print(
                    Panel("[bold blue]Press Enter to send random packets to all clients...[/bold blue]"),
                    style="cyan",
                )
                input()  # Wait for the server admin to press Enter
                for thread in self.threads:
                    if thread.is_alive():
                        conn = thread._args[0]  # Access the connection object
                        self.server_functions.send_random_packets(conn)
            except KeyboardInterrupt:
                console.print("\n[bold red]Stopped sending random packets.[/bold red]")
                break

    def start(self):
        """
        Start the server and manage client threads.
        """
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            console.print(Panel(f"[green]Server listening on {self.host}:{self.port}[/green]"))

            # Start the packet-sending thread
            packet_thread = threading.Thread(
                target=self.send_random_packets_interactively, daemon=True
            )
            packet_thread.start()

            while self.is_running:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(conn, addr)
                )
                self.threads.append(client_thread)
                client_thread.start()

        except KeyboardInterrupt:
            console.print("\n[bold red]Shutting down server...[/bold red]")
            self.is_running = False
        finally:
            for thread in self.threads:
                thread.join()
            self.server_socket.close()
            console.print("[red]Server socket closed.[/red]")


if __name__ == "__main__":
    server = Server()
    server.start()