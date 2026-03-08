# Crown VSX Syntax Highlighting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Crown / Tiara / Nimtra 向けのVSCode構文ハイライト拡張をOpenVSX向けにビルドする。

**Architecture:** TextMate Grammar方式。`injectTo: ["source.nim"]` でNimファイルにパターンを注入するinjection grammarと、Nim拡張が未インストールの場合のフォールバック用基本Nim grammarを提供する。`html""" """` ブロック内部をHTMLとして着色するために `embeddedLanguages` を使用する。

**Tech Stack:** TextMate Grammar (JSON), VSCode Extension API, vsce (パッケージング), ovsx (OpenVSX公開)

---

## ハイライト対象まとめ

| 対象 | パターン | スコープ |
|------|---------|---------|
| `html""" """` ブロック全体 | `html` + `"""..."""` | `meta.embedded.block.html` → HTML文法 |
| Crown HTTPハンドラ | `proc page*`, `proc post*`, etc. (procの後) | `entity.name.function.crown` |
| Crown関数 | `htmlResponse`, `jsonResponse`, `injectCrownSystem` | `support.function.crown` |
| `html` キーワード (テンプレート前) | `html` before `"""` | `keyword.other.html-template.crown` |
| Tiaraネームスペース | `Tiara` before `.` | `entity.name.type.tiara` |
| Tiaraコンポーネント関数 | `Tiara.button`, `Tiara.card`, etc. | `support.function.tiara` |
| Nimtraプラグマキーワード | `primary`, `autoincrement`, `unique`, etc. in `{. .}` | `storage.modifier.pragma.nimtra` |
| Nimtraクエリメソッド | `.select(`, `.where(`, `.all()`, etc. | `support.function.nimtra` |
| `{...}` Nim補間 (HTML内) | `{...}` inside html block | `meta.embedded.expression.nim.crown` → Nim文法 |

---

## Task 1: プロジェクトスキャフォールド

**Files:**
- Create: `package.json`
- Create: `language-configuration.json`
- Create: `.vscodeignore`
- Create: `README.md`

**Step 1: package.json を作成**

```json
{
  "name": "crown-vsx",
  "displayName": "Crown VSX",
  "description": "Syntax highlighting for Crown, Tiara, and Nimtra Nim frameworks",
  "version": "0.1.0",
  "publisher": "nimmer-jp",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Programming Languages"],
  "keywords": ["nim", "crown", "tiara", "nimtra", "syntax highlighting"],
  "repository": {
    "type": "git",
    "url": "https://github.com/nimmer-jp/crown-vsx"
  },
  "license": "MIT",
  "contributes": {
    "languages": [
      {
        "id": "nim",
        "aliases": ["Nim", "nim"],
        "extensions": [".nim", ".nims", ".nimble"],
        "configuration": "./language-configuration.json"
      }
    ],
    "grammars": [
      {
        "language": "nim",
        "scopeName": "source.nim",
        "path": "./syntaxes/nim.tmLanguage.json"
      },
      {
        "scopeName": "crown.injection",
        "path": "./syntaxes/crown.tmLanguage.json",
        "injectTo": ["source.nim"],
        "embeddedLanguages": {
          "meta.embedded.block.html": "html",
          "meta.embedded.expression.nim.crown": "nim"
        }
      }
    ]
  }
}
```

**Step 2: language-configuration.json を作成**

```json
{
  "comments": {
    "lineComment": "#",
    "blockComment": ["#[", "]#"]
  },
  "brackets": [
    ["{", "}"],
    ["[", "]"],
    ["(", ")"]
  ],
  "autoClosingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "\"", "close": "\"", "notIn": ["string"] },
    { "open": "'", "close": "'", "notIn": ["string", "comment"] },
    { "open": "{.", "close": ".}" }
  ],
  "surroundingPairs": [
    ["{", "}"],
    ["[", "]"],
    ["(", ")"],
    ["\"", "\""],
    ["'", "'"]
  ],
  "indentationRules": {
    "increaseIndentPattern": "^((?!#).)*:\\s*$"
  }
}
```

