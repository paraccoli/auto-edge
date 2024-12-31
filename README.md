# 計画
1. READMEの更新
   - インストール手順の更新
   - 実行ファイル作成手順の更新
   - スケジュール機能の説明追加
   - 設定オプションの更新

```markdown


# Bing Search Automation

Microsoft Edgeを使用してBing検索を自動化するツールです。

## 機能
- デスクトップモード (90回検索)
- モバイルモード (60回検索)
- デイリーキーワード検索
- スケジュール実行（時間・曜日指定可能）
- カスタム検索ワードリスト対応
- ダークモード対応
- 検索の一時停止/再開
- GUI インターフェース

## インストール手順

### 必要条件
- Python 3.6以上
- Microsoft Edge
- pip (Pythonパッケージマネージャー)

### 依存パッケージのインストール
```bash
pip install selenium webdriver-manager flet pyinstaller
```

## 使用方法

### 1. 実行ファイルの作成
管理者権限のPowerShellで以下を実行:
```powershell
# リアルタイム保護を一時的に無効化
Set-MpPreference -DisableRealtimeMonitoring $true

# EXEファイルのビルド
pyinstaller --onefile --noconsole --icon=icon.ico auto_edge.py

# リアルタイム保護を再度有効化
Set-MpPreference -DisableRealtimeMonitoring $false
```

### 2. 検索ワードリストの設定
`rockyou.txt`を以下の場所に配置:
```
C:\Program Files (x86)\Microsoft\Edge\Application\rockyou.txt
```

### 3. アプリケーションの起動
1. 

dist

フォルダ内の`auto_edge.exe`を実行
2. 検索モードを選択
3. 必要に応じて設定を変更
4. 「検索開始」ボタンをクリック

## 設定オプション

### 検索モード
- デスクトップモード: PC向け90回検索
- モバイルモード: スマートフォン向け60回検索
- デイリーキーワード: 定義済みキーワードで検索
- スケジュール実行: 指定時刻に自動実行

### スケジュール設定
- 実行時刻: 24時間形式で設定
- 実行曜日: 複数曜日選択可能
- 設定の永続化対応

### その他の設定
- 検索間隔: 2-4秒（ランダム）
- エラー時の自動リトライ
- ダークモード切替
- 検索の一時停止/再開

## トラブルシューティング

### よくあるエラー
1. WebDriverエラー
   - Edge WebDriverの再インストール
   - Microsoft Edgeの更新

2. ファイル読み込みエラー
   - `rockyou.txt`の文字エンコーディングをUTF-8に変更
   - ファイルパスの確認

3. 実行権限エラー
   - 管理者権限で実行

### その他の注意点
- アンチウイルスソフトの誤検知に注意
- スケジュール実行時はアプリケーションを終了しない

## 免責事項
本ツールの使用はMicrosoftの利用規約に違反する可能性があります。自己責任でご使用ください。
```