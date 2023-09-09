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

として、webxpressdが動いているホストに名前でアクセスできるようにしてください。WebXpressionはIPアドレスでのアクセスには対応していません。

WebXpressionでサイトを閲覧する場合は、

    http://webxpressd?http=(httpサイトのURL)

または

    http://webxpressd?https=(httpsサイトのURL)

としてアクセスしてください。

---

## 制限事項

* JavaScriptを使ったダイナミックなページには対応していません。
* その他たくさん

---

## 変更履歴

* 0.2.0 (2023/09/09) ... 初版