**Step 3: .vscodeignore を作成**

```
.vscode/**
docs/**
.gitignore
*.md
!README.md
```

**Step 4: README.md を作成**

```markdown
# Crown VSX

Crown, Tiara, Nimtra向けのVSCode構文ハイライト拡張です。

## 機能

- `html""" """` ブロック内のHTMLシンタックスハイライト
- Tiaraコンポーネント関数のハイライト (`Tiara.button`, `Tiara.card` 等)
- Nimtraモデルプラグマのハイライト (`{.primary.}`, `{.unique.}` 等)
- NimtraクエリメソッドのハイライトCoの (`db.select(...)`, `.where(...)` 等)
- CrownルートハンドラのハイライトCo (`proc page*`, `proc post*` 等)
```

**Step 5: コミット**

```bash
git add package.json language-configuration.json .vscodeignore README.md
git commit -m "feat: add project scaffolding for crown-vsx extension"
```

---

## Task 2: 基本Nim Grammar (フォールバック用)

**Files:**
- Create: `syntaxes/nim.tmLanguage.json`

**Step 1: syntaxes/ ディレクトリを作成して nim.tmLanguage.json を作成**

```json
{
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Nim",
  "scopeName": "source.nim",
  "fileTypes": ["nim", "nims", "nimble"],
  "patterns": [
    { "include": "#comments" },
    { "include": "#strings" },
    { "include": "#keywords" },
    { "include": "#numbers" },
    { "include": "#pragmas" },
    { "include": "#operators" },
    { "include": "#proc-declaration" }
  ],
  "repository": {
    "comments": {
      "patterns": [
        {
          "name": "comment.block.nim",
          "begin": "#\\[",
          "end": "\\]#"
        },
        {
          "name": "comment.line.number-sign.nim",
          "match": "#.*$"
        }
      ]
    },
    "strings": {
      "patterns": [
        {
          "name": "string.quoted.triple.nim",
          "begin": "\"\"\"",
          "end": "\"\"\""
        },
        {
          "name": "string.quoted.double.nim",
          "begin": "\"",
          "end": "\"",
          "patterns": [
            { "name": "constant.character.escape.nim", "match": "\\\\." }
          ]
        },
        {
          "name": "string.quoted.single.nim",
          "begin": "'",
          "end": "'",
          "patterns": [
            { "name": "constant.character.escape.nim", "match": "\\\\." }
          ]
        }
      ]
    },
    "keywords": {
      "patterns": [
        {
          "name": "keyword.control.nim",
          "match": "\\b(if|elif|else|for|while|do|case|of|when|try|except|finally|raise|break|continue|return|yield|defer|block)\\b"
        },
        {
          "name": "keyword.declaration.nim",
          "match": "\\b(proc|func|method|template|macro|iterator|converter|type|var|let|const|import|from|include|export|discard|addr|cast|nil|new|not|and|or|xor|in|notin|is|isnot|div|mod|shl|shr|as|bind|mixin|static|object|tuple|enum|distinct|ref|ptr|using|asm|interface)\\b"
        },
        {
          "name": "keyword.other.nim",
          "match": "\\b(async|await|result|echo|quit)\\b"
        },
        {
          "name": "constant.language.nim",
          "match": "\\b(true|false|nil)\\b"
        }
      ]
    },
    "numbers": {
      "patterns": [
        {
          "name": "constant.numeric.nim",
          "match": "\\b(0x[0-9A-Fa-f_]+|0o[0-7_]+|0b[01_]+|\\d[\\d_]*(\\.\\d[\\d_]*)?)\\b"
        }
      ]
    },
    "pragmas": {
      "patterns": [
        {
          "name": "meta.pragma.nim",
          "begin": "\\{\\.",
          "end": "\\.\\}",
          "beginCaptures": { "0": { "name": "punctuation.definition.pragma.begin.nim" } },
          "endCaptures": { "0": { "name": "punctuation.definition.pragma.end.nim" } },
          "patterns": [
            { "name": "keyword.other.pragma.nim", "match": "\\b\\w+\\b" },
            { "name": "string.quoted.double.nim", "begin": "\"", "end": "\"" },
            { "name": "constant.numeric.nim", "match": "\\b\\d+\\b" }
          ]
        }
      ]
    },
    "operators": {
      "patterns": [
        {
          "name": "keyword.operator.nim",
          "match": "[+\\-*/<>=!&|^~@%]+"
        }
      ]
    },
    "proc-declaration": {
      "patterns": [
        {
          "match": "\\b(proc|func|method|template|macro|iterator|converter)\\s+(\\w+\\*?)",
          "captures": {
            "1": { "name": "keyword.declaration.nim" },
            "2": { "name": "entity.name.function.nim" }
          }
        },
        {
          "match": "\\b(type)\\s+(\\w+\\*?)",
          "captures": {
            "1": { "name": "keyword.declaration.nim" },
            "2": { "name": "entity.name.type.nim" }
          }
        }
      ]
    }
  }
}
```

