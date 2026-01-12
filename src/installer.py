import os
import shutil
import zipfile
import pefile

# The files we look for in the SDK ZIP
# Now includes the loader which is vital for SDK 2.1
SOURCE_DLLS = [
    "amd_fidelityfx_upscaler_dx12.dll",
    "amd_fidelityfx_framegeneration_dx12.dll",
    "amd_fidelityfx_loader_dx12.dll",
]

# Mapping for deployment: Translates SDK names to Game names
FILE_MAPPING = {
    "amd_fidelityfx_upscaler_dx12.dll": "amd_fidelityfx_upscaler_dx12.dll",
    "amd_fidelityfx_framegeneration_dx12.dll": "amd_fidelityfx_framegeneration_dx12.dll",
    "amd_fidelityfx_loader_dx12.dll": "amd_fidelityfx_dx12.dll",  # Renames loader to main DLL
}


def get_dll_version(file_path):
    """Reads the internal Product Version from the DLL metadata."""
    try:
        pe = pefile.PE(file_path)
        for fileinfo in pe.FileInfo[0]:
            if fileinfo.Key.decode() == "StringFileInfo":
                for st in fileinfo.StringTable:
                    for entry in st.entries.items():
                        if entry[0].decode() == "ProductVersion":
                            return entry[1].decode()
        return "Unknown Version"
    except Exception:
        return "Metadata Unreadable"


def extract_specific_dlls(zip_path, extract_to="temp_dlls"):
    """Extracts DLLs and detects version from the upscaler."""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    extracted_files = []
    detected_version = "Unknown"

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            file_name = os.path.basename(file_info.filename)

            # Check against our SOURCE_DLLS list
            if file_name.lower() in SOURCE_DLLS:
                target_path = os.path.join(extract_to, file_name)
                with zip_ref.open(file_info) as source, open(
                    target_path, "wb"
                ) as target:
                    shutil.copyfileobj(source, target)

                extracted_files.append(target_path)

                # Use the upscaler to identify the SDK version
                if file_name.lower() == "amd_fidelityfx_upscaler_dx12.dll":
                    detected_version = get_dll_version(target_path)

    return extracted_files, detected_version


def deploy_to_game(source_folder, destination_path):
    """Creates a backup of existing DLLs before deploying and renaming new ones."""
    try:
        if not os.path.exists(destination_path):
            return False, "Target directory does not exist."

        backup_dir = os.path.join(destination_path, "fsr_shield_backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Use the Mapping to ensure files are renamed correctly for the game engine
        for sdk_name, game_name in FILE_MAPPING.items():
            new_file_source = os.path.join(source_folder, sdk_name)
            existing_game_file = os.path.join(destination_path, game_name)

            if os.path.exists(new_file_source):
                # Backup the file that is about to be replaced
                if os.path.exists(existing_game_file):
                    shutil.copy2(existing_game_file, backup_dir)

                # Copy and rename to the target filename
                target_destination = os.path.join(destination_path, game_name)
                shutil.copy2(new_file_source, target_destination)

        return True, backup_dir
    except PermissionError:
        return False, "Access Denied. Please run as Administrator."
    except Exception as e:
        return False, str(e)
