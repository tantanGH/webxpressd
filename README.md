# webxpressd

Preprocessing Service for WebXpression

---

## はじめに

Raspberry Pi OS上で動作する、WebXpressionのためのpreprocessing serviceです。

* 文字コード変換
* httpsサイトへのアクセス
* 未対応タグの除去

などを行います。

---

## Install (git,pip)

git, pip が入っていない場合はインストール。

    sudo apt install git
    sudo apt install pip

---

## Install (webxpressd)

    pip install git+https://github.com/tantanGH/webxpressd.git

---

## 使い方

キャッシュ用ディレクトリを用意します。

    cd
    mkdir -p var/webxpress-cache

起動時にキャッシュディレクトリを指定します。

    webxpressd var/webxpress-cache

デフォルトではポート6803番で待ち受け開始します。

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

JavaScriptを使ったダイナミックなページには対応していません。

---

## 変更履歴

* 0.2.0 (2023/09/09) ... 初版
