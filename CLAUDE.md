# CLAUDE.md — ロジトレ(logitore)

ロジカルシンキングの思考ノート+ドリルの PWA。Claude(チャット)で構想・仕様を固め、Claude Code で実装を引き継ぐ。

## ユーザーについて
- ユーザーはプログラムを書けない。会話ベースで開発を進める。
- 説明は高校生にもわかる言葉で。専門用語には一言説明を添える。
- 事実に基づいて答え、確証がないことは「わからない」と言う。ユーザーの見落とし・懸念点・改善点は積極的に提案する。

## 作業ルール(必ず守る)
- ユーザーが **「実行」** と言うまで実装しない。アイデア段階では議論・整理のみ。
- UI・見た目の変更は、まず HTML の試作(モック)を見せて確認を取ってから実装する。モック提示後の返答は「OK」→実装へ/「修正」→修正して再提示/「保留」→停止。
- コードを書いたら必ず動作確認(`bash tests/run.sh`)をしてから報告する。
- 用語:
  - **試作**:「記録」前の実装。ラベル「検討中(ver未確定)」を付ける。
  - **記録**:ユーザーがこの言葉を言った時点が正式な改訂。ver を更新する。
  - **破棄**:試作を取り消し、直前の「記録」時点に戻す(= 直前のタグに戻す)。
- 採番:通常の追加・修正はマイナー(v1.0→v1.1)、大幅・破壊的変更はメジャー(v1.x→v2.0)。迷ったらユーザーに確認。
- 「記録」のときにやること:
  1. `index.html` の `APP.version`、`sw.js` の `CACHE` 名を更新する
  2. 取扱説明書(`manual.html`)と設計仕様書(`docs/spec.html`、未作成なら作成)の更新履歴に追記する
  3. 引き継ぎファイル `docs/handoff/handoff_vX.Y.md` を新規作成する(過去分は上書きしない)
  4. `main` にマージし、`vX.Y` のタグを付ける
- 開発中のエラー・不具合は毎回この形式で報告する:1. 何が起きたか / 2. 原因 / 3. 対処内容 / 4. 再発防止策

## Git の運用
- `main` = 公開している版。作業はブランチ(例:`feature/multi-tab-sync`)で行い、PR を作ってからマージする。
- コミットメッセージは日本語で、何を変えたかが分かるように書く。

## 公開先
- GitHub Pages:https://tmgalaxy330-byte.github.io/PWA-app/(公開リポジトリの `main` 直下。`main` に取り込むと自動で公開される)

## ファイル構成
| ファイル | 役割 |
|---|---|
| `index.html` | アプリ本体(HTML/CSS/JS を1ファイルにまとめている。ビルド不要) |
| `manual.html` | 取扱説明書。アプリの設定・メニューから iframe で開く |
| `sw.js` | Service Worker(オフライン対応・更新通知)。**リリースのたびに `CACHE` 名を変える** |
| `manifest.webmanifest` | PWA 設定(アイコン・共有ターゲット) |
| `icons/` | アプリアイコン |
| `tests/` | Playwright による自動テスト(`bash tests/run.sh`) |
| `docs/spec.html` | 設計仕様書(記録のたびに更新履歴を追記) |
| `docs/handoff/` | 引き継ぎファイル(版ごとに追加) |

## index.html の中身(`/* ===== 見出し ===== */` で区切っている)
- 基本情報(`APP`)/アイコン(`ICONS`)/保存(`Store`、localStorage キー `logitore.v1`)/エラーログ/演出(リップル・シェイク・紙吹雪)/トースト
- 戻る操作:`Back`(シート等の重なり)と `Nav`(画面単位)。Android は CloseWatcher、それ以外は History API
- オーバーレイ部品:`sheet()` `dialog()` `menu()`
- テーマ/テンプレート(`TPL`・`USAGE`・`SAMPLE`・`DIAG`)/用語集(`GLOSS`)
- 画面:ホーム(`renderHome`)/作業画面(`renderEditor`・アウトライン・ツリー・パネル)/ドリル(`Q` 20問)/ゴミ箱/設定
- 書き出し・読み込み/PIN ロック/初回ガイド/PWA 更新通知/起動(`boot`)

## データ(端末内のみ。サーバーには送らない)
`S = { schema, thoughts[], trash[], settings{}, drill{}, errors[], meta{} }`
- 思考:`{ id, title, template, status(draft|wip|done), pinned, created, updated, root(ノードの木), memo, mece{a,b,c}, reviews[] }`
- ノード:`{ id, text, children[], label, ph, collapsed }`
- データ形式を変えるときは `migrate()` に移行処理を書き、既存データが壊れないようにする。

## 注意点
- 日本語入力:Enter 判定では `e.isComposing` と `keyCode===229` を必ず除外する。
- 保存はモバイルで終了イベントが来ないことがあるため、入力後の自動保存+`visibilitychange` で行っている。
- Android の戻るボタンの確認動作は、自動テストでは Esc キーで代用している。実機での確認が必要。
