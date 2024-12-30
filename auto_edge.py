import tkinter as tk
from tkinter import ttk, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import random
import time
import string
import threading

def load_search_words(file_path):
    try:
        # UTF-8でファイルを読み込み試行
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except UnicodeDecodeError:
        # UTF-8で失敗した場合、Latin-1で試行
        with open(file_path, 'r', encoding='latin-1') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません。")
        return None

def generate_random_search(words):
    if not words:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(3, 8)))
    return random.choice(words)

class BingSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bing Search Automation")
        self.root.geometry("600x400")
        
        # 検索モード選択
        self.mode_frame = ttk.LabelFrame(root, text="検索モード", padding=10)
        self.mode_frame.pack(fill="x", padx=10, pady=5)
        
        self.mode = tk.StringVar(value="desktop")
        ttk.Radiobutton(self.mode_frame, text="デスクトップ (90回)", value="desktop", variable=self.mode).pack(side="left", padx=5)
        ttk.Radiobutton(self.mode_frame, text="モバイル (60回)", value="mobile", variable=self.mode).pack(side="left", padx=5)
        
        # ログ表示エリア
        self.log_area = scrolledtext.ScrolledText(root, height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ボタン
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_button = ttk.Button(self.button_frame, text="検索開始", command=self.start_search)
        self.start_button.pack(side="left", padx=5)
        
        self.quit_button = ttk.Button(self.button_frame, text="終了", command=root.quit)
        self.quit_button.pack(side="right", padx=5)
        
        self.driver = None

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        
    def perform_searches(self, search_words, num_searches, device_type):
        try:
            service = Service(EdgeChromiumDriverManager().install())
            options = Options()
            
            if device_type == "mobile":
                options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15')
            
            self.driver = webdriver.Edge(service=service, options=options)
            self.driver.maximize_window()
            
            self.driver.get("https://rewards.bing.com/")
            time.sleep(5)
            
            for i in range(num_searches):
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                self.driver.get("https://www.bing.com")
                time.sleep(2)
                
                search_box = self.driver.find_element(By.NAME, "q")
                search_term = generate_random_search(search_words)
                
                search_box.clear()
                search_box.send_keys(search_term)
                search_box.send_keys(Keys.RETURN)
                
                self.log(f"{device_type}検索 {i+1}/{num_searches} 完了: {search_term}")
                time.sleep(random.uniform(2, 4))
                
                if i < num_searches - 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
        except Exception as e:
            self.log(f"エラーが発生しました: {e}")
    
    def start_search(self):
        self.start_button["state"] = "disabled"
        self.log_area.delete(1.0, tk.END)
        
        search_words = load_search_words(r"C:\Program Files (x86)\Microsoft\Edge\Application\rockyou.txt")
        if not search_words:
            self.log("デフォルトのランダム文字列を使用します。")
        
        mode = self.mode.get()
        num_searches = 90 if mode == "desktop" else 60
        device_type = "デスクトップ" if mode == "desktop" else "モバイル"
        
        thread = threading.Thread(target=lambda: self.perform_searches(search_words, num_searches, device_type))
        thread.start()
        
        def check_thread():
            if thread.is_alive():
                self.root.after(1000, check_thread)
            else:
                self.start_button["state"] = "normal"
                self.log("\n検索が完了しました。")
        
        check_thread()

if __name__ == "__main__":
    root = tk.Tk()
    app = BingSearchApp(root)
    root.mainloop()