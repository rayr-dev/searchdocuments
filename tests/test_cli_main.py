# tests/test_cli_main.py

import sys
import pytest

from unittest.mock import patch
from src.cli.cli_main import build_parser, run_cli

@pytest.fixture(autouse=True)
def patch_version_info():
    """Patch get_version_info so build_parser works without app_version.json."""
    with patch("src.utilities.path_utils.get_version_info",
               return_value={
                   "version": "1.0.0",
                   "build": "20260302",
                   "author": "Test",
                   "description": "Test",
                   "release": "Test"
               }):
        yield
# -----------------------------
# Helper to simulate CLI args
# -----------------------------
def make_args(folderA="src", folderB="src", output="src",
              hash=False, hashonly=False, findall=False,
              dryrun=False, deletematches=False,
              deletecandidates=False, quarantine=False,
              diag=False):
    """Build a sys.argv list for testing."""
    args = ["cli_main.py", folderA, folderB, "-o", output]
    if hash:
        args.append("--hash")
    if hashonly:
        args.append("--hashonly")
    if findall:
        args.append("--findall")
    if dryrun:
        args.append("--dryrun")
    if deletematches:
        args.append("--deletematches")
    if deletecandidates:
        args.append("--deletecandidates")
    if quarantine:
        args.append("--quarantine")
    if diag:
        args.append("--diag")
    return args

# -----------------------------
# build_parser tests
# -----------------------------
def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None

def test_build_parser_parses_folderA():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output"])
    assert args.folderA == "pathA"

def test_build_parser_parses_folderB():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output"])
    assert args.folderB == "pathB"

def test_build_parser_parses_output():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output"])
    assert args.output == "output"

def test_build_parser_output_required():
    """Output argument is required — should fail without it."""
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["pathA", "pathB"])

def test_build_parser_hash_flag_default_false():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output"])
    assert not args.hash

def test_build_parser_hash_flag_true():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--hash"])
    assert args.hash

def test_build_parser_hashonly_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--hashonly"])
    assert args.hashonly

def test_build_parser_findall_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--findall"])
    assert args.findall

def test_build_parser_dryrun_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--dryrun"])
    assert args.dryrun

def test_build_parser_deletematches_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--deletematches"])
    assert args.deletematches

def test_build_parser_deletecandidates_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--deletecandidates"])
    assert args.deletecandidates

def test_build_parser_quarantine_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--quarantine"])
    assert args.quarantine

def test_build_parser_diag_flag():
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output", "--diag"])
    assert args.diag

def test_build_parser_version_flag(capsys):
    """--version should print version string and exit."""
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Search Documents Tool" in captured.out
    assert "v1.0.0" in captured.out
    assert "Build:" in captured.out

def test_build_parser_all_flags_default_false():
    """All optional flags should default to False."""
    parser = build_parser()
    args = parser.parse_args(["pathA", "pathB", "-o", "output"])
    assert not args.hash
    assert not args.hashonly
    assert not args.findall
    assert not args.dryrun
    assert not args.deletematches
    assert not args.deletecandidates
    assert not args.quarantine
    assert not args.diag

# -----------------------------
# run_cli config mapping tests
# -----------------------------
PATCH_RECONCILE = "src.cli.cli_main.run_reconciliation"
PATCH_LOGGING   = "src.cli.cli_main.init_logging"
PATCH_INIT      = "src.cli.cli_main.config.initialize_runtime"

def test_run_cli_sets_hash_only_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  hashonly=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT,      return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.HASH_ONLY_MODE

def test_run_cli_sets_hash_compare_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  hash=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.HASH_COMPARE_MODE

def test_run_cli_sets_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  dryrun=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.DRY_RUN

def test_run_cli_sets_find_all(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  findall=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.FIND_ALL_LOCATIONS_MODE

def test_run_cli_sets_delete_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  deletematches=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.DELETE_EXACT_MATCHES

def test_run_cli_sets_delete_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  deletecandidates=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.DELETE_CANDIDATES

def test_run_cli_sets_quarantine(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  quarantine=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.USE_QUARANTINE

def test_run_cli_sets_diagnostic_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path),
                                  diag=True))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")), \
         patch(PATCH_INIT, return_value=None):
        run_cli()
    import src.cli.cli_main as cli_mod
    assert cli_mod.config.DIAGNOSTIC_MODE

