"""Verify that the live site serves this commit and the complete checked artifact."""

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import time
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from build_site import normalize_url


def fetch(url):
    request = Request(url, headers={"User-Agent": "PortfolioDeploymentCheck/1.0", "Cache-Control": "no-cache"})
    try:
        with urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError(f"Unexpected HTTP status {response.status} for {url}")
            return response.read()
    except HTTPError as error:
        raise ValueError(f"HTTP {error.code} for {url}") from error


def verify(url, commit, fetcher=fetch):
    url = normalize_url(url)
    suffix = "?deployment=" + quote(commit, safe="")
    manifest = json.loads(fetcher(url + "build-info.json" + suffix))
    if manifest.get("generator") != "kumar-portfolio" or manifest.get("commit") != commit:
        raise ValueError("Live deployment has not reached the requested commit")
    files = manifest.get("files", {})
    if "index.html" not in files or len(files) < 3:
        raise ValueError("Live deployment manifest is incomplete")
    for name, expected in files.items():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or ":" in name or "\\" in name:
            raise ValueError("Unexpected path in deployment manifest")
        data = fetcher(url + quote(name, safe="/") + suffix)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Live asset differs from the checked artifact: {name}")
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    for attempt in range(1, 13):
        try:
            count = verify(args.url, args.commit)
            print(f"PASS: live commit {args.commit}, {count} assets verified at {args.url}")
            return
        except Exception as error:
            print(f"Attempt {attempt}/12: {error}")
            if attempt == 12:
                raise SystemExit("Deployment verification failed. Inspect the run before reporting success.")
            time.sleep(5)


if __name__ == "__main__":
    main()
