# Bing Search Automation

Microsoft Edgeを使用してBing検索を自動化するツールです。

## 機能
- デスクトップモード (90回検索)
- モバイルモード (60回検索)
- カスタム検索ワードリスト対応
- GUIインターフェース

## インストール手順

### 必要条件
- Python 3.6以上
- Microsoft Edge
- pip (Pythonパッケージマネージャー)

### 依存パッケージのインストール
```bash
pip install selenium
pip install webdriver-manager
pip install pyinstaller
```

## 使用方法

### 1. 実行ファイルの作成
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "BingSearchAutomation" --clean auto_edge.py
```

### 2. 検索ワードリストの設定
`rockyou.txt`を以下の場所に配置:
```
C:\Program Files (x86)\Microsoft\Edge\Application\rockyou.txt
```

### 3. アプリケーションの起動
1. `dist`フォルダ内の`BingSearchAutomation.exe`を実行
2. 検索モードを選択（デスクトップ/モバイル）
3. 「検索開始」ボタンをクリック

## 設定オプション

### 検索モード
- デスクトップモード: PC向けユーザーエージェントで90回検索
- モバイルモード: スマートフォン向けユーザーエージェントで60回検索

### カスタマイズ可能な項目
- 検索間隔: 2-4秒（ランダム）
- 検索ワードリスト: テキストファイルで管理

## トラブルシューティング

### よくあるエラー
1. WebDriverエラー
   - Edge WebDriverの再インストールを試してください
   - Microsoft Edgeを最新版に更新してください

2. ファイル読み込みエラー
   - `rockyou.txt`の文字エンコーディングをUTF-8に変更
   - ファイルパスの確認

3. 実行権限エラー
   - 管理者権限で実行してください


## 免責事項
本ツールの使用はMicrosoftの利用規約に違反する可能性があります。自己責任でご使用ください。本ツールの使用により生じた損害について、当方は一切の責任を負いかねます。