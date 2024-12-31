import flet as ft
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import random
import time
import string
import asyncio
from datetime import datetime

# キーワードリスト
KEYWORDS = [
    "shopping", "beat it lyrics", "焼きそば　レシピ", "movie", "近くのマクドナルド",
    "weather", "flight", "hotel", "東京", "東京　不動産", "ドル円", "ups tracking",
    "translate", "ニュース", "job", "health", "game", "nasdaq 100", "ドジャース 速報",
    "誤謬", "trump harris odds", "アメリカ　時間"
]

def load_search_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません。")
        return None

def generate_random_search(words):
    if not words:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(3, 8)))
    return random.choice(words)

class BingSearchApp(ft.UserControl):  # ControlからUserControlに戻す
    def __init__(self):
        super().__init__()
        self.driver = None
        self.is_paused = False
        self.settings_file = "settings.json"
        self.search_history_file = "search_history.json"
        self.load_settings()
        self._init_components()


    def _init_components(self):
        # 時間選択用のドロップダウン
        hours = [str(i).zfill(2) for i in range(24)]
        minutes = [str(i).zfill(2) for i in range(0, 60, 5)]
        
        self.schedule_hour = ft.Dropdown(
            label="時",
            width=100,
            options=[ft.dropdown.Option(hour) for hour in hours],
            value=self.settings.get("schedule_hour", "12")
        )
        
        self.schedule_minute = ft.Dropdown(
            label="分",
            width=100,
            options=[ft.dropdown.Option(minute) for minute in minutes],
            value=self.settings.get("schedule_minute", "00")
        )
        
        self.schedule_time_row = ft.Row([
            ft.Text("実行時刻:"),
            self.schedule_hour,
            ft.Text(":"),
            self.schedule_minute
        ])

        self.schedule_days = ft.Row([
            ft.Checkbox(label="月", value=False),
            ft.Checkbox(label="火", value=False),
            ft.Checkbox(label="水", value=False),
            ft.Checkbox(label="木", value=False),
            ft.Checkbox(label="金", value=False),
            ft.Checkbox(label="土", value=False),
            ft.Checkbox(label="日", value=False)
        ])

        self.schedule_settings = ft.Column([
            self.schedule_time_row,
            ft.Text("実行する曜日"),
            self.schedule_days
        ], visible=False)

        # テーマ切り替えボタン
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="ダークモード切替",
            on_click=self.toggle_theme
        )

        # 検索履歴グラフ
        self.search_chart = ft.BarChart(
            bar_groups=[],
            visible=False,
            width=600,
            height=200
        )

        # 既存のコンポーネントを更新
        self.search_mode = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="desktop", label="デスクトップ (90回)"),
                ft.Radio(value="mobile", label="モバイル (60回)"),
                ft.Radio(value="japanese", label="デイリーキーワード"),
                ft.Radio(value="scheduled", label="スケジュール実行"),
            ]),
            value=self.settings.get("last_mode", "desktop")
        )

        self.file_picker = ft.FilePicker(
            on_result=self.file_picker_result
        )
        
        self.progress = ft.ProgressBar(width=600, visible=False)
        self.counter = ft.Text("0/0", size=16)
        self.log_area = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=12,
            max_lines=12,
            width=600
        )
        
        self.start_button = ft.ElevatedButton(
            text="検索開始",
            on_click=self.start_search
        )
        
        self.pause_button = ft.ElevatedButton(
            text="一時停止",
            on_click=self.toggle_pause,
            visible=False
        )

        self.stop_button = ft.ElevatedButton(
            text="検索停止",
            on_click=self.stop_search,
            visible=False,
            style=ft.ButtonStyle(
                color=ft.Colors.ERROR,  # colorsをColorsに変更
                bgcolor=ft.Colors.ERROR_CONTAINER,  # colorsをColorsに変更
            )
        )

        # スケジューラー設定
        self.scheduler = ft.TimePicker(
            visible=False,
            tooltip="実行時刻を設定"
        )

        # プロキシ設定
        self.proxy_input = ft.TextField(
            label="プロキシ設定",
            tooltip="例: http://proxy:8080",
            visible=False
        )

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Bing Search Automation", size=24, weight=ft.FontWeight.BOLD),
                    self.theme_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.search_chart,
                ft.Row([
                    ft.Text("検索モード", size=20),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip="設定",
                        on_click=self.show_settings
                    )
                ]),
                self.search_mode,
                self.scheduler,
                ft.Row([
                    ft.ElevatedButton(
                        "カスタムキーワード選択",
                        icon=ft.Icons.FILE_UPLOAD,
                        on_click=lambda _: self.file_picker.pick_files()
                    ),
                    ft.ElevatedButton(
                        "検索履歴",
                        icon=ft.Icons.HISTORY,
                        on_click=self.show_history
                    )
                ]),
                self.progress,
                self.counter,
                self.log_area,
                ft.Row([
                    self.start_button,
                    self.pause_button,
                    self.stop_button,
                    ft.ElevatedButton(
                        "終了", 
                        icon=ft.Icons.EXIT_TO_APP,
                        on_click=self.show_exit_dialog
                    )
                ])
            ]),
            padding=20
        )

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK 
            if self.page.theme_mode == ft.ThemeMode.LIGHT 
            else ft.ThemeMode.LIGHT
        )
        self.theme_button.icon = (
            ft.Icons.LIGHT_MODE 
            if self.page.theme_mode == ft.ThemeMode.DARK 
            else ft.Icons.DARK_MODE
        )
        self.page.update()

    def show_history(self, e):
        # 検索履歴を表示
        pass

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.settings["custom_keywords_path"] = file_path
            self.save_settings()
            self.log(f"カスタムキーワードファイルを選択: {file_path}")
    
    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                "last_mode": "desktop",
                "custom_keywords_path": None,
                "schedule_time": "12:00",
                "schedule_days": [False] * 7
            }

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def show_settings(self, e):
        # 設定値を保持するための変数
        self.settings_interval = ft.TextField(
            label="検索間隔(秒)", 
            value=str(self.settings.get("interval", 3))
        )
        self.settings_retry = ft.Checkbox(
            label="エラー時に自動リトライ",
            value=self.settings.get("auto_retry", False)
        )

        dlg = ft.AlertDialog(
            title=ft.Text("設定"),
            content=ft.Column([
                self.settings_interval,
                self.settings_retry,
            ]),
            actions=[
                ft.TextButton("保存", on_click=self.save_settings_dialog),
                ft.TextButton("キャンセル", on_click=lambda e: self.close_settings_dialog(dlg)),
            ],
        )
        self.settings_dialog = dlg
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def save_settings_dialog(self, e):
        # 設定値を取得して保存
        self.settings["interval"] = int(self.settings_interval.value)
        self.settings["auto_retry"] = self.settings_retry.value
        
        # JSONファイルに保存
        self.save_settings()
        
        # ダイアログを閉じる
        self.settings_dialog.open = False
        self.page.update()
        
        # 変更を通知
        self.log("設定を保存しました")

    def close_settings_dialog(self, dlg):
        dlg.open = False
        self.page.update()

    def toggle_pause(self, e):
        self.is_paused = not self.is_paused
        self.pause_button.text = "再開" if self.is_paused else "一時停止"
        self.update()

    def log(self, message):
        self.log_area.value = self.log_area.value + message + "\n"
        self.update()

    async def perform_searches(self, search_words, num_searches, device_type):
        try:
            self.pause_button.visible = True
            self.update()
            
            service = Service(EdgeChromiumDriverManager().install())
            options = Options()
            
            if device_type == "モバイル":
                mobile_ua = 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
                options.add_argument(f'--user-agent={mobile_ua}')
                options.add_argument('--window-size=375,812')
            
            self.driver = webdriver.Edge(service=service, options=options)
            if device_type == "デスクトップ":
                self.driver.maximize_window()
            
            self.driver.get("https://rewards.bing.com/")
            await asyncio.sleep(5)
            
            for i in range(num_searches):
                if self.driver is None:  # 停止ボタンが押された場合
                    return
                    
                # 一時停止中は待機
                while self.is_paused:
                    await asyncio.sleep(1)
                    continue
                    
                try:
                    # プログレスバーの更新
                    self.progress.value = (i + 1) / num_searches
                    self.counter.value = f"{i+1}/{num_searches}"
                    self.progress.visible = True
                    self.update()
                    
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
                    self.driver.get("https://www.bing.com")
                    await asyncio.sleep(2)
                    
                    search_box = None
                    try:
                        search_box = self.driver.find_element(By.NAME, "q")
                    except:
                        search_box = self.driver.find_element(By.ID, "sb_form_q")
                    
                    if search_box:
                        search_term = generate_random_search(search_words)
                        search_box.clear()
                        search_box.send_keys(search_term)
                        search_box.send_keys(Keys.RETURN)
                        
                        self.log(f"{device_type}検索 {i+1}/{num_searches} 完了: {search_term}")
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        if i < num_searches - 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                except Exception as search_error:
                    self.log(f"検索中にエラーが発生しました: {search_error}")
                    if self.settings.get("auto_retry", False):
                        self.log("リトライします...")
                        continue
                    
        except Exception as e:
            self.log(f"エラーが発生しました: {e}")
        finally:
            self.pause_button.visible = False
            self.stop_button.visible = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    async def start_search(self, e):
        self.start_button.disabled = True
        self.stop_button.visible = True
        self.log_area.value = ""
        
        mode = self.search_mode.value
        if mode == "japanese":
            search_words = KEYWORDS
            num_searches = 90
            device_type = "デスクトップ"
        else:
            search_words = load_search_words(r"C:\Program Files (x86)\Microsoft\Edge\Application\rockyou.txt")
            if not search_words:
                self.log("デフォルトのランダム文字列を使用します。")
            num_searches = 90 if mode == "desktop" else 60
            device_type = "デスクトップ" if mode == "desktop" else "モバイル"
        
        await self.perform_searches(search_words, num_searches, device_type)
        self.start_button.disabled = False
        self.log("\n検索が完了しました。")
        self.update()

    def show_exit_dialog(self, e):
        def close_app(e):
            dlg.open = False
            self.page.update()
            self.page.window.close()

        def close_dialog(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("終了確認"),
            content=ft.Text("アプリケーションを終了しますか？"),
            actions=[
                ft.TextButton("はい", on_click=close_app),
                ft.TextButton("いいえ", on_click=close_dialog),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def stop_search(self, e):
        self.is_paused = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
        
        self.pause_button.visible = False
        self.stop_button.visible = False
        self.start_button.disabled = False
        self.progress.visible = False
        self.log("検索を停止しました")
        self.update()

    def schedule_changed(self, e):
        """スケジュール設定が変更されたときの処理"""
        schedule_time = f"{self.schedule_hour.value}:{self.schedule_minute.value}"
        schedule_days = [cb.value for cb in self.schedule_days.controls]
        
        self.settings["schedule_time"] = schedule_time
        self.settings["schedule_hour"] = self.schedule_hour.value
        self.settings["schedule_minute"] = self.schedule_minute.value
        self.settings["schedule_days"] = schedule_days
        self.save_settings()
        self.log(f"スケジュール設定を更新: {schedule_time}, {schedule_days}")

    async def check_schedule(self):
        """スケジュールされた時間に検索を実行"""
        while True:
            if self.search_mode.value == "scheduled":
                now = datetime.now()
                try:
                    schedule_time = datetime.strptime(
                        self.settings["schedule_time"], 
                        "%H:%M"
                    ).time()
                    
                    if (now.time().hour == schedule_time.hour and 
                        now.time().minute == schedule_time.minute and
                        self.settings["schedule_days"][now.weekday()]):
                        self.log("スケジュール実行を開始します")
                        await self.start_search(None)
                except ValueError:
                    self.log("スケジュール時刻の形式が不正です")
                
            await asyncio.sleep(60)

async def main(page: ft.Page):
    try:
        page.title = "Bing Search Automation"
        
        # ウィンドウの初期設定（新しいAPI）
        page.window.width = 600
        page.window.height = 800
        page.window.center()
        page.window.resizable = False
        page.window.maximized = False
        page.window.minimized = False
        
        app = BingSearchApp()
        page.add(app)
        page.overlay.append(app.file_picker)
        
        # スケジュールチェッカーを非同期で開始
        asyncio.create_task(app.check_schedule())
        
        await page.update_async()
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    ft.app(target=main)