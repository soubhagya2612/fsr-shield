import pytest
import os
from src.installer import deploy_to_game


def test_deployment_with_backup_and_mapping(tmp_path):
    """Test that files are backed up AND the loader is renamed correctly."""

    # 1. Setup fake game directory with an "old" loader (standard name)
    game_dir = tmp_path / "game_folder"
    game_dir.mkdir()
    old_loader = game_dir / "amd_fidelityfx_dx12.dll"
    old_loader.write_bytes(b"old_loader_data")

    # 2. Setup source folder with the NEW SDK loader (new name)
    source_dir = tmp_path / "extracted"
    source_dir.mkdir()
    new_loader_source = source_dir / "amd_fidelityfx_loader_dx12.dll"
    new_loader_source.write_bytes(b"new_loader_data")

    # Add the upscaler too for a complete test
    new_upscaler_source = source_dir / "amd_fidelityfx_upscaler_dx12.dll"
    new_upscaler_source.write_bytes(b"new_upscaler_data")

    # 3. Run deployment
    success, result_path = deploy_to_game(str(source_dir), str(game_dir))

    # 4. Assertions
    backup_folder = game_dir / "fsr_shield_backup"

    assert success is True

    # Check if the OLD loader was backed up under its ORIGINAL name
    assert (backup_folder / "amd_fidelityfx_dx12.dll").exists()
    assert (
        backup_folder / "amd_fidelityfx_dx12.dll"
    ).read_bytes() == b"old_loader_data"

    # Check if the NEW loader was renamed correctly in the game folder
    deployed_loader = game_dir / "amd_fidelityfx_dx12.dll"
    assert deployed_loader.exists()
    assert deployed_loader.read_bytes() == b"new_loader_data"

    # Ensure the loader wasn't just copied with its old name
    assert not (game_dir / "amd_fidelityfx_loader_dx12.dll").exists()