**Step 2: コミット**

```bash
git add syntaxes/nim.tmLanguage.json
git commit -m "feat: add basic Nim TextMate grammar as fallback"
```

---

## Task 3: Crown Injection Grammar — HTMLブロック埋め込み

**Files:**
- Create: `syntaxes/crown.tmLanguage.json`

**重要:** このファイルは `injectionSelector: "L:source.nim"` を使う。`L:` プレフィックスにより、注入パターンが元のNim grammarより高い優先度で適用される。これにより `html""" """` ブロックが通常のNim文字列ではなくHTMLとして認識される。

**Step 1: syntaxes/crown.tmLanguage.json を作成 (HTMLブロック部分のみ)**

```json
{
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Crown VSX Injection",
  "scopeName": "crown.injection",
  "injectionSelector": "L:source.nim",
  "patterns": [
    { "include": "#html-template" }
  ],
  "repository": {
    "html-template": {
      "name": "meta.embedded.block.html.crown",
      "begin": "(?<![\\w])(html)(\"\"\")",
      "end": "(\"\"\")",
      "beginCaptures": {
        "1": { "name": "keyword.other.html-template.crown" },
        "2": { "name": "punctuation.definition.string.begin.nim" }
      },
      "endCaptures": {
        "1": { "name": "punctuation.definition.string.end.nim" }
      },
      "contentName": "meta.embedded.block.html",
      "patterns": [
        { "include": "#nim-interpolation" },
        { "include": "text.html.basic" }
      ]
    },
    "nim-interpolation": {
      "name": "meta.embedded.expression.nim.crown",
      "begin": "\\{(?![[:space:]])",
      "end": "\\}",
      "beginCaptures": { "0": { "name": "punctuation.section.embedded.begin.nim" } },
      "endCaptures": { "0": { "name": "punctuation.section.embedded.end.nim" } },
      "patterns": [
        { "include": "source.nim" }
      ]
    }
  }
}
```

**Step 2: VSCodeで手動確認**

以下のNimファイルを開いて確認:
```nim
import crown/core

proc page*(req: Request): string =
  return html"""
    <div class="container">
      <h1>Title</h1>
      <p>{someVar}</p>
    </div>
  """
```

期待する結果:
- `html` が特別な色で表示される
- `"""` の後がHTMLとしてハイライト（タグ、属性、etc.）
- `{someVar}` がNimコードとしてハイライト
- 閉じ `"""` でHTMLハイライトが終了する

**Step 3: コミット**

```bash
git add syntaxes/crown.tmLanguage.json
git commit -m "feat: add Crown injection grammar with embedded HTML block support"
```

---

