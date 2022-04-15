# jsut_hiho

## 内容物

* basic5000.txt
    * 漢字混じりのテキストや読み
    * [みんなで作るJSUTコーパスbasic5000](https://tyc.rei-yumesaki.net/material/minnade-jsut/)のコピー
* basic5000_phoneme_openjtalk.txt
    * OpenJTalk用音素列
    * phoneme.pyを実行して取得
* basic5000_modified_openjtalk.txt
    * アクセント情報を手修正するためのテキストファイル
    * script/phoneme.pyを実行して取得したものを手修正
    * 手修正は「なお、次の者は認定講習を受講しなくても、産業保安監督部へ申請し、認定電気工事従事者認定証の交付を受けることができる」まで完了
* basic5000_accent_*_openjtalk.txt
    * [./basic5000_modified_openjtalk.txt]のアクセント情報をonehotベクトルで使いやすいように加工したテキストファイル
    * script/accent_post.pyを実行して取得
    * 現在は最初1000文まで対応

## 謝辞

[JSUT (Japanese speech corpus of Saruwatari-lab., University of Tokyo)](https://sites.google.com/site/shinnosuketakamichi/publication/jsut)

[みんなで作るJSUTコーパスbasic5000](https://tyc.rei-yumesaki.net/material/minnade-jsut/)

## ライセンス

* 拡張子が.txtのファイル　･･･　CC BY-SA 4.0（元データのライセンスを継承）
* それ以外　･･･　[MIT LICENSE](./MIT_LICENSE)
