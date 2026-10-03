from pathlib import Path
import hashlib
import json
import urllib.request

name = "malecns_v1"
registry = json.loads(Path("doom/datasets.json").read_text())["datasets"][name]
locked = json.loads(
    Path(f"data-provenance/{name}/source.lock.json").read_text()
)
root = Path("connectome_data") / name
root.mkdir(parents=True, exist_ok=True)

for filename, url in registry["files"].items():
    target = root / filename
    if not target.exists():
        partial = target.with_suffix(".download")
        print(f"Downloading {filename}", flush=True)
        urllib.request.urlretrieve(url, partial)
        partial.replace(target)

    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()

    if digest != locked[filename]["sha256"]:
        raise RuntimeError(f"Checksum mismatch: {filename}")
    print(f"Verified {filename}", flush=True)

(root / "source.lock.json").write_text(
    json.dumps(locked, indent=2) + "\n"
)