## Task 4: Injection Grammar — Crown / Tiara / Nimtra 識別子

**Files:**
- Modify: `syntaxes/crown.tmLanguage.json`

**Step 1: crown.tmLanguage.json の patterns と repository を拡張**

`"patterns"` の配列を更新 (html-templateの後に追加):
```json
"patterns": [
  { "include": "#html-template" },
  { "include": "#crown-identifiers" },
  { "include": "#tiara-components" },
  { "include": "#nimtra-pragmas" },
  { "include": "#nimtra-query-methods" }
]
```

`"repository"` に以下を追加:

```json
"crown-identifiers": {
  "patterns": [
    {
      "comment": "Crown route handler procs: proc page*, proc post*, etc.",
      "match": "(?<=\\bproc\\s+)(page|post|layout|get|put|delete|patch|notFound)\\b",
      "name": "entity.name.function.crown"
    },
    {
      "comment": "Crown response and utility functions",
      "match": "\\b(htmlResponse|jsonResponse|injectCrownSystem)\\b",
      "name": "support.function.crown"
    },
    {
      "comment": "Crown Request type",
      "match": "\\bRequest\\b",
      "name": "support.type.crown"
    }
  ]
},
"tiara-components": {
  "patterns": [
    {
      "comment": "Tiara namespace",
      "match": "\\bTiara\\b(?=\\.)",
      "name": "entity.name.type.tiara"
    },
    {
      "comment": "Tiara component methods after Tiara.",
      "match": "(?<=\\bTiara\\.)(button|card|text|badge|input|modal|navbar|hero|toast|tabs|dropdown|datePicker|colorPicker|container|searchBox|sectionHeader|codeBlock|carousel|iconWithBadge|notificationIcon|profileIcon|clientScriptTag|defaultStyles)\\b",
      "name": "support.function.tiara"
    }
  ]
},
"nimtra-pragmas": {
  "name": "meta.pragma.nim",
  "begin": "\\{\\.",
  "end": "\\.\\}",
  "beginCaptures": { "0": { "name": "punctuation.definition.pragma.begin.nim" } },
  "endCaptures": { "0": { "name": "punctuation.definition.pragma.end.nim" } },
  "patterns": [
    {
      "comment": "Nimtra model pragmas",
      "name": "storage.modifier.pragma.nimtra",
      "match": "\\b(primary|autoincrement|unique|index|maxLength|default|table)\\b"
    },
    {
      "comment": "General Nim pragmas",
      "name": "keyword.other.pragma.nim",
      "match": "\\b\\w+\\b"
    },
    {
      "name": "string.quoted.double.nim",
      "begin": "\"",
      "end": "\""
    },
    {
      "name": "constant.numeric.nim",
      "match": "\\b\\d+\\b"
    }
  ]
},
"nimtra-query-methods": {
  "patterns": [
    {
      "comment": "Nimtra query builder and CRUD methods",
      "match": "(?<=\\.)(select|where|all|first|insert|update|upsert|updateById|deleteById|findById|findByIdModel|findAll|findAllModels|existsById|insertReturningId|upsertReturningId|orderBy|limit|offset|columns|join|count|sync)\\b",
      "name": "support.function.nimtra"
    }
  ]
}
```

**Step 2: 完成した crown.tmLanguage.json の全体像を確認**

最終的なファイルの全体:

```json
{
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Crown VSX Injection",
  "scopeName": "crown.injection",
  "injectionSelector": "L:source.nim",
  "patterns": [
    { "include": "#html-template" },
    { "include": "#crown-identifiers" },
    { "include": "#tiara-components" },
    { "include": "#nimtra-pragmas" },
    { "include": "#nimtra-query-methods" }
  ],
  "repository": {
    "html-template": {
      "name": "meta.embedded.block.html.crown",
      "begin": "(?<![\\w])(html)(\"\"\")",
      "end": "(\"\"\")",
      "beginCaptures": {
        "1": { "name": "keyword.other.html-template.crown" },
        "2": { "name": "punctuation.definition.string.begin.nim" }
      },
      "endCaptures": {
        "1": { "name": "punctuation.definition.string.end.nim" }
      },
      "contentName": "meta.embedded.block.html",
      "patterns": [
        { "include": "#nim-interpolation" },
        { "include": "text.html.basic" }
      ]
    },
    "nim-interpolation": {
      "name": "meta.embedded.expression.nim.crown",
      "begin": "\\{(?![[:space:]])",
      "end": "\\}",
      "beginCaptures": { "0": { "name": "punctuation.section.embedded.begin.nim" } },
      "endCaptures": { "0": { "name": "punctuation.section.embedded.end.nim" } },
      "patterns": [
        { "include": "source.nim" }
      ]
    },
    "crown-identifiers": {
      "patterns": [
        {
          "match": "(?<=\\bproc\\s+)(page|post|layout|get|put|delete|patch|notFound)\\b",
          "name": "entity.name.function.crown"
        },
        {
          "match": "\\b(htmlResponse|jsonResponse|injectCrownSystem)\\b",
          "name": "support.function.crown"
        },
        {
          "match": "\\bRequest\\b",
          "name": "support.type.crown"
        }
      ]
    },
    "tiara-components": {
      "patterns": [
        {
          "match": "\\bTiara\\b(?=\\.)",
          "name": "entity.name.type.tiara"
        },
        {
          "match": "(?<=\\bTiara\\.)(button|card|text|badge|input|modal|navbar|hero|toast|tabs|dropdown|datePicker|colorPicker|container|searchBox|sectionHeader|codeBlock|carousel|iconWithBadge|notificationIcon|profileIcon|clientScriptTag|defaultStyles)\\b",
          "name": "support.function.tiara"
        }
      ]
    },
    "nimtra-pragmas": {
      "name": "meta.pragma.nim",
      "begin": "\\{\\.",
      "end": "\\.\\}",
      "beginCaptures": { "0": { "name": "punctuation.definition.pragma.begin.nim" } },
      "endCaptures": { "0": { "name": "punctuation.definition.pragma.end.nim" } },
      "patterns": [
        {
          "name": "storage.modifier.pragma.nimtra",
          "match": "\\b(primary|autoincrement|unique|index|maxLength|default|table)\\b"
        },
        {
          "name": "keyword.other.pragma.nim",
          "match": "\\b\\w+\\b"
        },
        {
          "name": "string.quoted.double.nim",
          "begin": "\"",
          "end": "\""
        },
        {
          "name": "constant.numeric.nim",
          "match": "\\b\\d+\\b"
        }
      ]
    },
    "nimtra-query-methods": {
      "patterns": [
        {
          "match": "(?<=\\.)(select|where|all|first|insert|update|upsert|updateById|deleteById|findById|findByIdModel|findAll|findAllModels|existsById|insertReturningId|upsertReturningId|orderBy|limit|offset|columns|join|count|sync)\\b",
          "name": "support.function.nimtra"
        }
      ]
    }
  }
}
```

**Step 3: VSCodeで手動確認 (全機能)**

以下のテストファイルを開いて全パターンを確認:

```nim
# Crown + Tiara + Nimtra 統合テスト

import crown/core
import tiara
import nimtra

# ---- Nimtra モデル ----
type
  User = ref object
    id {.primary, autoincrement.}: int
    name {.maxLength: 50.}: string
    email {.unique.}: string
    role {.default: "user".}: string
    table {.table: "users".}: string  # table pragma

# ---- Crown ルートハンドラ ----
proc post*(req: Request): string =
  let msg = req.postParams.getOrDefault("msg", "")
  return html"""
    {Tiara.toast(message="保存: " & msg)}
  """

proc page*(req: Request): string =
  let users = await db.select(User).where(it.role == "admin").all()
  return html"""
    <div class="container">
      <h1>Users</h1>
      {Tiara.button(label="追加", color="primary")}
      {Tiara.card(title="リスト")}
    </div>
  """

# ---- Nimtra クエリ ----
proc fetchUsers() {.async.} =
  let db = await openLibSQL(url = "file:local.db")
  let result = await db.select(User).where(it.id > 0).orderBy("name").limit(10).all()
  await db.insert(User(name: "Alice"))
  await db.sync()
```

