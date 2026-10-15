# ふしぎ診断所

Netlify: https://amazing-dusk-b8e52b.netlify.app

- `index.html` 診断一覧
- `afro/` アフロ診断
- `akuma/` 悪魔診断(10問・10体の悪魔)
- `*/r/<type>/` 結果ごとのシェア用ページ(Xのカード画像設定)
- `*/og/` シェア画像(1200×630)
- `make_og.py` シェア画像と結果ページを作り直すスクリプト(`python3 make_og.py https://サイトURL`)。

## 画像について
アフロのイラスト(`afro/img/`)とシェア画像(`afro/og/`, `og.png`)は、AI生成した画像をまとめたzipを
Netlifyのビルド時に `fetch_assets.py` が取り込みます。zipのURLは `fetch_assets.py` の中にあります。
リポジトリ内の `afro/og/*.png` は手描き版の予備で、ビルド時に上書きされます。

## 悪魔診断のシェア画像
`akuma/og/` と `akuma/r/<悪魔名>/` は `python3 make_og_akuma.py https://サイトURL` で作り直せます。
こちらはAI生成画像ではなく、ページ内のSVGの肖像から作るので、Netlifyのビルド時に上書きされません。
