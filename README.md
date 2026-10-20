# capitallogs-site

YUKI CAPITAL の公式サイト（https://yuki-capital.com）。GitHub Pages で公開し、DNS は Cloudflare。

## 構成
- `index.html` … トップ。`data/site.json` を読んで描画する（`assets/app.js`）
- `data/site.json` … 毎朝 Claude が更新する唯一のデータファイル（今日の資本・条件・保有・X の投稿・note・日記・メディアの数字・毎日の記録・記事一覧）
- `articles/` … サイト限定の記事（1記事1フォルダ `articles/<slug>/index.html`）
- `archive/` … 毎日の記録の一覧
- `about/` … プロフィールと実業・プライバシー・お問い合わせ
- `images/` … アイコンなど。日記の写真は x-images リポジトリの公開URLを使う

## 更新の手順（Claude のフェーズ7）
1. `data/site.json` の `capital` / `conditions` / `posts` / `note` / `diary` / `archive` を当日の値に書き換える
2. 記事を出す日は `articles/<slug>/index.html` を足し、`site.json` の `articles` 先頭に1件足す
3. `git add -A && git commit -m "update YYYY-MM-DD" && git push origin main`
4. 数分後に https://yuki-capital.com を開いて、日付と総金融資産が当日の値になっているか確かめる
