import socket
import time

import numpy as np
import pytest
from pydicom import dcmread
from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage, RTStructureSetStorage

from oar_contour.dicom_node import Destination, NodeConfig, OarNode
from oar_contour.evaluate import compare_rtstructs, hd95
from oar_contour.pipeline import run_pipeline

from conftest import FakeSegmenter, thorax_labels


def test_hd95_known_shift():
    a = np.zeros((40, 40, 40), bool)
    a[10:30, 10:30, 10:30] = True
    b = np.roll(a, 2, axis=0)
    assert hd95(a, a, (1, 1, 1)) == 0
    assert hd95(a, b, (2.0, 1, 1)) == pytest.approx(4.0, abs=0.01)


def test_compare_identical_rtstruct(ct_dir, tmp_path):
    out = tmp_path / "rs.dcm"
    run_pipeline(ct_dir, out, FakeSegmenter(thorax_labels()), site="thorax")
    metrics = {m.name: m for m in compare_rtstructs(ct_dir, out, out)}
    assert metrics["Heart"].dice == 1.0
    assert metrics["Heart"].hd95_mm == 0.0
    assert metrics["Lung_L"].volume_ratio == pytest.approx(1.0)


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_node_receives_ct_and_forwards_rtstruct(ct_dir, tmp_path):
    # "Monaco" giả: nhận RTSTRUCT
    received = []

    def on_store(event):
        received.append(event.dataset)
        return 0x0000

    tps = AE(ae_title="FAKE_TPS")
    tps.add_supported_context(RTStructureSetStorage)
    tps_port = _free_port()
    tps_server = tps.start_server(("127.0.0.1", tps_port), block=False,
                                  evt_handlers=[(evt.EVT_C_STORE, on_store)])

    port = _free_port()
    node = OarNode(
        NodeConfig(port=port, work_dir=tmp_path / "work", settle_seconds=1,
                   ae_site={"OAR_THX": "thorax"},
                   forward=Destination("127.0.0.1", tps_port, "FAKE_TPS")),
        FakeSegmenter(thorax_labels()),
    )
    node.start(block=False)
    try:
        # CT-sim giả gửi series tới AE OAR_THX
        scu = AE(ae_title="CTSIM")
        scu.add_requested_context(CTImageStorage)
        assoc = scu.associate("127.0.0.1", port, ae_title="OAR_THX")
        assert assoc.is_established
        for f in sorted(ct_dir.iterdir()):
            assert assoc.send_c_store(dcmread(f)).Status == 0
        assoc.release()

        deadline = time.monotonic() + 60
        while not received and time.monotonic() < deadline:
            time.sleep(0.2)
    finally:
        node.stop()
        tps_server.shutdown()

    assert len(received) == 1
    rs = received[0]
    assert rs.Modality == "RTSTRUCT"
    names = {r.ROIName for r in rs.StructureSetROISequence}
    assert {"Lung_L", "Lung_R", "Heart", "Breast_L"} <= names
    # CT đã xoá sau khi xử lý xong (mặc định)
    assert not any((tmp_path / "work" / "incoming").iterdir())


def test_preview_png(ct_dir, tmp_path):
    from oar_contour.preview import render_preview

    out = tmp_path / "rs.dcm"
    run_pipeline(ct_dir, out, FakeSegmenter(thorax_labels()), site="thorax")
    png = render_preview(ct_dir, out, tmp_path / "p.png")
    assert png.stat().st_size > 10_000
