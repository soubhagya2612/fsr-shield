import os
import sys
import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

# Importing our custom modules
from downloader import get_latest_release_info, download_file
from security import verify_file
from installer import extract_specific_dlls, deploy_to_game
from games import SUPPORTED_GAMES, find_steam_game_path
from manifest import is_hash_trusted

# Initialize the rich console for styled output
console = Console()


def render_banner():
    """Renders a stylized ASCII banner for the CLI."""
    ascii_banner = pyfiglet.figlet_format("FSR - SHIELD", font="slant")
    console.print(f"[bold white]{ascii_banner}[/bold white]")
    console.print("--- AMD FidelityFX Deployment Utility | Version 1.0 --- \n")


def select_game():
    """Displays supported games in a minimal table."""
    table = Table(show_header=True, header_style="bold white", box=None)
    table.add_column("ID", width=4)
    table.add_column("TARGET GAME")

    # Map numbers to game keys for easy selection
    game_list = list(SUPPORTED_GAMES.keys())
    for index, key in enumerate(game_list, start=1):
        table.add_row(str(index), SUPPORTED_GAMES[key].name)

    console.print(table)
    console.print("-" * 30)

    choice = console.input("[bold]Enter ID (or 'q' to quit): [/bold]")

    if choice.lower() == "q":
        sys.exit(0)

    try:
        selected_index = int(choice) - 1
        if 0 <= selected_index < len(game_list):
            return game_list[selected_index]
        else:
            console.print("[red][!] Invalid selection.[/red]")
            sys.exit(1)
    except ValueError:
        console.print("[red][!] Input must be numeric.[/red]")
        sys.exit(1)


def run_fsr_shield():
    """Main execution flow with industrial log style and confirmation prompts."""
    # Clear terminal for professional look
    os.system("cls" if os.name == "nt" else "clear")
    render_banner()

    # 1. User selects the game
    game_key = select_game()
    game_cfg = SUPPORTED_GAMES[game_key]

    console.print(f"\n[bold]Selected Target:[/bold] {game_cfg.name}")
    console.print("-" * 50)

    # 2. Find Installation Path
    console.print(f"[*] Locating {game_cfg.name} in Steam libraries...")
    target_dir = find_steam_game_path(game_cfg)

    if not target_dir:
        console.print(f"[red][!] Error: Could not find installation directory.[/red]")
        return

    console.print(f"[green][+][/green] Path verified: {target_dir}")

    # 3. Fetch Latest Release Info from GitHub
    repo = "GPUOpen-LibrariesAndSDKs/FidelityFX-SDK"
    console.print(f"[*] Querying GitHub API: {repo}...")
    release_info = get_latest_release_info(repo)

    if release_info is None:
        console.print("[red][!] Error: Connection to GitHub failed.[/red]")
        return

    # Determine asset (Priority for 'minimal' package, fallback to source)
    assets = release_info.get("assets", [])
    asset = next((a for a in assets if "minimal" in a["name"].lower()), None)

    if asset:
        download_url = asset["browser_download_url"]
        asset_name = asset["name"]
    else:
        # Fallback for the "Minimal package" zipball from the HTML
        download_url = release_info.get("zipball_url")
        asset_name = f"SDK-Source-{release_info.get('tag_name')}.zip"

    if not download_url:
        console.print("[red][!] Error: No suitable SDK package found.[/red]")
        return

    temp_zip = "fsr_sdk_temp.zip"

    # 4. Download Process
    console.print(f"[*] Fetching: {asset_name}")
    if download_file(download_url, temp_zip):

        # 5. Security & Integrity Check
        console.print("[*] Verifying SHA-256 integrity...")
        _, actual_hash = verify_file(temp_zip, "")

        if is_hash_trusted(actual_hash):
            console.print("[green][+][/green] Integrity Verified: Trusted Signature.")

            # 6. Extraction & Version Detection
            extracted_folder = "extracted_dlls"
            # Unpack both the file list and the detected version string
            extracted_files, version = extract_specific_dlls(temp_zip, extracted_folder)

            console.print(f"[*] Detected SDK Version: [bold cyan]{version}[/bold cyan]")
            console.print("-" * 50)

            # 7. Final Confirmation Prompt
            confirm_msg = (
                f"Ready to update {game_cfg.name} with FSR {version}. Proceed?"
            )
            if Confirm.ask(confirm_msg):

                # 8. Deployment and Backup
                console.print("[*] Creating backup and deploying DLLs...")
                success, result = deploy_to_game(extracted_folder, target_dir)

                if success:
                    console.print("-" * 50)
                    console.print("[bold green]DEPLOYMENT SUCCESSFUL[/bold green]")
                    console.print(f"Target: {game_cfg.name}")
                    console.print(f"Backup created in: {result}")
                    console.print("-" * 50)
                else:
                    console.print(f"[red][!] Deployment failed: {result}[/red]")
            else:
                console.print(
                    "[yellow][!] Deployment cancelled. No files were changed.[/yellow]"
                )
        else:
            # Alert for untrusted file hashes
            console.print("\n" + "!" * 50)
            console.print(f"[bold red]SECURITY ALERT: UNTRUSTED HASH[/bold red]")
            console.print(f"Hash: {actual_hash}")
            console.print("!" * 50 + "\n")

        # Cleanup temporary files
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
    else:
        console.print("[red][!] Error: Download failed.[/red]")


if __name__ == "__main__":
    try:
        run_fsr_shield()
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Operation aborted by user.[/yellow]")
        sys.exit(0)
