from pathlib import Path

import pytest

from dockyard_audit.config import ComposeConfigError, load_compose


def test_load_compose(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text("services:\n  web:\n    image: nginx:1.27\n", encoding="utf-8")
    assert "web" in load_compose(file)["services"]


def test_rejects_empty_document(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text("", encoding="utf-8")
    with pytest.raises(ComposeConfigError, match="empty"):
        load_compose(file)


def test_rejects_missing_services(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text("name: sample\n", encoding="utf-8")
    with pytest.raises(ComposeConfigError, match="services"):
        load_compose(file)


def test_rejects_non_mapping_service(tmp_path: Path):
    file = tmp_path / "compose.yml"
    file.write_text("services:\n  web: nginx\n", encoding="utf-8")
    with pytest.raises(ComposeConfigError, match="mapping"):
        load_compose(file)


def test_missing_file_is_actionable(tmp_path: Path):
    with pytest.raises(ComposeConfigError, match="does not exist"):
        load_compose(tmp_path / "missing.yml")
