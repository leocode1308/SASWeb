import requests
from pathlib import Path

def download_to_local(url: str, out_path: Path, parent_mkdir: bool = True):
    if not isinstance(out_path, Path):
        raise ValueError(f"{out_path} must be a Path object")
    
    if parent_mkdir:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        out_path.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False