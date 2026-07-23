#!/usr/bin/env python3
"""Build a numbered Xiaohongshu/reference contact sheet and Markdown ledger."""

from __future__ import annotations

import argparse
import json
import textwrap
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(size: int):
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def ellipsize(text: str, limit: int) -> str:
    normalized = " ".join(str(text).split())
    return normalized if len(normalized) <= limit else normalized[: limit - 1] + "…"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()

    raw = json.loads(args.json_file.read_text(encoding="utf-8"))
    items = raw.get("candidates", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not 1 <= len(items) <= 12:
        parser.error("candidates must contain 1-12 items")

    required = {"id", "image_path", "title", "author", "url", "reason", "composition"}
    for index, item in enumerate(items, start=1):
        missing = required - set(item)
        if missing:
            parser.error(f"candidate {index} missing: {', '.join(sorted(missing))}")
        image_path = (args.json_file.parent / item["image_path"]).resolve()
        if not image_path.is_file():
            parser.error(f"candidate {index} image not found: {image_path}")
        item["_resolved_image"] = image_path

    columns = 3
    rows = (len(items) + columns - 1) // columns
    width, margin, gap = 1800, 60, 28
    card_w = (width - margin * 2 - gap * (columns - 1)) // columns
    card_h = 410
    header_h = 120
    height = header_h + margin + rows * card_h + max(0, rows - 1) * gap + margin
    board = Image.new("RGB", (width, height), "#F2F1ED")
    draw = ImageDraw.Draw(board)
    title_font = load_font(42)
    label_font = load_font(26)
    meta_font = load_font(20)
    draw.text((margin, 34), "小红书 / 社交内容参考灵感板", fill="#111111", font=title_font)
    draw.text((width - 360, 48), f"{len(items)} REFERENCES", fill="#6A6A6A", font=meta_font)

    for index, item in enumerate(items):
        row, col = divmod(index, columns)
        x = margin + col * (card_w + gap)
        y = header_h + margin + row * (card_h + gap)
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=18, fill="white")
        image = Image.open(item["_resolved_image"]).convert("RGB")
        thumb = ImageOps.fit(image, (card_w, 270), method=Image.Resampling.LANCZOS)
        board.paste(thumb, (x, y))
        draw.rectangle((x + 16, y + 16, x + 80, y + 64), fill="#111111")
        draw.text((x + 30, y + 22), str(item["id"]), fill="white", font=meta_font)
        draw.text((x + 20, y + 286), ellipsize(item["title"], 28), fill="#111111", font=label_font)
        draw.text((x + 20, y + 330), f"@{ellipsize(item['author'], 22)}", fill="#6A6A6A", font=meta_font)
        lines = textwrap.wrap(ellipsize(item["composition"], 48), width=24)
        draw.text((x + 20, y + 365), " / ".join(lines[:1]), fill="#D94F2B", font=meta_font)

    args.board.parent.mkdir(parents=True, exist_ok=True)
    board.save(args.board, quality=92)

    ledger = [
        "# 小红书 / 社交内容参考来源清单",
        "",
        f"- 生成日期：{date.today().isoformat()}",
        "- 默认权利状态：reference-only",
        "- 使用规则：仅用于构图、场景和内容形式研究，不自动取图入稿。",
        "",
    ]
    for item in items:
        ledger.extend(
            [
                f"## {item['id']}. {item['title']}",
                "",
                f"- 作者：{item['author']}",
                f"- 原帖：{item['url']}",
                f"- 推荐理由：{item['reason']}",
                f"- 可借鉴构图：{item['composition']}",
                "- 权利状态：reference-only",
                "",
            ]
        )
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text("\n".join(ledger), encoding="utf-8")
    print(f"board: {args.board.resolve()}")
    print(f"ledger: {args.ledger.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
