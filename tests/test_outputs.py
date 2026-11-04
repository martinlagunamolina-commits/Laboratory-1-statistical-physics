"""Verify exported results, literal-vs-centered ratios, and benchmark workloads."""
import csv
import json
from math import comb, isclose, log
import main
from benchmark import worker


def test_group_exports_and_all_microstates(tmp_path, monkeypatch):
    monkeypatch.setattr(main,"RESULTS",tmp_path)
    monkeypatch.setattr(main,"REPORT",tmp_path)
    main.generate_microstates()
    with (tmp_path/"microstates_N7.csv").open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==128
    assert len({r['microstate'] for r in rows})==128
    for row in rows:
        assert row['microstate'].count('H')==int(row['heads'])
    main.generate_group_results([71,71,71,71],"nearest")
    data=json.loads((tmp_path/"group_results.json").read_text())
    assert data['N']==171
    assert data['center']==85
    assert data['likelihood_states']==[61,81]
    assert isclose(data['P30'],comb(171,30)/(1<<171),rel_tol=1e-11)
    assert isclose(data['Pwithin10'],sum(comb(171,k) for k in range(76,96))/(1<<171),rel_tol=1e-11)
    assert isclose(data['likelihood_log_ratios'][0],log(comb(171,85))-log(comb(171,61)),abs_tol=1e-10)
    assert data['deltaS_e_J_per_K']<0<data['deltaS_g_J_per_K']
    # M<10 makes the literal M-10 state invalid; do not clamp it silently.
    main.generate_group_results([1],"nearest")
    data=json.loads((tmp_path/"group_results.json").read_text())
    assert data['likelihood_log_ratios'][0] is None
    main.generate_group_results(None,"nearest")
    assert json.loads((tmp_path/"group_results.json").read_text())['status']=='pending_NIA_suffixes'


def test_isolated_enumeration_worker():
    row=worker("enumeration",10)
    assert row['N']==10
    assert row['seconds']>0
    assert row['peak_rss_mib']>0
    assert row['retained_bytes']==0

def test_failed_benchmark_can_be_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "RESULTS", tmp_path)
    monkeypatch.setattr(main, "REPORT", tmp_path)
    data = {"rows": [{"N": 20, "status": "failed", "error": "worker failed"}],
            "per_run_timeout_seconds": 300, "platform": "test_platform"}
    (tmp_path / "enumeration_benchmark.json").write_text(json.dumps(data))
    main.generate_benchmark_tables()
    assert "failed" in (tmp_path / "enumeration_benchmark.tex").read_text()