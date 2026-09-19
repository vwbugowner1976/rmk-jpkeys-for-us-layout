# JP key definitions

These names mirror the behaviors from `zmk-behavior-jpkeysforuslayout`.

| RMK source token | Meaning on a Japanese host layout |
| --- | --- |
| JP_AMP | & |
| JP_CARET | ^ |
| JP_QUOTE | ' |
| JP_DQUOTE | " |
| JP_QUOTEDQUOTE | ' / Shift: " |
| JP_EQUAL | = |
| JP_PLUS | + |
| JP_EQUALPLUS | = / Shift: + |
| JP_YEN | ¥ |
| JP_PIPE | \| |
| JP_YENPIPE | ¥ / Shift: \| |
| JP_AT | @ |
| JP_COLON | : |
| JP_SEMICOLONCOLON | ; / Shift: : |
| JP_ASTER | * |
| JP_BAQT | ` |
| JP_TILDE | ~ |
| JP_BAQTTILDE | ` / Shift: ~ |
| JP_UNDER | _ |
| JP_MINUSUNDER | - / Shift: _ |
| JP_LBRACE | { |
| JP_LBRACKET | [ |
| JP_LBRACELBRACKET | { / Shift: [ |
| JP_RBRACE | } |
| JP_RBRACKET | ] |
| JP_RBRACERBRACKET | } / Shift: ] |
| JP_LPAREN | ( |
| JP_RPAREN | ) |
| JP_KANA | Language 1 |
| JP_EISU | Language 2 |
| JP_HANZEN | Grave / Hankaku-Zenkaku style usage |

Shift-dependent tokens are expanded to RMK `[behavior.fork]` entries. The transformer uses free keys from F13..F24 as internal triggers only.
