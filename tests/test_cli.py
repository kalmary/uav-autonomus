import json

import pytest

from src.__main__ import main


def test_prints_config(monkeypatch, capsys, tmp_path) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text("lidar_beams: 3\n")
    monkeypatch.setattr("sys.argv", ["uav-planner", "--config", str(path)])
    main()
    output = json.loads(capsys.readouterr().out)
    assert output["lidar_beams"] == 3
    assert output["lidar_range_m"] == 10.0


def test_prints_defaults(monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["uav-planner"])
    main()
    assert json.loads(capsys.readouterr().out)["lidar_beams"] == 1


@pytest.mark.parametrize("content", ["lidar_beams: 0", "lidar_beams: [", "unknown: 1"])
def test_reports_invalid_config(monkeypatch, capsys, tmp_path, content) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text(content)
    monkeypatch.setattr("sys.argv", ["uav-planner", "--config", str(path)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    output = capsys.readouterr()
    assert "error:" in output.err
    assert not output.out


def test_reports_missing_file(monkeypatch, capsys, tmp_path) -> None:
    path = tmp_path / "missing.yaml"
    monkeypatch.setattr("sys.argv", ["uav-planner", "--config", str(path)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("preplan", [True, False])
@pytest.mark.parametrize("override", [None, "--preplan", "--no-preplan"])
def test_preplan_cli_overrides_yaml(monkeypatch, capsys, tmp_path, preplan, override) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text(f"preplan: {str(preplan).lower()}\n")
    args = ["uav-planner", "--config", str(path)]
    if override:
        args.append(override)
    monkeypatch.setattr("sys.argv", args)
    main()
    expected = preplan if override is None else override == "--preplan"
    assert json.loads(capsys.readouterr().out)["preplan"] is expected


@pytest.mark.parametrize("flag", ["--preplan", "--no-preplan"])
def test_preplan_cli_without_config(monkeypatch, capsys, flag) -> None:
    monkeypatch.setattr("sys.argv", ["uav-planner", flag])
    main()
    assert json.loads(capsys.readouterr().out)["preplan"] is (flag == "--preplan")
