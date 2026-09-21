#!/usr/bin/env python3
"""Expand JP_* key actions into stock RMK actions.

The source keyboard TOML may use names compatible with the ZMK
jpkeysforuslayout module. Simple JP actions become ordinary RMK actions.
Shift-dependent mod-morph actions are implemented with RMK forks and
automatically allocated F13..F24 virtual trigger keys.

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DIRECT = {
    "JP_AMP": "WM(Kc6, LShift)",
    "JP_CARET": "Equal",
    "JP_QUOTE": "WM(Kc7, LShift)",
    "JP_DQUOTE": "WM(Kc2, LShift)",
    "JP_EQUAL": "WM(Minus, LShift)",
    "JP_PLUS": "WM(Semicolon, LShift)",
    "JP_YEN": "International3",
    "JP_PIPE": "WM(International3, LShift)",
    "JP_AT": "LeftBracket",
    "JP_COLON": "Quote",
    "JP_ASTER": "WM(Quote, LShift)",
    "JP_BAQT": "WM(LeftBracket, LShift)",
    "JP_TILDE": "WM(Equal, LShift)",
    "JP_UNDER": "WM(International1, LShift)",
    "JP_LBRACE": "WM(RightBracket, LShift)",
    "JP_LBRACKET": "RightBracket",
    "JP_RBRACE": "WM(Backslash, LShift)",
    "JP_RBRACKET": "Backslash",
    "JP_LPAREN": "WM(Kc8, LShift)",
    "JP_RPAREN": "WM(Kc9, LShift)",
    "JP_KANA": "Language1",
    "JP_EISU": "Language2",
    "JP_HANZEN": "Grave",
}

# Stable JP morph ABI shared with MyKeebStudio.
# Do not reorder/reassign these triggers without bumping the ABI.
MORPHS = {
    "JP_MINUSUNDER": ("F13", "Minus", "WM(International1, LShift)"),
    "JP_EQUALPLUS": ("F14", "WM(Minus, LShift)", "WM(Semicolon, LShift)"),
    "JP_SEMICOLONCOLON": ("F15", "Semicolon", "Quote"),
    "JP_QUOTEDQUOTE": ("F16", "WM(Kc7, LShift)", "WM(Kc2, LShift)"),
    "JP_YENPIPE": ("F17", "International3", "WM(International3, LShift)"),
    "JP_BAQTTILDE": ("F18", "WM(LeftBracket, LShift)", "WM(Equal, LShift)"),
    "JP_LBRACELBRACKET": ("F19", "RightBracket", "WM(RightBracket, LShift)"),
    "JP_RBRACERBRACKET": ("F20", "Backslash", "WM(Backslash, LShift)"),
}

JPKEYS_ABI = 1

TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])({})(?![A-Za-z0-9_])")


def contains_token(text: str, token: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", text) is not None


def replace_token(text: str, token: str, replacement: str) -> str:
    return re.sub(
        rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
        replacement,
        text,
    )


def allocate_morph_triggers(source: str, used_morphs: list[str]) -> dict[str, str]:
    trigger_map = {name: MORPHS[name][0] for name in used_morphs}
    collisions = sorted(
        trigger for name, trigger in trigger_map.items()
        if contains_token(source, trigger)
    )
    if collisions:
        raise ValueError(
            "JP Keys ABI v1 reserves F13..F20 for shift-dependent JP behaviors. "
            "Source keymap already uses: " + ", ".join(collisions)
        )
    return trigger_map


def fork_entries(trigger_map: dict[str, str]) -> str:
    lines = []
    for name in MORPHS:
        if name not in trigger_map:
            continue
        trigger = trigger_map[name]
        _, negative, positive = MORPHS[name]
        lines.append(f'  # {name}')
        lines.append(
            '  { trigger = "%s", negative_output = "%s", positive_output = "%s", '
            'match_any = "LShift|RShift" },'
            % (trigger, negative, positive)
        )
    return "\n".join(lines)


def inject_forks(text: str, entries: str) -> str:
    if not entries:
        return text

    header = "# BEGIN rmk-jpkeys-for-us-layout (generated)\n"
    footer = "# END rmk-jpkeys-for-us-layout (generated)\n"
    generated = header + entries + "\n" + footer

    # Merge into an existing [behavior.fork] list when present.
    section = re.search(r"(?m)^\[behavior\.fork\]\s*$", text)
    if section:
        tail = text[section.end():]
        match = re.search(r"(?m)^forks\s*=\s*\[", tail)
        if not match:
            raise ValueError("[behavior.fork] exists but has no 'forks = [' list")
        insert_at = section.end() + match.end()
        return text[:insert_at] + "\n" + generated + text[insert_at:]

    block = "\n[behavior.fork]\nforks = [\n" + generated + "]\n"
    # Place behavior before common runtime sections when possible.
    anchors = [
        "\n[ble]",
        "\n[host]",
        "\n[split]",
        "\n[rmk]",
    ]
    positions = [p for a in anchors if (p := text.find(a)) >= 0]
    if positions:
        pos = min(positions)
        return text[:pos] + block + text[pos:]
    return text.rstrip() + "\n" + block


def transform(source: str, runtime_abi: bool = False) -> tuple[str, dict[str, str]]:
    # Runtime configurators such as MyKeebStudio can assign any ABI morph after
    # flashing. In that mode all stable triggers must exist even when a morph is
    # absent from the source keymap defaults.
    used_morphs = list(MORPHS) if runtime_abi else [
        name for name in MORPHS if contains_token(source, name)
    ]
    trigger_map = allocate_morph_triggers(source, used_morphs)

    out = source
    for name, action in DIRECT.items():
        out = replace_token(out, name, action)
    for name, trigger in trigger_map.items():
        out = replace_token(out, name, trigger)

    unknown = sorted(set(re.findall(r"\bJP_[A-Z0-9_]+\b", out)))
    if unknown:
        raise ValueError("Unknown JP key token(s): " + ", ".join(unknown))

    out = inject_forks(out, fork_entries(trigger_map))
    return out, trigger_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="source keyboard.jp.toml")
    parser.add_argument("output", type=Path, help="generated keyboard.toml")
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; fail if output is missing or differs",
    )
    parser.add_argument(
        "--runtime-abi",
        action="store_true",
        help="reserve and emit all stable F13..F20 JP morph triggers for runtime configurators",
    )
    args = parser.parse_args()

    source = args.input.read_text(encoding="utf-8")
    try:
        rendered, trigger_map = transform(source, runtime_abi=args.runtime_abi)
    except ValueError as exc:
        print(f"rmk-jpkeys: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"rmk-jpkeys: generated output differs: {args.output}", file=sys.stderr)
            return 1
        print(f"rmk-jpkeys: OK: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    if trigger_map:
        mapping = ", ".join(f"{name}={key}" for name, key in trigger_map.items())
        print(f"rmk-jpkeys: generated {args.output} ({mapping})")
    else:
        print(f"rmk-jpkeys: generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
