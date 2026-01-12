import requests
from rich.progress import Progress


def get_latest_release_info(repo_url):
    """
    Fetches the latest release information from the GitHub API.
    Example repo_url: "GPUOpen-LibrariesAndSDKs/FidelityFX-SDK"
    """
    api_url = f"https://api.github.com/repos/{repo_url}/releases/latest"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def download_file(url, dest_path):
    """
    Downloads a file, handling cases where Content-Length is missing.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # GitHub zipballs often return None for content-length
        total_size = response.headers.get("content-length")
        if total_size is not None:
            total_size = int(total_size)

        with Progress() as progress:
            # If total_size is None, the bar will 'pulse' instead of showing 0%
            task = progress.add_task("[cyan]Downloading...", total=total_size)

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        return True
    except Exception as e:
        return False
