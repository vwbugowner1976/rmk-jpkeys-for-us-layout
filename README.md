# RMK JP Keys for US Layout

Reusable Japanese-key behaviors for **RMK** keyboards that use a US-style physical key arrangement while the host OS uses a Japanese/JIS keyboard layout.

The source names intentionally mirror `zmk-behavior-jpkeysforuslayout`, so the same semantic key names can be reused when moving a keyboard between ZMK and RMK.

## What it does

Write JP actions in a source file such as `keyboard.jp.toml`:

```toml
[[keymap.layer]]
name = "Base"
keys = """
JP_MINUSUNDER JP_EQUALPLUS JP_QUOTEDQUOTE JP_YENPIPE
"""
```

Then generate the normal RMK config:

```bash
python3 tools/apply_jpkeys.py keyboard.jp.toml keyboard.toml
```

The generated `keyboard.toml` contains only stock RMK actions. Simple JP keys are expanded directly. Shift-dependent keys are implemented with RMK `[behavior.fork]` entries.

No RMK fork and no Python package dependency are required.

## Supported keys

See [definitions/JP_KEYS.md](definitions/JP_KEYS.md). It includes:

- `JP_MINUSUNDER`, `JP_EQUALPLUS`
- `JP_SEMICOLONCOLON`, `JP_QUOTEDQUOTE`
- `JP_YENPIPE`, `JP_BAQTTILDE`
- bracket/brace pairs
- Japanese `@`, `^`, `&`, `*`, parentheses and related symbols
- `JP_KANA`, `JP_EISU`, `JP_HANZEN`

## Shift-dependent keys

RMK forks need a trigger action. The transformer automatically reserves unused keys from **F13..F24** only in the generated file. They are internal implementation details and are replaced by the fork before HID output.

If a keyboard already uses some of F13..F24, those keys are skipped automatically. Generation fails rather than silently colliding when too few virtual triggers remain.

## Recommended project layout

```text
your-rmk-keyboard/
├─ keyboard.jp.toml       # edit this
├─ keyboard.toml          # generated for RMK
└─ .cache/
   └─ rmk-jpkeys-for-us-layout/
```

Pin this repository to a known commit in your local build script, regenerate `keyboard.toml`, then run the normal RMK build.

## Verify generated output

```bash
python3 tools/apply_jpkeys.py keyboard.jp.toml keyboard.toml --check
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT.