def test_run_cli_calls_reconciliation(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path)))
    with patch(PATCH_RECONCILE,
               return_value=({}, "summary")) as mock_reconcile, \
         patch(PATCH_LOGGING,
               return_value=str(tmp_path / "test.log")):
        run_cli()
    assert mock_reconcile.called

def test_run_cli_passes_correct_folders(tmp_path, monkeypatch):
    import os
    folderA = str(tmp_path / "source")
    folderB = str(tmp_path / "target")
    output  = str(tmp_path / "output")
    os.makedirs(output)
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=folderA,
                                  folderB=folderB,
                                  output=output))
    with patch(PATCH_RECONCILE,
               return_value=({}, "summary")) as mock_reconcile, \
         patch(PATCH_LOGGING,
               return_value=str(tmp_path / "test.log")):
        run_cli()
    args, kwargs = mock_reconcile.call_args
    assert args[0] == folderA
    assert args[1] == folderB
    assert args[2].startswith(output)

# -----------------------------
# Error handling tests
# -----------------------------
def test_run_cli_exits_on_reconciliation_error(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path)))
    with patch(PATCH_RECONCILE,
               side_effect=Exception("Something went wrong")), \
         patch(PATCH_LOGGING,
               return_value=str(tmp_path / "test.log")), \
         pytest.raises(SystemExit) as exc_info:
        run_cli()
    assert exc_info.value.code == 1

def test_run_cli_prints_summary(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=str(tmp_path),
                                  folderB=str(tmp_path),
                                  output=str(tmp_path)))
    with patch(PATCH_RECONCILE,
               return_value=({}, "Summary output here")), \
         patch(PATCH_LOGGING,
               return_value=str(tmp_path / "test.log")):
        run_cli()
    captured = capsys.readouterr()
    assert "Summary output here" in captured.out


def test_cli_main_entry_point():
    """Test that __main__ block exists and calls run_cli."""
    import ast
    source = open("src/cli/cli_main.py",encoding="utf-8").read()
    tree = ast.parse(source)

    # Find if __name__ == "__main__": run_cli() exists
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check for if __name__ == "__main__":
            test = node.test
            if (isinstance(test, ast.Compare) and
                    isinstance(test.left, ast.Name) and
                    test.left.id == "__name__"):
                # Check body contains run_cli()
                for stmt in node.body:
                    if (isinstance(stmt, ast.Expr) and
                            isinstance(stmt.value, ast.Call) and
                            isinstance(stmt.value.func, ast.Name) and
                            stmt.value.func.id == "run_cli"):
                        found = True

    assert found, "cli_main.py missing if __name__ == '__main__': run_cli()"
def test_run_cli_creates_output_folder_if_missing(tmp_path, monkeypatch):
    """CLI should create output folder if it does not exist."""
    import os
    folderA = str(tmp_path / "source")
    folderB = str(tmp_path / "target")
    output  = str(tmp_path / "new_output")  # ← does not exist yet
    os.makedirs(folderA)
    os.makedirs(folderB)

    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=folderA,
                                  folderB=folderB,
                                  output=output))
    with patch(PATCH_RECONCILE, return_value=({}, "summary")), \
         patch(PATCH_LOGGING,   return_value=str(tmp_path / "test.log")):
        run_cli()

    assert os.path.isdir(output)  # ← folder was created


def test_run_cli_exits_if_output_folder_cannot_be_created(tmp_path, monkeypatch):
    """CLI should print error and exit if output folder cannot be created."""
    import os
    folderA = str(tmp_path / "source")
    folderB = str(tmp_path / "target")
    output  = str(tmp_path / "new_output")
    os.makedirs(folderA)
    os.makedirs(folderB)

    monkeypatch.setattr(sys, "argv",
                        make_args(folderA=folderA,
                                  folderB=folderB,
                                  output=output))

    with patch("src.cli.cli_main.os.makedirs",
               side_effect=OSError("Permission denied")), \
         pytest.raises(SystemExit) as exc_info:
        run_cli()

    assert exc_info.value.code == 1
