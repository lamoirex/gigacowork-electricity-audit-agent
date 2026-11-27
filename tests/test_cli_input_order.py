import pytest

from testdata.scenarios.foreign_format import generate
from tests._helpers import load_engine


def test_cli_rejects_swapped_inputs(tmp_path, capsys):
    generate(tmp_path)
    engine = load_engine()
    output = tmp_path / "result"
    with pytest.raises(SystemExit) as error:
        engine.main(
            [
                str(tmp_path / "norms_foreign.xlsx"),
                str(tmp_path / "charges_foreign.xlsx"),
                str(tmp_path / "stores_foreign.xlsx"),
                str(output),
            ]
        )
    assert error.value.code == 2
    assert "нет обязательных колонок" in capsys.readouterr().err
    assert not output.exists()
