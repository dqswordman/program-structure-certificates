"""Build the offline public edition around the original v1.0.0 scientific snapshot."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TAG = "v1.0.0"
FROZEN = "8b0f2e0dd17ee36ce9233a9053dc55c22110dfce"
NAME = "program-structure-certificates-" + TAG
ADDITIONS = ("LICENSE", "licenses/CC-BY-4.0.txt", "PUBLICATION.md", "docs/companion.json",
             "docs/report.en.md", "docs/report.zh.md")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main(destination):
    commit = git("rev-parse", f"{TAG}^{{commit}}").decode().strip()
    if commit != FROZEN:
        raise ValueError("Unexpected scientific revision")
    with zipfile.ZipFile(io.BytesIO(git("archive","--format=zip",FROZEN))) as baseline:
        members = {item.filename: baseline.read(item) for item in baseline.infolist() if not item.is_dir()}
    edition = git("rev-parse","HEAD").decode().strip()
    digests = {}
    for name in ADDITIONS:
        if name in members:
            raise ValueError(f"Publication file would replace a scientific source: {name}")
        members[name] = git("show",f"{edition}:{name}")
        digests[name] = hashlib.sha256(members[name]).hexdigest()
    record = {"tag":TAG,"scientific_commit":FROZEN,"publication_commit":edition,
              "paper":"https://arxiv.org/abs/2611.24975v1","additions_sha256":digests}
    members["PUBLICATION_MANIFEST.json"] = (json.dumps(record,indent=2)+"\n").encode()
    data = io.BytesIO()
    with zipfile.ZipFile(data,"w") as archive:
        for path,content in sorted(members.items()):
            entry = zipfile.ZipInfo(f"{NAME}/{path}", (2026,11,20,0,0,0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    blob = data.getvalue()
    if len(blob)>100_000_000:
        raise ValueError("Main ZIP exceeds 100,000,000 bytes")
    with zipfile.ZipFile(io.BytesIO(blob)) as check:
        if check.testzip() or len(check.namelist()) != len(members):
            raise ValueError("ZIP member verification failed")
        for path,expected in members.items():
            if check.read(f"{NAME}/{path}") != expected:
                raise ValueError(f"ZIP differs: {path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(blob)
    print(json.dumps({"name":destination.name,"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest(),**record},indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination",type=Path)
    main(parser.parse_args().destination)
