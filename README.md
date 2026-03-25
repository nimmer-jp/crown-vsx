# Nim Crown

Crown, Tiara, Nimtra向けのVSCode構文ハイライト拡張です。

## 機能

- `html""" """` ブロック内のHTMLシンタックスハイライト
- `component""" """` / `html: """ """` ブロック内のHTMLシンタックスハイライト
- `css: """ """` ブロック内のCSSシンタックスハイライト
- Crown raw HTMLディレクティブのハイライト (`{? if ... ?}`, `{?= expr ?}`, `<? ... ?>`)
- Crown scoped component DSLのハイライト (`component myButton(...):`, `css:`, `html:`, `text`, `raw`)
- Tiaraコンポーネント関数のハイライト (`Tiara.button`, `Tiara.card` 等)
- Nimtraモデルプラグマのハイライト (`{.primary.}`, `{.unique.}` 等)
- Nimtraクエリメソッドのハイライト (`db.select(...)`, `.where(...)` 等)
- Crownルートハンドラのハイライト (`proc page*`, `proc post*` 等)

## 対応フレームワーク

- [Crown](https://github.com/nimmer-jp/crown) — Nimのメタフレームワーク
- [Tiara](https://github.com/nimmer-jp/tiara) — NimのUIコンポーネントライブラリ
- [Nimtra](https://github.com/nimmer-jp/nimtra) — NimのORM

## インストール

[Open VSX Registry](https://open-vsx.org/extension/nimmer-jp/nim-crown) からインストールしてください。
