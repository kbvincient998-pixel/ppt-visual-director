#!/usr/bin/env python3
"""Compare media-sensitive structures between a source and edited PPTX."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
PROTECTED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".avi",
    ".mp3",
    ".m4a",
    ".wav",
    ".wmv",
}


def signature(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        slides = sorted(name for name in names if SLIDE_RE.fullmatch(name))
        media = {}
        for name in sorted(item for item in names if item.startswith("ppt/media/")):
            payload = archive.read(name)
            media[Path(name).name] = {
                "size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        animations, transitions = [], []
        for name in slides:
            number = int(SLIDE_RE.fullmatch(name).group(1))
            root = ET.fromstring(archive.read(name))
            if root.find(".//p:timing", NS) is not None:
                animations.append(number)
            if root.find(".//p:transition", NS) is not None:
                transitions.append(number)
        return {
            "slides": len(slides),
            "media": media,
            "animations": animations,
            "transitions": transitions,
            "macros": sorted(name for name in names if name.lower().endswith("vbaproject.bin")),
            "embeddings": sorted(name for name in names if name.startswith("ppt/embeddings/")),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--strict-all-media",
        action="store_true",
        help="also fail when ordinary image assets are missing or changed",
    )
    args = parser.parse_args()
    source = signature(args.source)
    candidate = signature(args.candidate)

    source_media = set(source["media"])
    candidate_media = set(candidate["media"])
    missing_media = sorted(source_media - candidate_media)
    changed_media = sorted(
        name
        for name in source_media & candidate_media
        if source["media"][name] != candidate["media"][name]
    )
    protected = {
        name for name in source_media if Path(name).suffix.lower() in PROTECTED_EXTENSIONS
    }
    missing_protected = sorted(protected - candidate_media)
    changed_protected = sorted(
        name
        for name in protected & candidate_media
        if source["media"][name] != candidate["media"][name]
    )
    report = {
        "source": str(args.source.resolve()),
        "candidate": str(args.candidate.resolve()),
        "source_slides": source["slides"],
        "candidate_slides": candidate["slides"],
        "missing_media": missing_media,
        "changed_media": changed_media,
        "missing_protected_media": missing_protected,
        "changed_protected_media": changed_protected,
        "missing_animation_slides": sorted(set(source["animations"]) - set(candidate["animations"])),
        "missing_transition_slides": sorted(set(source["transitions"]) - set(candidate["transitions"])),
        "missing_macros": sorted(set(source["macros"]) - set(candidate["macros"])),
        "missing_embeddings": sorted(set(source["embeddings"]) - set(candidate["embeddings"])),
    }
    failures = [
        source["slides"] != candidate["slides"],
        bool(report["missing_media"] if args.strict_all_media else report["missing_protected_media"]),
        bool(report["changed_media"] if args.strict_all_media else report["changed_protected_media"]),
        bool(report["missing_animation_slides"]),
        bool(report["missing_transition_slides"]),
        bool(report["missing_macros"]),
        bool(report["missing_embeddings"]),
    ]
    report["status"] = "FAIL" if any(failures) else "PASS"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(failures) else 0


if __name__ == "__main__":
    raise SystemExit(main())
