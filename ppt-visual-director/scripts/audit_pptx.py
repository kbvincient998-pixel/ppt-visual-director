#!/usr/bin/env python3
"""Read-only PPTX preflight for editability and media-preservation risks."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/package/2006/relationships",
}
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")


def slide_number(name: str) -> int:
    match = SLIDE_RE.fullmatch(name)
    if not match:
        raise ValueError(name)
    return int(match.group(1))


def relation_targets(archive: zipfile.ZipFile, number: int) -> list[str]:
    rel_name = f"ppt/slides/_rels/slide{number}.xml.rels"
    if rel_name not in archive.namelist():
        return []
    root = ET.fromstring(archive.read(rel_name))
    return [item.get("Target", "") for item in root.findall("r:Relationship", NS)]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def audit(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        slides = sorted(
            (name for name in names if SLIDE_RE.fullmatch(name)),
            key=slide_number,
        )
        media = sorted(name for name in names if name.startswith("ppt/media/"))
        media_types = Counter(Path(name).suffix.lower().lstrip(".") or "none" for name in media)
        masters = sorted(name for name in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name))
        layouts = sorted(name for name in names if re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", name))
        themes = sorted(name for name in names if re.fullmatch(r"ppt/theme/theme\d+\.xml", name))
        embedded_fonts = sorted(name for name in names if name.startswith("ppt/fonts/"))
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        slide_size = presentation.find("p:sldSz", NS)
        slide_dimensions = None
        if slide_size is not None:
            cx = int(slide_size.get("cx", "0"))
            cy = int(slide_size.get("cy", "0"))
            slide_dimensions = {
                "cx_emu": cx,
                "cy_emu": cy,
                "width_inches": round(cx / 914400, 3),
                "height_inches": round(cy / 914400, 3),
                "aspect_ratio": round(cx / cy, 4) if cy else None,
            }
        slide_rows = []
        fonts = Counter()
        technical_classes = Counter()
        transition_types = Counter()
        risk_slides: dict[str, list[int]] = {
            "animations": [],
            "transitions": [],
            "video_or_audio": [],
            "charts": [],
            "tables": [],
            "smartart_or_diagram": [],
        }

        for name in slides:
            number = slide_number(name)
            root = ET.fromstring(archive.read(name))
            targets = relation_targets(archive, number)
            extensions = {Path(target).suffix.lower() for target in targets}
            has_timing = root.find(".//p:timing", NS) is not None
            has_transition = root.find(".//p:transition", NS) is not None
            has_av = bool(extensions & {".mp4", ".mov", ".m4v", ".avi", ".mp3", ".m4a", ".wav"})
            has_chart = any("/charts/" in target or target.startswith("../charts/") for target in targets)
            has_diagram = any("/diagrams/" in target or target.startswith("../diagrams/") for target in targets)
            table_count = len(root.findall(".//a:tbl", NS))
            for font_tag in ("latin", "ea", "cs"):
                for font_node in root.findall(f".//a:{font_tag}", NS):
                    typeface = font_node.get("typeface")
                    if typeface and not typeface.startswith("+"):
                        fonts[typeface] += 1

            transition = root.find(".//p:transition", NS)
            transition_type = None
            if transition is not None:
                transition_type = local_name(transition[0].tag) if len(transition) else "default"
                transition_types[transition_type] += 1

            if has_timing:
                risk_slides["animations"].append(number)
            if has_transition:
                risk_slides["transitions"].append(number)
            if has_av:
                risk_slides["video_or_audio"].append(number)
            if has_chart:
                risk_slides["charts"].append(number)
            if table_count:
                risk_slides["tables"].append(number)
            if has_diagram:
                risk_slides["smartart_or_diagram"].append(number)

            text_shapes = len(root.findall(".//p:sp", NS))
            pictures = len(root.findall(".//p:pic", NS))
            graphic_frames = len(root.findall(".//p:graphicFrame", NS))
            groups = len(root.findall(".//p:grpSp", NS))
            object_count = text_shapes + pictures + graphic_frames + groups
            if has_timing or has_av:
                technical_class = "media-protected"
            elif pictures >= 8 or groups >= 2 or object_count >= 25 or (pictures >= 4 and text_shapes <= 3):
                technical_class = "composite-visual"
            else:
                technical_class = "native-editable"
            technical_classes[technical_class] += 1

            slide_rows.append(
                {
                    "slide": number,
                    "technical_classification": technical_class,
                    "semantic_evidence_review_required": bool(has_chart or table_count or pictures),
                    "text_shapes": text_shapes,
                    "pictures": pictures,
                    "graphic_frames": graphic_frames,
                    "groups": groups,
                    "tables": table_count,
                    "text_characters": sum(len(node.text or "") for node in root.findall(".//a:t", NS)),
                    "has_animation": has_timing,
                    "has_transition": has_transition,
                    "transition_type": transition_type,
                    "has_video_or_audio": has_av,
                    "has_chart": has_chart,
                    "has_smartart_or_diagram": has_diagram,
                }
            )

        for style_name in masters + layouts + themes + ["ppt/presentation.xml"]:
            style_root = ET.fromstring(archive.read(style_name))
            for font_tag in ("latin", "ea", "cs"):
                for font_node in style_root.findall(f".//a:{font_tag}", NS):
                    typeface = font_node.get("typeface")
                    if typeface and not typeface.startswith("+"):
                        fonts[typeface] += 1

        macros = [name for name in names if name.lower().endswith("vbaproject.bin")]
        embeddings = [name for name in names if name.startswith("ppt/embeddings/")]
        high_risk = bool(
            risk_slides["animations"]
            or risk_slides["video_or_audio"]
            or macros
            or embeddings
        )
        if high_risk:
            route = "powerpoint-ui-preserve"
        elif risk_slides["transitions"]:
            route = "powerpoint-ui-preserve-if-transitions-must-survive"
        else:
            route = "artifact-tool-file-edit"

        return {
            "file": str(path.resolve()),
            "summary": {
                "slides": len(slides),
                "media_files": len(media),
                "media_types": dict(sorted(media_types.items())),
                "slide_dimensions": slide_dimensions,
                "slide_masters": len(masters),
                "slide_layouts": len(layouts),
                "themes": len(themes),
                "macros": len(macros),
                "embeddings": len(embeddings),
                "embedded_fonts": len(embedded_fonts),
                "fonts_referenced": [name for name, _ in fonts.most_common()],
                "technical_classifications": dict(technical_classes),
                "transition_types": dict(transition_types),
                "recommended_route": route,
            },
            "risk_slides": risk_slides,
            "slides": slide_rows,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if not args.pptx.is_file():
        parser.error(f"file not found: {args.pptx}")
    result = audit(args.pptx)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
