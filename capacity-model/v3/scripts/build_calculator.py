"""Build the single-file calculator (index.html) from the template, aggregated data and config.

Run after scripts/build_inputs.py:
  python scripts/build_calculator.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def flatten(cfg):
    globals_flat = {k: v["value"] for k, v in cfg["globals"].items()}
    org = {k: v for k, v in cfg["org_chart"].items() if not k.startswith("_")}
    return {
        "globals": globals_flat,
        "profiles": cfg["profiles"],
        "org_chart": org,
    }


def main():
    data = json.loads((ROOT / "data" / "team_book.json").read_text())
    cfg = flatten(json.loads((ROOT / "config" / "profiles.json").read_text()))
    tpl = (ROOT / "calculator.template.html").read_text()
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    html = html.replace("/*__CONFIG__*/null", json.dumps(cfg, separators=(",", ":")))
    assert "__DATA__" not in html and "__CONFIG__" not in html
    out = ROOT / "index.html"
    out.write_text(html)
    print("wrote", out, f"{out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
