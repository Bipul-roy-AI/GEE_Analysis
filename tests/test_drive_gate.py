from unittest.mock import MagicMock
import pytest
from bdgee.batch import LiveBackend


def backend(files):
    b=LiveBackend.__new__(LiveBackend)
    b.drive=MagicMock();b.poll=0;b.folder=lambda _:'folder-id'
    b.drive.files().list().execute.return_value={'files':files}
    return b


def task():return {'config':{'fileExportOptions':{'fileFormat':'CSV','driveDestination':{'folder':'BD_GEE_test','filenamePrefix':'unique_1'}}}}


def test_drive_requires_correct_file_not_prefix_collision():
    b=backend([{'id':'one','name':'unique_1.csv','size':'12'}, {'id':'other','name':'unique_10.csv','size':'20'}])
    assert [f['id'] for f in b.verify_export(task())]==['one']


def test_missing_or_empty_outputs_cannot_pass(monkeypatch):
    import bdgee.batch as module
    for files in [[],[{'id':'empty','name':'unique_1.csv','size':'0'}]]:
        clock=iter([0,601]);monkeypatch.setattr(module.time,'monotonic',lambda:next(clock))
        with pytest.raises(RuntimeError,match='Drive files'):backend(files).verify_export(task())


def test_multipart_export_rejects_any_empty_shard(monkeypatch):
    import bdgee.batch as module
    clock=iter([0,601]);monkeypatch.setattr(module.time,'monotonic',lambda:next(clock))
    t=task();t['config']['fileExportOptions']['fileFormat']='GEO_TIFF'
    b=backend([{'id':'a','name':'unique_1-000000-000000.tif','size':'8'}, {'id':'b','name':'unique_1-000000-000001.tif','size':'0'}])
    with pytest.raises(RuntimeError):b.verify_export(t)
