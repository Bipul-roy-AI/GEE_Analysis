from pathlib import Path
import pytest
from tools.prepare_tutorial_queue import prepare


def test_legacy_update_preserves_outputs_and_is_repeatable(tmp_path):
    (tmp_path/'themes/water').mkdir(parents=True)
    (tmp_path/'tools').mkdir()
    source=tmp_path/'themes/water/example.js'
    before=b"// example\r\nvar crs='EPSG:6933';\r\n"
    source.write_bytes(before)
    (tmp_path/'tools/js_header.txt').write_bytes(before)
    (tmp_path/'outputs').mkdir()
    state=tmp_path/'outputs/climate_test_state.json';state.write_text('completed')
    assert prepare(tmp_path)==2
    assert source.read_bytes()==before.replace(b'6933',b'4326')
    assert state.read_text()=='completed'
    backups=list((tmp_path/'outputs').glob('before_tutorial_crs_*/themes/water/example.js'))
    assert len(backups)==1 and backups[0].read_bytes()==before
    assert prepare(tmp_path)==0


def test_refuses_to_modify_an_existing_tutorial_run(tmp_path):
    (tmp_path/'outputs').mkdir()
    (tmp_path/'outputs/tutorials_state.json').write_text('{}')
    with pytest.raises(RuntimeError,match='already exists'):prepare(tmp_path)