チェック項目:
- [ ] `html` が特別な色 (keyword.other.html-template.crown)
- [ ] `"""..."""` 内がHTML文法でハイライト (タグ、属性名、属性値)
- [ ] `{Tiara.toast(...)}` がNimとしてハイライト
- [ ] `Tiara` が entity.name.type.tiara でハイライト
- [ ] `Tiara.` の後のコンポーネント名が support.function.tiara
- [ ] `proc page*`, `proc post*` 後の関数名が entity.name.function.crown
- [ ] `htmlResponse`, `jsonResponse` が support.function.crown
- [ ] `Request` が support.type.crown
- [ ] `{.primary, autoincrement.}` で `primary`, `autoincrement` が storage.modifier.pragma.nimtra
- [ ] `{.maxLength: 50.}` で `maxLength` が storage.modifier.pragma.nimtra
- [ ] `.select(`, `.where(`, `.all()` が support.function.nimtra
- [ ] `.orderBy(`, `.limit(`, `.insert(` も support.function.nimtra

**Step 4: コミット**

```bash
git add syntaxes/crown.tmLanguage.json
git commit -m "feat: add Crown/Tiara/Nimtra identifier highlighting to injection grammar"
```

---

## Task 5: VSIX パッケージング

**Step 1: vsce をインストール**

```bash
npm install -g @vscode/vsce
```

**Step 2: VSIX をビルド**

```bash
cd /Users/nakagawa_shota/repo/valit/crown-vsx
vsce package
```

期待する出力:
```
 DONE  Packaged: /Users/nakagawa_shota/repo/valit/crown-vsx/crown-vsx-0.1.0.vsix (X files, XX.XXkB)
```

もし `WARNING: LICENSE.md, LICENSE.txt or LICENSE not found` と出たらスキップして良い（後で追加可能）。

**Step 3: ローカルでインストールしてテスト**

```bash
code --install-extension crown-vsx-0.1.0.vsix
```

VSCodeを再起動し、Task 4のテストファイルで全チェック項目を再確認する。

**Step 4: コミット**

```bash
git add crown-vsx-0.1.0.vsix
git commit -m "build: add packaged VSIX v0.1.0"
```

注意: `.vscodeignore` に `*.vsix` を追加することも検討する（リポジトリに含めない場合）。

---

## Task 6 (Optional): OpenVSX 公開

**Step 1: ovsx をインストール**

```bash
npm install -g ovsx
```

**Step 2: OpenVSX にアクセストークンを設定**

[open-vsx.org](https://open-vsx.org) でアカウントを作成してトークンを取得。

**Step 3: 公開**

```bash
ovsx publish crown-vsx-0.1.0.vsix -p <ACCESS_TOKEN>
```

---

## 備考

- `nim-interpolation` パターンの `\\{(?![[:space:]])` は、Tailwind CSSのクラス内の `{` (例: `bg-[var(--...)]`) との誤検知を避けるためのルック・アヘッドではない。Tailwindは `[...]` を使うため実際は問題ない。ただし `{ ` のような空白始まりの場合は除外している。
- `nimtra-pragmas` パターンが `L:` 注入により既存Nim grammarのpragmaルールより優先される。これにより `{.primary.}` などのNimtraプラグマが正しく着色される。
- 将来の拡張として、HTMLブロック内の `crown-get`, `crown-post`, `crown-target` HTML属性をハイライトするには、`text.html.basic` へのサブ注入文法を追加する。
