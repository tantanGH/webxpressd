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

## Install (chromium)

webexpressd は Chromium を使います。かなりサイズが大きいものなので、新規のSDカードに最新の Raspberry Pi OS Lite (32bit) を導入し、そこへ導入することをお勧めします。

    sudo apt update
    sudo apt install chromium-chromedriver

---

## Install (git,pip)

    sudo apt install git
    sudo apt install pip

---

## Install (webxpressd)

    pip install git+https://github.com/tantanGH/webxpressd.git

一般ユーザが予約ポートで待ち受けできるように、pythonの実効ファイルに対して特別な許可を与えます。

    ls -alF /usr/bin/python3
    sudo setcap CAP_NET_BIND_SERVICE+ep /usr/bin/python3.9

これはWebXpressionが80番以外のポートへのアクセスをサポートしていないためです。

---

## 使い方

    webxpressd

でポート80番で待ち受け開始します。

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

ページ内リンクや埋め込み画像にはまだ対応していません。

---

## 変更履歴

* 0.2.0 (2023/09/09) ... 初版
