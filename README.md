# webxpressd

Preprocessing Service for WebXpression

---

## はじめに

Raspberry Pi OS上で動作する、WebXpressionのためのpreprocessing serviceです。

* 文字コード変換
* httpsサイトへのアクセス
* 未対応タグの除去
* 画像の再圧縮

などを行います。

本ソフトウェアは WebXpression の高速・高機能を活かすために独自で開発しているものです。
WebXpression開発者の Mitsuky さんのご迷惑にならないよう、問い合わせについては tantan までお願いします。

---

## 前提条件

* Raspberry Pi 4B (4GB)
* Raspberry Pi OS Lite (GUIなし、32bit) の最新版

でのみ確認しています。

X680x0実機とIPネットワークで接続されており、かつインターネットにアクセスできる必要があります。
以下の覚書などを参考にしてください。

* [https://github.com/tantanGH/nereid-wifi-connection](https://github.com/tantanGH/nereid-wifi-connection)

---

## インストール

git, pip が入っていない場合はインストール。

    sudo apt install git
    sudo apt install pip

pipで導入。

    pip install git+https://github.com/tantanGH/webxpressd.git

---

## 使い方

コマンドラインから起動します。

    webxpressd

デフォルトではポート6803番、画像クオリティ20で待ち受け開始します。

webxpressdは一般ユーザ権限で動かすため、予約ポート(1024未満)は使えません。
しかしWebXpressionは80番ポート以外接続できないので、このままでは利用できません。

このため、80番ポートへのアクセスを6803番ポートにリダイレクトする設定をiptablesに対して行います。

    sudo apt install iptables-persistent
    sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 6803
    sudo netfilter-persistent save

一度設定するだけでokです。


X680x0側では、`\etc\hosts` に

    192.168.31.101    webxpressd

などとして、webxpressdが動いているホストに`webxpressd`の名前でアクセスできるようにしてください。WebXpressionはIPアドレスでのアクセスには対応していません。

また、WebXpressionのキャッシュディレクトリ(WEBCACHE)はRAMDISK上に取ることをお勧めします。NereidであればバンクメモリRAMDISKを活用するのが良いでしょう。

WebXpressionでサイトを閲覧する場合は、

    http://webxpressd?http=(httpサイトのURL)

または

    http://webxpressd?https=(httpsサイトのURL)

としてアクセスしてください。

---

## X68000Z で WebXpression.x を利用する際の注意

X68000Z で WebXpression.x version 0.46 を使用して画像ありのページを表示すると画面が乱れます。これは WebXpression.x 側で CRTCに設定している一部のレジスタ値が範囲外のものであるためです。これを修正して X68000Z でも正しく表示できるようにするための差分を以下に置きます。

[WebXpression.bfd](https://github.com/tantanGH/)

ただし完全無保証です。

---

## 制限事項

* JavaScriptを使ったダイナミックなページには対応していません。
* その他たくさん

---

## 変更履歴

* 0.3.0 (2023/09/13) ... HEADの実装改善。WebXpression.xをX68000Zで正常動作させる差分を同梱。
* 0.2.7 (2023/09/10) ... SVG画像に対応。その他細かい修正。
* 0.2.0 (2023/09/09) ... 初版
