#!/usr/bin/env python3
"""Validate IMAGE2IMAGE visual task sheets without external dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROLES = {"emotion", "product", "insight", "evidence", "idea", "mechanism", "summary"}
MODES = {
    "direct-use",
    "light-edit",
    "image2image-edit",
    "preserve-cutout-composite",
    "identity-preserve",
    "evidence-preserve",
    "generate-new",
}
INPUT_ROLES = {"edit-target", "style-reference", "supporting-insert", "evidence"}
REQUIRED = {
    "slide",
    "role",
    "message",
    "asset_mode",
    "source_assets",
    "input_image_roles",
    "invariants",
    "target",
    "visual_language",
    "allowed_changes",
    "forbidden",
}
TARGET_REQUIRED = {"aspect_ratio", "subject_position", "text_safe_zone"}
VISUAL_LANGUAGE_REQUIRED = {"target_brand", "reference_policy"}


def nonempty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def validate(data: object) -> list[str]:
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list) or not tasks:
        return ["root must be a non-empty list or an object with non-empty tasks"]

    errors: list[str] = []
    seen_slides: set[int] = set()
    for index, task in enumerate(tasks, start=1):
        prefix = f"task {index}"
        if not isinstance(task, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        missing = REQUIRED - task.keys()
        if missing:
            errors.append(f"{prefix}: missing {', '.join(sorted(missing))}")
            continue
        if not isinstance(task["slide"], int) or task["slide"] < 1:
            errors.append(f"{prefix}: slide must be a positive integer")
        elif task["slide"] in seen_slides:
            errors.append(f"{prefix}: duplicate slide {task['slide']}")
        else:
            seen_slides.add(task["slide"])
        if task["role"] not in ROLES:
            errors.append(f"{prefix}: invalid role {task['role']!r}")
        if task["asset_mode"] not in MODES:
            errors.append(f"{prefix}: invalid asset_mode {task['asset_mode']!r}")
        if not isinstance(task["message"], str) or not task["message"].strip():
            errors.append(f"{prefix}: message must be non-empty")
        source_assets = task["source_assets"]
        if task["asset_mode"] != "generate-new" and not nonempty_list(source_assets):
            errors.append(f"{prefix}: source_assets required for {task['asset_mode']}")
        if not isinstance(source_assets, list) or not all(
            isinstance(item, str) and item.strip() for item in source_assets
        ):
            errors.append(f"{prefix}: source_assets must be a string list")
            source_assets = []
        input_roles = task["input_image_roles"]
        if not isinstance(input_roles, dict):
            errors.append(f"{prefix}: input_image_roles must be an object")
        else:
            missing_roles = set(source_assets) - input_roles.keys()
            extra_roles = input_roles.keys() - set(source_assets)
            if missing_roles:
                errors.append(f"{prefix}: missing input roles for {', '.join(sorted(missing_roles))}")
            if extra_roles:
                errors.append(f"{prefix}: input roles reference unknown assets {', '.join(sorted(extra_roles))}")
            for asset, role in input_roles.items():
                if role not in INPUT_ROLES:
                    errors.append(f"{prefix}: invalid input role {role!r} for {asset}")
        for key in ("invariants", "allowed_changes", "forbidden"):
            if not isinstance(task[key], list) or not all(isinstance(item, str) for item in task[key]):
                errors.append(f"{prefix}: {key} must be a string list")
        if task["asset_mode"] in {
            "light-edit",
            "image2image-edit",
            "preserve-cutout-composite",
            "identity-preserve",
            "evidence-preserve",
        }:
            if not nonempty_list(task["invariants"]):
                errors.append(f"{prefix}: invariants must be non-empty for protected assets")
        if task["asset_mode"] in {
            "light-edit",
            "image2image-edit",
            "preserve-cutout-composite",
            "identity-preserve",
            "generate-new",
        } and not nonempty_list(task["allowed_changes"]):
            errors.append(f"{prefix}: allowed_changes must be non-empty for {task['asset_mode']}")
        if task["asset_mode"] != "direct-use" and not nonempty_list(task["forbidden"]):
            errors.append(f"{prefix}: forbidden must be non-empty for {task['asset_mode']}")
        target = task["target"]
        if not isinstance(target, dict):
            errors.append(f"{prefix}: target must be an object")
        else:
            target_missing = TARGET_REQUIRED - target.keys()
            if target_missing:
                errors.append(f"{prefix}: target missing {', '.join(sorted(target_missing))}")
            for key in TARGET_REQUIRED & target.keys():
                if not isinstance(target[key], str) or not target[key].strip():
                    errors.append(f"{prefix}: target.{key} must be non-empty")
        visual_language = task["visual_language"]
        if not isinstance(visual_language, dict):
            errors.append(f"{prefix}: visual_language must be an object")
        else:
            language_missing = VISUAL_LANGUAGE_REQUIRED - visual_language.keys()
            if language_missing:
                errors.append(f"{prefix}: visual_language missing {', '.join(sorted(language_missing))}")
            for key in VISUAL_LANGUAGE_REQUIRED & visual_language.keys():
                if not isinstance(visual_language[key], str) or not visual_language[key].strip():
                    errors.append(f"{prefix}: visual_language.{key} must be non-empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.json_file.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    task_count = len(data["tasks"] if isinstance(data, dict) else data)
    print(f"VALID: {task_count} visual task(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
