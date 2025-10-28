import os
import shutil
import time
import platform
import subprocess
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import ctypes  # 移动到顶部，确保跨平台支持

class BrowserCacheCleaner:
    def __init__(self, log_callback=None):
        # 获取当前用户路径
        self.user_profile = os.path.expanduser('~')
        self.os_type = platform.system()
        self.log_callback = log_callback
        
        # 定义各浏览器缓存路径 - 根据不同操作系统设置不同路径
        if self.os_type == 'Windows':
            self.browser_paths = {
                'chrome': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History'),
                    'downloads': os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History Provider Cache')
                },
                'firefox': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
                },
                'edge': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
                },
                'ie': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Windows', 'INetCache'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Cookies')
                },
                '360': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'History')
                },
                '360se': {
                    'cache': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default', 'History')
                }
            }
        else:
            # Linux 路径配置
            self.browser_paths = {
                'chrome': {
                    'cache': os.path.join(self.user_profile, '.cache', 'google-chrome', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, '.config', 'google-chrome', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, '.config', 'google-chrome', 'Default', 'History')
                },
                'firefox': {
                    'cache': os.path.join(self.user_profile, '.cache', 'mozilla', 'firefox'),
                    'cookies': os.path.join(self.user_profile, '.mozilla', 'firefox')
                },
                'edge': {
                    'cache': os.path.join(self.user_profile, '.cache', 'microsoft-edge', 'Default', 'Cache'),
                    'cookies': os.path.join(self.user_profile, '.config', 'microsoft-edge', 'Default', 'Cookies'),
                    'history': os.path.join(self.user_profile, '.config', 'microsoft-edge', 'Default', 'History'),
                    # 额外的Edge浏览器可能路径，适用于不同Linux发行版
                    'cache_alt': os.path.join(self.user_profile, '.cache', 'microsoft-edge-dev', 'Default', 'Cache'),
                    'cookies_alt': os.path.join(self.user_profile, '.config', 'microsoft-edge-dev', 'Default', 'Cookies'),
                    'history_alt': os.path.join(self.user_profile, '.config', 'microsoft-edge-dev', 'Default', 'History')
                },
                # Linux上没有IE和360系列浏览器，所以路径会被自动处理
                'ie': {'cache': '', 'cookies': ''},
                '360': {'cache': '', 'cookies': '', 'history': ''},
                '360se': {'cache': '', 'cookies': '', 'history': ''}
            }
        
    def log(self, message):
        """记录日志信息"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def close_browser_processes(self, browser_ids=None):
        """关闭指定的浏览器进程 - 跨平台实现"""
        # 浏览器标识符到进程名的映射 - 跨平台兼容
        browser_to_process = {
            'chrome': 'chrome.exe' if self.os_type == 'Windows' else 'google-chrome',
            'firefox': 'firefox.exe' if self.os_type == 'Windows' else 'firefox',
            'edge': 'msedge.exe' if self.os_type == 'Windows' else 'microsoft-edge',
            'ie': 'iexplore.exe' if self.os_type == 'Windows' else '',
            '360': '360chrome.exe' if self.os_type == 'Windows' else '',
            '360se': '360se.exe' if self.os_type == 'Windows' else ''
        }
        
        # 如果没有指定浏览器，则关闭所有浏览器进程
        if browser_ids is None:
            browser_ids = list(browser_to_process.keys())
            self.log(f"[系统: {self.os_type}] 开始关闭所有浏览器进程...")
        else:
            # 过滤掉在当前系统上不存在的浏览器
            browser_ids = [id for id in browser_ids if browser_to_process[id]]
            self.log(f"[系统: {self.os_type}] 开始关闭选择的浏览器进程: {', '.join(browser_ids)}...")
        
        for browser_id in browser_ids:
            if browser_id in browser_to_process and browser_to_process[browser_id]:
                process = browser_to_process[browser_id]
                try:
                    if self.os_type == 'Windows':
                        # Windows系统使用taskkill命令
                        subprocess.run(['taskkill', '/F', '/IM', process], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    else:
                        # Linux系统使用pkill命令
                        subprocess.run(['pkill', process], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.log(f"已关闭 {process} 进程")
                except Exception as e:
                    self.log(f"关闭 {process} 进程时出错: {e}")
    
    def clean_chrome_cache(self):
        """清理Chrome浏览器缓存"""
        self.log(f"[系统: {self.os_type}] 开始清理Chrome浏览器缓存...")
        
        paths = ['cache', 'cookies', 'history', 'downloads']
        for path_type in paths:
            if path_type in self.browser_paths['chrome']:
                path = self.browser_paths['chrome'][path_type]
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                            self.log(f"已清理Chrome文件: {path}")
                        elif os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                            self.log(f"已清理Chrome目录: {path}")
                    except Exception as e:
                        self.log(f"清理Chrome {path_type} 时出错: {e}")
        self.log("Chrome浏览器缓存清理完成")
        
    def clean_firefox_cache(self):
        """清理Firefox浏览器缓存"""
        self.log(f"[系统: {self.os_type}] 开始清理Firefox浏览器缓存...")
        
        # 处理Firefox配置文件目录
        profiles_path = self.browser_paths['firefox']['cache']
        if os.path.exists(profiles_path):
            try:
                # 遍历所有配置文件
                for profile in os.listdir(profiles_path):
                    profile_path = os.path.join(profiles_path, profile)
                    if os.path.isdir(profile_path) and profile.endswith('.default'):
                        # Firefox缓存和存储路径
                        cache_dirs = [
                            os.path.join(profile_path, 'cache2'),
                            os.path.join(profile_path, 'storage'),
                            os.path.join(profile_path, 'cookies.sqlite'),
                            os.path.join(profile_path, 'places.sqlite')
                        ]
                        
                        for cache_dir in cache_dirs:
                            if os.path.exists(cache_dir):
                                try:
                                    if os.path.isfile(cache_dir):
                                        os.remove(cache_dir)
                                        self.log(f"已清理Firefox文件: {cache_dir}")
                                    elif os.path.isdir(cache_dir):
                                        shutil.rmtree(cache_dir, ignore_errors=True)
                                        self.log(f"已清理Firefox目录: {cache_dir}")
                                except Exception as e:
                                    self.log(f"清理Firefox缓存时出错: {e}")
            except Exception as e:
                self.log(f"遍历Firefox配置文件时出错: {e}")
        self.log("Firefox浏览器缓存清理完成")
        
    def clean_edge_cache(self):
        """清理Edge浏览器缓存"""
        self.log(f"[系统: {self.os_type}] 开始清理Edge浏览器缓存...")
        
        # 标准路径类型
        paths = ['cache', 'cookies', 'history']
        
        # 对于Linux系统，还需要检查替代路径
        if self.os_type != 'Windows':
            alt_paths = ['cache_alt', 'cookies_alt', 'history_alt']
            paths.extend(alt_paths)
        
        for path_type in paths:
            if path_type in self.browser_paths['edge']:
                path = self.browser_paths['edge'][path_type]
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                            self.log(f"已清理Edge文件: {path}")
                        elif os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                            self.log(f"已清理Edge目录: {path}")
                    except Exception as e:
                        self.log(f"清理Edge {path_type} 时出错: {e}")
        self.log("Edge浏览器缓存清理完成")
        
    def clean_ie_cache(self):
        """清理IE浏览器缓存（仅在Windows系统可用）"""
        if self.os_type == 'Windows':
            self.log("开始清理IE浏览器缓存...")
            
            paths = ['cache', 'cookies']
            for path_type in paths:
                if path_type in self.browser_paths['ie']:
                    path = self.browser_paths['ie'][path_type]
                    if os.path.exists(path):
                        try:
                            if os.path.isfile(path):
                                os.remove(path)
                                self.log(f"已清理IE文件: {path}")
                            elif os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                                self.log(f"已清理IE目录: {path}")
                        except Exception as e:
                            self.log(f"清理IE {path_type} 时出错: {e}")
            self.log("IE浏览器缓存清理完成")
        else:
            self.log("IE浏览器仅在Windows系统可用，跳过清理")
            
    def clean_360_cache(self):
        """清理360浏览器缓存（主要在Windows系统可用）"""
        if self.os_type == 'Windows':
            self.log("开始清理360浏览器缓存...")
            
            paths = ['cache', 'cookies', 'history']
            for path_type in paths:
                if path_type in self.browser_paths['360']:
                    path = self.browser_paths['360'][path_type]
                    if os.path.exists(path):
                        try:
                            if os.path.isfile(path):
                                os.remove(path)
                                self.log(f"已清理360文件: {path}")
                            elif os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                                self.log(f"已清理360目录: {path}")
                        except Exception as e:
                            self.log(f"清理360 {path_type} 时出错: {e}")
            self.log("360浏览器缓存清理完成")
        else:
            self.log("360浏览器主要在Windows系统可用，跳过清理")
            
    def clean_360se_cache(self):
        """清理360极速浏览器缓存"""
        if self.os_type == 'Windows':
            self.log("开始清理360极速浏览器缓存...")
            
            # 360极速浏览器的路径
            se_cache_paths = []
            # 检查是否使用Chrome核心路径
            chrome_core_path = os.path.join(self.user_profile, 'AppData', 'Local', '360Chrome', 'Chrome', 'User Data', 'Default')
            if os.path.exists(chrome_core_path):
                se_cache_paths.extend([
                    os.path.join(chrome_core_path, 'Cache'),
                    os.path.join(chrome_core_path, 'Cookies'),
                    os.path.join(chrome_core_path, 'History')
                ])
            
            # 检查独立路径
            roaming_path = os.path.join(self.user_profile, 'AppData', 'Roaming', '360se6', 'UserData')
            if os.path.exists(roaming_path):
                se_cache_paths.append(roaming_path)
            
            for path in se_cache_paths:
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        else:
                            shutil.rmtree(path, ignore_errors=True)
                        self.log(f"已清理360极速浏览器: {path}")
                    except Exception as e:
                        self.log(f"清理360极速浏览器路径 {path} 时出错: {e}")
            
            self.log("360极速浏览器缓存清理完成")
        else:
            self.log("360极速浏览器主要在Windows系统可用，跳过清理")
            
    def clean_all_browsers(self):
        """清理所有浏览器缓存"""
        self.log(f"[系统: {self.os_type}] 开始清理所有支持的浏览器缓存...")
        
        # 首先关闭所有浏览器进程
        self.close_browser_processes()
        time.sleep(2)  # 等待进程完全关闭
        
        # 根据当前操作系统决定清理哪些浏览器
        browsers_to_clean = {
            'Windows': ['chrome', 'firefox', 'edge', 'ie', '360', '360se'],
            'Linux': ['chrome', 'firefox', 'edge']
        }
        
        # 获取当前系统支持的浏览器列表，如果没有定义则使用默认列表
        supported_browsers = browsers_to_clean.get(self.os_type, ['chrome', 'firefox', 'edge'])
        
        # 创建浏览器ID到清理方法的映射
        browser_to_method = {
            'chrome': self.clean_chrome_cache,
            'firefox': self.clean_firefox_cache,
            'edge': self.clean_edge_cache,
            'ie': self.clean_ie_cache,
            '360': self.clean_360_cache,
            '360se': self.clean_360se_cache
        }
        
        # 执行清理
        for browser_id in supported_browsers:
            if browser_id in browser_to_method:
                browser_to_method[browser_id]()
        
        self.log("\n清理完成！")
        return True

class BrowserCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("浏览器缓存清理工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TButton", font=('SimHei', 10))
        self.style.configure("TLabel", font=('SimHei', 10))
        self.style.configure("TRadiobutton", font=('SimHei', 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        self.title_label = ttk.Label(self.main_frame, text="浏览器缓存清理工具", font=('SimHei', 16, 'bold'))
        self.title_label.pack(pady=10)
        
        # 创建浏览器选择框架
        self.browser_frame = ttk.LabelFrame(self.main_frame, text="选择要清理的浏览器")
        self.browser_frame.pack(fill=tk.X, pady=10)
        
        # 创建浏览器选择选项
        self.browser_vars = {
            'chrome': tk.BooleanVar(value=False),
            'firefox': tk.BooleanVar(value=False),
            'edge': tk.BooleanVar(value=False),
            'ie': tk.BooleanVar(value=False),
            '360': tk.BooleanVar(value=False),
            '360se': tk.BooleanVar(value=False)
        }
        
        # 布局浏览器选择复选框
        row = 0
        col = 0
        for browser, var in self.browser_vars.items():
            browser_name = {
                'chrome': 'Google Chrome',
                'firefox': 'Mozilla Firefox',
                'edge': 'Microsoft Edge',
                'ie': 'Internet Explorer',
                '360': '360安全浏览器',
                '360se': '360极速浏览器'
            }.get(browser, browser)
            
            checkbox = ttk.Checkbutton(self.browser_frame, text=browser_name, variable=var)
            checkbox.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # 添加全选和全取消按钮
        self.select_all_button = ttk.Button(self.browser_frame, text="全选", command=self.select_all)
        self.select_all_button.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.deselect_all_button = ttk.Button(self.browser_frame, text="全取消", command=self.deselect_all)
        self.deselect_all_button.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        
        # 创建日志文本框
        self.log_label = ttk.Label(self.main_frame, text="清理日志:")
        self.log_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=70, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # 创建清理按钮
        self.clean_button = ttk.Button(self.button_frame, text="开始清理", command=self.start_cleaning)
        self.clean_button.pack(side=tk.LEFT, padx=5)
        
        # 创建退出按钮
        self.exit_button = ttk.Button(self.button_frame, text="退出", command=root.quit)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
        # 添加关于按钮
        self.about_button = ttk.Button(self.button_frame, text="关于", command=self.show_about)
        self.about_button.pack(side=tk.RIGHT, padx=5)
        
        # 检查管理员权限
        self.check_admin_permission()
        
    def select_all(self):
        """全选所有浏览器复选框"""
        for var in self.browser_vars.values():
            var.set(True)
            
    def deselect_all(self):
        """全取消所有浏览器复选框"""
        for var in self.browser_vars.values():
            var.set(False)
        
    def check_admin_permission(self):
        """检查是否以管理员权限运行 - 跨平台实现"""
        try:
            os_type = platform.system()
            if os_type == 'Windows':
                # Windows系统检查管理员权限
                is_admin = os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    messagebox.showwarning("权限警告", "请以管理员权限运行此程序，否则可能无法完全清理所有缓存文件。")
            else:
                # Linux系统检查是否为root用户
                try:
                    is_admin = os.geteuid() == 0
                    if not is_admin:
                        messagebox.showwarning("权限警告", "请以root权限运行此程序，否则可能无法完全清理所有缓存文件。")
                except AttributeError:
                    # 某些环境可能不支持geteuid
                    pass
        except Exception as e:
            pass
    
    def log(self, message):
        """在日志文本框中显示消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_cleaning(self):
        """开始清理过程"""
        # 禁用清理按钮防止重复点击
        self.clean_button.config(state=tk.DISABLED)
        
        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 在新线程中执行清理操作，避免UI冻结
        self.clean_thread = threading.Thread(target=self.run_cleaning)
        self.clean_thread.daemon = True
        self.clean_thread.start()
    
    def run_cleaning(self):
        """在后台线程中运行清理操作 - 跨平台实现"""
        cleaner = BrowserCacheCleaner(log_callback=self.log)
        os_type = platform.system()
        self.log(f"[系统: {os_type}] 开始清理浏览器缓存")
        
        # 映射浏览器标识符到浏览器名称
        browser_names = {
            'chrome': 'Google Chrome',
            'firefox': 'Mozilla Firefox',
            'edge': 'Microsoft Edge',
            'ie': 'Internet Explorer',
            '360': '360安全浏览器',
            '360se': '360极速浏览器'
        }
        
        # 根据当前操作系统决定支持的浏览器
        if os_type != 'Windows':
            # 在非Windows系统上自动过滤掉特定浏览器
            for browser in ['ie', '360', '360se']:
                if browser in self.browser_vars:
                    self.browser_vars[browser].set(False)
        
        # 用于跟踪清理结果
        cleaned_browsers = []
        not_cleaned_browsers = []
        
        try:
            # 检查是否选择了至少一个浏览器
            if not any(var.get() for var in self.browser_vars.values()):
                self.root.after(0, lambda: messagebox.showinfo("提示", "请至少选择一个浏览器进行清理。"))
                self.root.after(0, lambda: self.clean_button.config(state=tk.NORMAL))
                return
            
            # 收集用户勾选的浏览器标识符
            selected_browsers = [browser_id for browser_id, var in self.browser_vars.items() if var.get()]
            
            # 只关闭用户勾选的浏览器进程
            cleaner.close_browser_processes(selected_browsers)
            self.root.after(0, lambda: self.log("等待2秒让进程完全关闭..."))
            time.sleep(2)
            
            # 根据选择清理浏览器
            if self.browser_vars['chrome'].get():
                # 检查Chrome浏览器是否存在
                chrome_paths = cleaner.browser_paths['chrome']
                chrome_exists = any(os.path.exists(path) for path_type, path in chrome_paths.items() if path) if chrome_paths else False
                if not chrome_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['chrome']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['chrome'])
                else:
                    cleaner.clean_chrome_cache()
                    cleaned_browsers.append(browser_names['chrome'])
                
            if self.browser_vars['firefox'].get():
                # 检查Firefox浏览器是否存在
                firefox_paths = cleaner.browser_paths['firefox']
                firefox_exists = any(os.path.exists(path) for path_type, path in firefox_paths.items() if path) if firefox_paths else False
                if not firefox_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['firefox']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['firefox'])
                else:
                    cleaner.clean_firefox_cache()
                    cleaned_browsers.append(browser_names['firefox'])
                
            if self.browser_vars['edge'].get():
                # 检查Edge浏览器是否存在
                edge_paths = cleaner.browser_paths['edge']
                edge_exists = any(os.path.exists(path) for path_type, path in edge_paths.items() if path) if edge_paths else False
                if not edge_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['edge']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['edge'])
                else:
                    cleaner.clean_edge_cache()
                    cleaned_browsers.append(browser_names['edge'])
                
            if self.browser_vars['ie'].get() and os_type == 'Windows':
                # 检查IE浏览器是否存在
                ie_paths = cleaner.browser_paths['ie']
                ie_exists = any(os.path.exists(path) for path_type, path in ie_paths.items() if path) if ie_paths else False
                if not ie_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['ie']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['ie'])
                else:
                    cleaner.clean_ie_cache()
                    cleaned_browsers.append(browser_names['ie'])
                
            if self.browser_vars['360'].get() and os_type == 'Windows':
                # 检查360安全浏览器是否存在
                browser360_paths = cleaner.browser_paths['360']
                browser360_exists = any(os.path.exists(path) for path_type, path in browser360_paths.items() if path) if browser360_paths else False
                if not browser360_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['360']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['360'])
                else:
                    cleaner.clean_360_cache()
                    cleaned_browsers.append(browser_names['360'])
                
            if self.browser_vars['360se'].get() and os_type == 'Windows':
                # 检查360极速浏览器是否存在
                browser360se_paths = cleaner.browser_paths['360se']
                # 检查是否存在任何有效的路径
                browser360se_exists = False
                if browser360se_paths:
                    for path_type, path in browser360se_paths.items():
                        if path and os.path.exists(path):
                            browser360se_exists = True
                            break
                    # 检查一些特定的路径
                    if not browser360se_exists and os_type == 'Windows':
                        roaming_path = os.path.join(cleaner.user_profile, 'AppData', 'Roaming', '360se6', 'UserData')
                        browser360se_exists = os.path.exists(roaming_path)
                
                if not browser360se_exists:
                    self.root.after(0, lambda: self.log(f"提示: {browser_names['360se']} 程序未安装所以未清理。"))
                    not_cleaned_browsers.append(browser_names['360se'])
                else:
                    cleaner.clean_360se_cache()
                    cleaned_browsers.append(browser_names['360se'])
            
            # 清理完成后启用按钮并显示提示
            self.root.after(0, lambda: self.log("\n清理完成！"))
            
            # 根据清理结果生成不同的完成提示
            if not cleaned_browsers:
                # 没有成功清理任何浏览器
                result_message = "没有成功清理任何浏览器。\n\n原因可能是：\n"
                if not_cleaned_browsers:
                    result_message += "- 以下浏览器未安装：" + "、".join(not_cleaned_browsers)
                else:
                    result_message += "- 所有选择的浏览器都无法清理（可能权限不足）"
            else:
                # 成功清理了至少一个浏览器
                result_message = "浏览器缓存清理完成！\n\n"
                result_message += "已成功清理的浏览器：" + "、".join(cleaned_browsers) + "\n"
                if not_cleaned_browsers:
                    result_message += "未清理的浏览器（未安装）：" + "、".join(not_cleaned_browsers)
            
            self.root.after(0, lambda: messagebox.showinfo("清理结果", result_message))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"清理过程中发生错误: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"清理过程中发生错误: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.clean_button.config(state=tk.NORMAL))
    
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("300x203")
        about_window.resizable(False, False)
        
        # 居中显示
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 创建内容
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(about_frame, text="浏览器缓存清理工具", font=('SimHei', 12, 'bold')).pack(pady=10)
        ttk.Label(about_frame, text="版本: 1.0.0", font=('SimHei', 10)).pack(pady=5)
        ttk.Label(about_frame, text="清理各种浏览器的缓存和上网痕迹", font=('SimHei', 10)).pack(pady=5)
        ttk.Label(about_frame, text="辽阳中院技术处开发", font=('SimHei', 10)).pack(pady=5)
        
        ttk.Button(about_frame, text="确定", command=about_window.destroy).pack(pady=10)

def main():
    # 创建tkinter根窗口
    root = tk.Tk()
    
    # 创建应用实例
    app = BrowserCleanerApp(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()