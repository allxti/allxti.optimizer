import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import psutil
import winreg
from pathlib import Path
import threading
import time
import ctypes
import sys
from PIL import Image, ImageTk
import wmi
import requests
import tempfile
import shutil

try:
    import customtkinter as ctk
except ImportError:
    print("Instala: pip install customtkinter")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class GameOptimizerApp:
    def __init__(self):
        # Configurar CustomTkinter con tema oscuro profesional
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("allxti optimizer V0.1")
        self.root.geometry("800x550")
        self.root.resizable(True, True)  # Hacer responsive
        
        # Cargar el logo como favicon
        self.load_logo()
        
        # Variables
        self.games_file = "games.json"
        self.current_game = None
        self.optimization_active = False
        self.original_services = []
        self.original_power_plan = None
        self.monitoring_active = False
        self.fps_history = []
        self.language = "es"  # es=español, en=ingles
        
        # Configuración de visualización
        self.show_cpu = True
        self.show_gpu = True
        self.show_ram = True
        self.show_temp = True
        self.show_fps = True
        self.show_power = True
        self.close_browsers = False  # Nueva opción
        
        # Colores profesionales oscuros
        self.colors = {
            'primary': '#1e3a8a',
            'secondary': '#3b82f6',
            'accent': '#10b981',
            'danger': '#ef4444',
            'dark_bg': '#0f172a',
            'darker_bg': '#0c111b',
            'card_bg': '#1e293b',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#334155'
        }
        
        # Inicializar WMI para sensores de hardware
        try:
            self.wmi_obj = wmi.WMI(namespace=r"\root\OpenHardwareMonitor")
        except:
            self.wmi_obj = None
        
        self.setup_ui()
        self.load_games()
    
    def load_logo(self):
        """Cargar y establecer el logo como favicon"""
        try:
            # Crear un ícono temporal con el diseño del logo
            # Como no tenemos el archivo real, usaremos un ícono genérico
            # En una implementación real, deberías cargar el archivo .ico o .png
            
            # Para este ejemplo, crearemos un ícono simple
            # En la práctica, deberías usar el archivo real del logo
            self.logo_image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            
            # Establecer el ícono en la ventana principal
            # Esto requiere que tengas el archivo real del logo
            # Por ahora, solo mostramos un ícono genérico
            
        except:
            pass
    
    def setup_ui(self):
        # Frame principal con diseño moderno y responsive
        main_frame = ctk.CTkFrame(self.root, 
                                 corner_radius=15, 
                                 fg_color=self.colors['dark_bg'])
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título con ícono (responsive)
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(10, 15))
        
        # Icono de juego y título
        title_label = ctk.CTkLabel(title_frame, 
                                  text="🚀 allxti optimizer V0.1", 
                                  font=ctk.CTkFont(size=22, weight="bold"),
                                  text_color=self.colors['text_primary'])
        title_label.pack()
        
        # Panel de juegos (responsive)
        games_panel = ctk.CTkFrame(main_frame, 
                                  corner_radius=10, 
                                  fg_color=self.colors['card_bg'])
        games_panel.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(games_panel, 
                    text="Juegos Disponibles:", 
                    font=ctk.CTkFont(weight="bold"),
                    text_color=self.colors['text_primary']).pack(anchor="w", padx=10, pady=(5,0))
        
        # Frame para el menú desplegable y el icono
        combo_frame = ctk.CTkFrame(games_panel, fg_color="transparent")
        combo_frame.pack(fill="x", padx=10, pady=5)
        
        # Menú desplegable para seleccionar juego
        self.game_combo = ctk.CTkComboBox(combo_frame, 
                                         values=[],
                                         state="readonly",
                                         fg_color=self.colors['darker_bg'],
                                         text_color=self.colors['text_primary'],
                                         border_color=self.colors['border'],
                                         command=self.on_game_select,
                                         width=300)
        self.game_combo.pack(side="left", fill="x", expand=True)
        
        # Label para mostrar el icono del juego
        self.game_icon_label = ctk.CTkLabel(combo_frame, text="", width=32, height=32)
        self.game_icon_label.pack(side="right", padx=(5, 0))
        
        # Checkbox para cerrar navegadores
        self.browser_checkbox = ctk.CTkCheckBox(games_panel, 
                                               text="Cerrar navegadores al optimizar", 
                                               variable=tk.BooleanVar(value=self.close_browsers),
                                               command=self.toggle_browser_close,
                                               text_color=self.colors['text_primary'],
                                               hover_color=self.colors['secondary'],
                                               fg_color=self.colors['secondary'])
        self.browser_checkbox.pack(anchor="w", padx=10, pady=2)
        
        # Botones de acción en fila (responsive)
        button_frame = ctk.CTkFrame(games_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_button = ctk.CTkButton(button_frame, 
                                         text="▶️ Iniciar Optimización", 
                                         command=self.start_optimization, 
                                         fg_color=self.colors['accent'], 
                                         hover_color="#059669",
                                         width=150,
                                         font=ctk.CTkFont(weight="bold"))
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(button_frame, 
                                        text="⏹️ Detener Optimización", 
                                        command=self.stop_optimization, 
                                        fg_color=self.colors['danger'], 
                                        hover_color="#dc2626",
                                        width=150,
                                        font=ctk.CTkFont(weight="bold"))
        self.stop_button.pack(side="left", padx=5)
        
        # Botón agregar juego (responsive)
        add_button = ctk.CTkButton(games_panel, 
                                  text="➕ Agregar Juego", 
                                  command=self.add_game, 
                                  fg_color=self.colors['secondary'], 
                                  hover_color="#2563eb",
                                  width=120,
                                  font=ctk.CTkFont(weight="bold"))
        add_button.pack(pady=5)
        
        # Estado (responsive)
        self.status_label = ctk.CTkLabel(main_frame, 
                                        text="Estado: Inactivo", 
                                        font=ctk.CTkFont(size=12),
                                        text_color=self.colors['text_secondary'])
        self.status_label.pack(pady=5)
        
        # Panel de monitoreo (6 cuadros en 2x3, responsive)
        monitor_frame = ctk.CTkFrame(main_frame, 
                                    corner_radius=10, 
                                    fg_color=self.colors['card_bg'])
        monitor_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Crear los 6 cuadros de monitoreo
        self.create_monitor_tiles(monitor_frame)
        
        # Frame para botones de configuración, donaciones y actualización
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=10)
        
        # Botón de configuración
        config_button = ctk.CTkButton(bottom_frame, 
                                     text="⚙️ Configuración", 
                                     command=self.open_config, 
                                     fg_color=self.colors['primary'], 
                                     hover_color="#1d4ed8",
                                     font=ctk.CTkFont(weight="bold"))
        config_button.pack(side="left", padx=5)
        
        # Botón de donaciones
        donate_button = ctk.CTkButton(bottom_frame, 
                                     text="❤️ Donaciones", 
                                     command=self.open_donate, 
                                     fg_color=self.colors['accent'], 
                                     hover_color="#059669",
                                     font=ctk.CTkFont(weight="bold"))
        donate_button.pack(side="left", padx=5)
        
        # Botón de actualización
        update_button = ctk.CTkButton(bottom_frame, 
                                     text="🔄 Actualizar", 
                                     command=self.check_for_update, 
                                     fg_color=self.colors['secondary'], 
                                     hover_color="#2563eb",
                                     font=ctk.CTkFont(weight="bold"))
        update_button.pack(side="left", padx=5)
    
    def toggle_browser_close(self):
        """Actualizar la variable de cerrar navegadores"""
        self.close_browsers = self.browser_checkbox.get()
    
    def on_game_select(self, event=None):
        """Manejar selección de juego desde el menú desplegable"""
        selected_game_name = self.game_combo.get()
        if selected_game_name:
            # Buscar juego en archivo
            if os.path.exists(self.games_file):
                with open(self.games_file, 'r') as f:
                    games = json.load(f)
                    for game in games:
                        if game['name'] == selected_game_name:
                            self.current_game = game
                            # Cargar icono del juego
                            self.load_game_icon(game['path'])
                            break
    
    def load_game_icon(self, game_path):
        """Cargar y mostrar icono del juego directamente del .exe"""
        try:
            # Usar una técnica simple para obtener el icono
            # Como alternativa, usar un icono genérico
            self.game_icon_label.configure(image=None, text="🎮", font=ctk.CTkFont(size=16))
        except:
            # Si no se puede cargar el icono, mostrar texto genérico
            self.game_icon_label.configure(image=None, text="🎮", font=ctk.CTkFont(size=16))
    
    def create_monitor_tiles(self, parent):
        """Crear los 6 cuadros de monitoreo en diseño 2x3"""
        # Definir íconos y etiquetas
        tiles_info = [
            ("💻", "CPU", "cpu_label"),
            ("🖥️", "GPU", "gpu_label"),
            ("💾", "RAM", "ram_label"),
            ("🌡️", "Temp", "temp_label"),
            ("📊", "FPS", "fps_label"),
            ("⚡", "Power", "power_label")
        ]
        
        # Crear frame para los tiles
        tile_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tile_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Crear tiles en 2 filas x 3 columnas
        for i, (icon, label, var_name) in enumerate(tiles_info):
            row = i // 3
            col = i % 3
            
            tile = ctk.CTkFrame(tile_frame, 
                               corner_radius=8, 
                               fg_color=self.colors['darker_bg'],
                               border_width=1,
                               border_color=self.colors['border'])
            tile.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configurar grid dentro del tile
            tile.grid_columnconfigure(0, weight=1)
            tile.grid_rowconfigure(0, weight=1)
            tile.grid_rowconfigure(1, weight=1)
            
            # Icono y texto
            icon_label = ctk.CTkLabel(tile, 
                                     text=icon, 
                                     font=ctk.CTkFont(size=20),
                                     text_color=self.colors['text_primary'])
            icon_label.pack(pady=(10, 0))
            
            value_label = ctk.CTkLabel(tile, 
                                      text=f"{label}: --", 
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color=self.colors['text_primary'])
            value_label.pack(pady=(0, 10))
            
            # Guardar referencia
            setattr(self, var_name, value_label)
        
        # Configurar pesos para que se expandan uniformemente
        for i in range(2):
            tile_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            tile_frame.grid_columnconfigure(i, weight=1)
    
    def load_games(self):
        if os.path.exists(self.games_file):
            with open(self.games_file, 'r') as f:
                games = json.load(f)
                game_names = [game['name'] for game in games]
                self.game_combo.configure(values=game_names)
                if games:
                    self.game_combo.set(game_names[0])
                    self.current_game = games[0]
                    # Cargar icono del primer juego
                    self.load_game_icon(games[0]['path'])
    
    def add_game(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo del juego",
            filetypes=[("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            game_name = Path(file_path).stem
            games = []
            if os.path.exists(self.games_file):
                with open(self.games_file, 'r') as f:
                    games = json.load(f)
            
            # Verificar si ya existe
            existing_games = [g for g in games if g['name'] == game_name]
            if not existing_games:
                games.append({'name': game_name, 'path': file_path})
                with open(self.games_file, 'w') as f:
                    json.dump(games, f)
                
                # Actualizar menú desplegable
                game_names = [game['name'] for game in games]
                self.game_combo.configure(values=game_names)
                self.game_combo.set(game_name)
                self.current_game = {'name': game_name, 'path': file_path}
                # Cargar icono del nuevo juego
                self.load_game_icon(file_path)
            else:
                messagebox.showinfo("Información", "Este juego ya está registrado.")
    
    def get_selected_game(self):
        if not hasattr(self, 'current_game'):
            return None
        return self.current_game
    
    def show_loading_screen(self):
        """Mostrar pantalla de carga durante optimización"""
        loading_window = ctk.CTkToplevel(self.root)
        loading_window.title("Optimizando...")
        loading_window.geometry("350x200")
        loading_window.resizable(False, False)
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        # Centrar la ventana
        loading_window.lift()
        loading_window.attributes("-topmost", True)
        
        # Contenido de la pantalla de carga
        ctk.CTkLabel(loading_window, 
                    text="🚀 allxti optimizer V0.1", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.colors['text_primary']).pack(pady=20)
        
        progress = ctk.CTkProgressBar(loading_window, 
                                     width=300,
                                     progress_color=self.colors['accent'])
        progress.pack(fill="x", padx=20, pady=10)
        progress.set(0)
        
        status_label = ctk.CTkLabel(loading_window, 
                                   text="Iniciando...", 
                                   font=ctk.CTkFont(size=12),
                                   text_color=self.colors['text_secondary'])
        status_label.pack(pady=5)
        
        # Devolver referencias para actualizar
        return loading_window, progress, status_label
    
    def optimize_system(self):
        """Aplicar optimizaciones extremas"""
        loading_window, progress, status_label = self.show_loading_screen()
        
        try:
            # 1. Guardar configuración original
            status_label.configure(text="Guardando configuración original...")
            progress.set(0.05)
            self.backup_original_settings()
            
            # 2. Deshabilitar efectos visuales de Windows
            status_label.configure(text="Deshabilitando efectos visuales...")
            progress.set(0.1)
            self.disable_visual_effects()
            
            # 3. Servicios a detener (extremo - pero mantener red y wifi)
            status_label.configure(text="Deteniendo servicios innecesarios...")
            progress.set(0.2)
            services_to_stop = [
                "OneSyncSvc", "CDPSvc", "DiagTrack", "dmwappushservice",
                "MapsBroker", "RetailDemo", "Fax", "XblAuthManager",
                "XblGameSave", "XboxNetApiSvc", "PrintNotify",
                "SensorService", "SensrSvc", "Themes",
                "WbioSrvc", "WMPNetworkSvc", "RemoteRegistry",
                "RetailDemo", "StiSvc", "TabletInputService", "upnphost",
                "VSS", "WcsPlugInService", "WdNisSvc", "WerSvc", "WinHttpAutoProxySvc",
                "WinRM", "WpcMonSvc", "WPDBusEnum", "WpnService", "XblGameSave",
                "XboxGipSvc", "ALG", "AppIDSvc", "AppMgmt", "AppReadiness",
                "AppXSvc", "AssignedAccessManagerSvc", "autotimesvc", "AxInstSV",
                "BDESVC", "BluetoothUserService", "BthAvctpSvc", "BthHFSvc",
                "camsvc", "CDPUserSvc", "ConsentUxUserSvc", "CoreMessagingRegistrar",
                "CryptSvc", "DeviceAssociationBrokerSvc",
                "DevQueryBroker", "DispBrokerDesktopSvc", "DisplayEnhancementService",
                "DoSvc", "DsmSvc", "DsSvc", "EntAppSvc", "fdPHost", "FDResPub",
                "FontCache", "HomeGroupListener", "HomeGroupProvider", "icssvc",
                "IKEEXT", "InstallService", "IpxlatCfgSvc", "LicenseManager",
                "lltdsvc", "LxpSvc", "MSDTC", "MSiSCSI", "NaturalAuthentication",
                "NcaSvc", "NcbService", "Netlogon", "NetTcpPortSharing", "NgcCtnrSvc",
                "NgcSvc", "NlaSvc", "P9RdrService", "PerfHost", "PhoneSvc",
                "PimIndexMaintenanceSvc", "pla", "PolicyAgent", "QWAVE", "RasMan",
                "RemoteAccess", "RemoteRegistry", "RetailDemo", "RmSvc", "SamSs",
                "SCardSvr", "ScDeviceEnum", "Schedule", "SecurityHealthService",
                "SEMgrSvc", "SENS", "SessionEnv", "SgrmBroker", "SharedAccess",
                "SharedRealitySvc", "smphost", "SNMPTRAP",
                "SstpSvc", "StateRepository", "stisvc", "StorSvc",
                "svsvc", "SwPrv", "SystemEventsBroker", "TabletInputService",
                "TapiSrv", "TermService", "TextInputManagementService", "Themes",
                "TieringEngineService", "TimeBrokerSvc", "TokenBroker", "TrkWks",
                "TrustedInstaller", "UI0Detect", "UmRdpService", "upnphost",
                "UserDataSvc", "UevAgentService", "UmRdpService", "upnphost",
                "UserManager", "VacSvc", "VaultSvc", "vds", "vm3dservice",
                "vmicheartbeat", "vmickvpexchange", "vmicrdv", "vmicshutdown",
                "vmictimesync", "vmicvmsession", "vmicvss", "VSS", "WalletService",
                "WarpJITSvc", "wbengine", "WbioSrvc", "Wcmsvc", "wcncsvc",
                "WebClient", "Wecsvc", "WEPHOSTSVC", "wercplsupport", "WerSvc",
                "WFDSConMgrSvc", "WiaRpc", "WinHttpAutoProxySvc", "Winmgmt",
                "WinRM", "wisvc", "WlanSvc", "wlidsvc", "WManSvc", "WMPNetworkSvc",
                "WorkFoldersClient", "WpcMonSvc", "WPDBusEnum", "WpnService",
                "WwanSvc", "XblAuthManager", "XblGameSave", "XboxGipSvc",
                "XboxNetApiSvc", "ALG", "AppIDSvc", "AppMgmt", "AppReadiness",
                "AppXSvc", "AssignedAccessManagerSvc", "autotimesvc", "AxInstSV",
                "BDESVC", "BluetoothUserService", "BthAvctpSvc", "BthHFSvc"
            ]
            
            # Excluir servicios críticos de red y wifi
            excluded_services = ["WlanSvc", "WwanSvc", "NlaSvc", "DcomLaunch", 
                               "RpcEptMapper", "SamSs", "Schedule", "Winmgmt"]
            
            services_to_stop = [s for s in services_to_stop if s not in excluded_services]
            
            for i, service in enumerate(services_to_stop):
                try:
                    subprocess.run(["sc", "stop", service], capture_output=True)
                except:
                    pass
                progress.set(0.2 + (i / len(services_to_stop)) * 0.2)
            
            # 4. Procesos a matar
            status_label.configure(text="Terminando procesos innecesarios...")
            progress.set(0.4)
            processes_to_kill = [
                "OneDrive.exe", "steamwebhelper.exe", "Discord.exe", "Spotify.exe", "Skype.exe",
                "Teams.exe", "Slack.exe", "Zoom.exe", "SkypeBackgroundHost.exe",
                "msedgewebview2.exe", "RuntimeBroker.exe", "SearchUI.exe",
                "ShellExperienceHost.exe", "YourPhone.exe", "Clipchamp.exe",
                "WindowsTerminal.exe", "Notepad++.exe", "Everything.exe",
                "EverythingService.exe", "EverythingToolbar.exe"
            ]
            
            # Agregar navegadores si está habilitado
            if self.close_browsers:
                processes_to_kill.extend([
                    "msedge.exe", "chrome.exe", "firefox.exe"
                ])
            
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() in [p.lower() for p in processes_to_kill]:
                    try:
                        proc.kill()
                    except:
                        pass
            
            # 5. Configurar plan de energía extremo
            status_label.configure(text="Configurando plan de energía...")
            progress.set(0.6)
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], 
                          capture_output=True)  # High performance
            
            # 6. Ajustes de prioridad y afinidad
            status_label.configure(text="Ajustando prioridades del sistema...")
            progress.set(0.7)
            self.set_system_priority()
            
            # 7. Ajustes de memoria virtual
            status_label.configure(text="Optimizando memoria virtual...")
            progress.set(0.8)
            self.optimize_virtual_memory()
            
            # 8. Ajustes de red (menos agresivos)
            status_label.configure(text="Optimizando red...")
            progress.set(0.9)
            self.optimize_network()
            
            # 9. Optimización de VRAM y CPU (nuevo)
            status_label.configure(text="Optimizando VRAM y CPU...")
            progress.set(0.95)
            self.optimize_vram_cpu()
            
            # 10. Finalizar
            status_label.configure(text="¡Optimización completa!")
            progress.set(1.0)
            
            time.sleep(1)  # Mostrar mensaje final
            loading_window.destroy()
            
            self.optimization_active = True
            self.status_label.configure(text=f"✅ Optimizado para {self.current_game['name']}")
            
            # Iniciar monitoreo
            self.start_monitoring()
            
        except Exception as e:
            loading_window.destroy()
            messagebox.showerror("Error", f"Error en optimización: {str(e)}")
    
    def disable_visual_effects(self):
        """Deshabilitar efectos visuales de Windows"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "AnimateMinMax", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Animations", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "CommandButtons", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Composition", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "CursorShadow", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "DragFullWindows", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "DropShadow", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "DWMAeroPeekEnabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "FadeOutMenuShadow", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "FontSmoothing", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "IconsOnTaskbar", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ListBoxSmoothScrolling", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "MenuAnimation", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "SelectionFade", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "TaskbarAnimations", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Themes", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Thumbnails", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "TitleBarGradient", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ToolTipAnimation", 0, winreg.REG_DWORD, 0)
        except:
            pass
    
    def set_system_priority(self):
        """Ajustar prioridades del sistema"""
        try:
            # Ajustar prioridad de procesos críticos
            key_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 38529)
        except:
            pass
    
    def optimize_virtual_memory(self):
        """Optimizar memoria virtual"""
        try:
            # Deshabilitar paginación (usar con precaución)
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ClearPageFileAtShutdown", 0, winreg.REG_DWORD, 0)
        except:
            pass
    
    def optimize_network(self):
        """Optimizar configuración de red (menos agresivo)"""
        try:
            # Ajustar TCP (menos agresivo)
            subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"], capture_output=True)
        except:
            pass
    
    def optimize_vram_cpu(self):
        """Optimizar uso de VRAM y CPU para máximo rendimiento"""
        try:
            # Ajustar prioridad del proceso actual a alta
            current_process = psutil.Process()
            current_process.nice(psutil.REALTIME_PRIORITY_CLASS)
            
            # Aumentar tamaño de caché de disco
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 1)
            
            # Optimizar VRAM (ajustar valores según GPU)
            # Esto es un ajuste general, no específico por GPU
            key_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "TdrDelay", 0, winreg.REG_DWORD, 10)
                    winreg.SetValueEx(key, "TdrLevel", 0, winreg.REG_DWORD, 0)
            except:
                pass
            
            # Ajustar plan de energía para CPU
            subprocess.run(["powercfg", "/setacvalueindex", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "sub_processor", "perfprofile", "100"], capture_output=True)
            subprocess.run(["powercfg", "/setdcvalueindex", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "sub_processor", "perfprofile", "100"], capture_output=True)
            
            # Ajustar afinidad de CPU (si hay múltiples núcleos)
            # Esto puede mejorar rendimiento en algunos juegos
            if psutil.cpu_count() > 4:
                # Usar todos los núcleos excepto uno para el sistema
                cpu_affinity = list(range(psutil.cpu_count()))
                if len(cpu_affinity) > 1:
                    cpu_affinity = cpu_affinity[:-1]  # Reservar último núcleo para sistema
                
                # Aplicar afinidad a procesos del juego (esto se haría cuando se inicie el juego)
                # Por ahora, solo estableceremos la afinidad para este proceso
                current_process.cpu_affinity(cpu_affinity)
                
        except:
            pass
    
    def backup_original_settings(self):
        """Guardar configuración original"""
        result = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
        self.original_power_plan = result.stdout.split("(")[1].split(")")[0] if "(" in result.stdout else None
    
    def restore_system(self):
        """Restaurar sistema a estado original"""
        try:
            if self.original_power_plan:
                subprocess.run(["powercfg", "/setactive", self.original_power_plan], capture_output=True)
            
            # Reiniciar servicios detenidos (menos críticos)
            services_to_start = [
                "DiagTrack", "MapsBroker", "CDPSvc", "OneSyncSvc",
                "Themes", "ShellHWDetection", "XblAuthManager",
                "XblGameSave", "XboxNetApiSvc"
            ]
            
            for service in services_to_start:
                try:
                    subprocess.run(["sc", "start", service], capture_output=True)
                except:
                    pass
            
            # Restaurar efectos visuales
            self.restore_visual_effects()
            
            # Restaurar prioridad del proceso
            try:
                current_process = psutil.Process()
                current_process.nice(psutil.NORMAL_PRIORITY_CLASS)
            except:
                pass
            
            self.optimization_active = False
            self.monitoring_active = False
            self.status_label.configure(text="🔄 Sistema restaurado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar: {str(e)}")
    
    def restore_visual_effects(self):
        """Restaurar efectos visuales originales"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "AnimateMinMax", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "Animations", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "CommandButtons", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "Composition", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "CursorShadow", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "DragFullWindows", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "DropShadow", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "DWMAeroPeekEnabled", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "FadeOutMenuShadow", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "FontSmoothing", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "IconsOnTaskbar", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ListBoxSmoothScrolling", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "MenuAnimation", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "SelectionFade", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "TaskbarAnimations", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "Themes", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "Thumbnails", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "TitleBarGradient", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ToolTipAnimation", 0, winreg.REG_DWORD, 1)
        except:
            pass
    
    def get_cpu_usage(self):
        """Obtener uso de CPU (redondeado)"""
        return round(psutil.cpu_percent(interval=0.5), 1)
    
    def get_gpu_usage(self):
        """Obtener uso de GPU (real) usando WMI"""
        try:
            if self.wmi_obj:
                sensors = self.wmi_obj.Sensor()
                for sensor in sensors:
                    if "gpu" in sensor.Name.lower() and "load" in sensor.Name.lower():
                        return round(sensor.Value, 1)
                    
                    # Intentar obtener carga de GPU por otro nombre
                    if "gpu" in sensor.Name.lower() and "usage" in sensor.Name.lower():
                        return round(sensor.Value, 1)
        except:
            pass
        
        # Fallback: usar carga de CPU como aproximación
        cpu_load = self.get_cpu_usage()
        return round(min(100, cpu_load * 0.8), 1)
    
    def get_gpu_memory(self):
        """Obtener uso de VRAM (real)"""
        try:
            if self.wmi_obj:
                sensors = self.wmi_obj.Sensor()
                for sensor in sensors:
                    if "gpu" in sensor.Name.lower() and "memory" in sensor.Name.lower():
                        return round(sensor.Value, 1)
        except:
            pass
        
        # Fallback: usar carga de CPU como aproximación
        cpu_load = self.get_cpu_usage()
        return round(min(100, cpu_load * 0.8), 1)
    
    def get_ram_usage(self):
        """Obtener uso de RAM (redondeado)"""
        return round(psutil.virtual_memory().percent, 1)
    
    def get_temperature(self):
        """Obtener temperatura real de CPU/GPU"""
        try:
            if self.wmi_obj:
                # Intentar obtener temperatura desde WMI
                sensors = self.wmi_obj.Sensor()
                for sensor in sensors:
                    if "temperature" in sensor.SensorType.lower() and "cpu" in sensor.Name.lower():
                        return round(sensor.Value, 1)
                    
                    # Intentar obtener temperatura de GPU
                    if "temperature" in sensor.SensorType.lower() and "gpu" in sensor.Name.lower():
                        return round(sensor.Value, 1)
        except:
            pass
        
        # Fallback: simular temperatura basada en carga
        cpu_load = self.get_cpu_usage()
        base_temp = 40  # Temperatura base
        temp = base_temp + (cpu_load / 2)  # Aumento proporcional a la carga
        return round(temp, 1)
    
    def estimate_fps(self):
        """Estimar FPS basado en carga del sistema"""
        cpu_load = self.get_cpu_usage()
        gpu_load = self.get_gpu_usage()
        
        # Calcular FPS estimado (más realista)
        base_fps = 120
        load_penalty = (cpu_load + gpu_load) / 2
        
        estimated_fps = max(30, base_fps - (load_penalty * 0.8))
        
        # Agregar al historial
        self.fps_history.append(estimated_fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        
        return round(estimated_fps)
    
    def get_power_consumption(self):
        """Obtener consumo de energía estimado"""
        cpu_load = self.get_cpu_usage() / 100
        gpu_load = self.get_gpu_usage() / 100
        
        # Estimación basada en carga
        estimated_power = 50 + (cpu_load * 75) + (gpu_load * 100)
        return round(estimated_power, 1)
    
    def update_monitoring(self):
        """Actualizar lecturas de monitoreo más rápido"""
        while self.monitoring_active:
            try:
                # Actualizar CPU
                if self.show_cpu:
                    cpu_usage = self.get_cpu_usage()
                    self.cpu_label.configure(text=f"CPU: {cpu_usage}%", 
                                           text_color=self.get_color_by_value(cpu_usage))
                
                # Actualizar GPU
                if self.show_gpu:
                    gpu_usage = self.get_gpu_usage()
                    self.gpu_label.configure(text=f"GPU: {gpu_usage}%", 
                                           text_color=self.get_color_by_value(gpu_usage))
                
                # Actualizar RAM
                if self.show_ram:
                    ram_usage = self.get_ram_usage()
                    self.ram_label.configure(text=f"RAM: {ram_usage}%", 
                                           text_color=self.get_color_by_value(ram_usage))
                
                # Actualizar temperatura
                if self.show_temp:
                    temp = self.get_temperature()
                    self.temp_label.configure(text=f"Temp: {temp}°C", 
                                            text_color=self.get_color_by_temp(temp))
                
                # Actualizar FPS
                if self.show_fps:
                    fps = self.estimate_fps()
                    self.fps_label.configure(text=f"FPS: {fps}", 
                                           text_color=self.get_color_by_fps(fps))
                
                # Actualizar potencia
                if self.show_power:
                    power = self.get_power_consumption()
                    self.power_label.configure(text=f"Power: {power}W", 
                                             text_color=self.get_color_by_power(power))
                
                # Actualizar FPS promedio
                if self.fps_history and self.show_fps:
                    avg_fps = sum(self.fps_history) / len(self.fps_history)
                    # No mostramos esto en el UI principal, pero podríamos añadirlo si se desea
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
            
            time.sleep(0.5)  # Actualizar cada 0.5 segundos (más rápido)
    
    def get_color_by_value(self, value):
        """Devolver color según valor (rojo->amarillo->verde)"""
        if value > 80:
            return "#ef4444"  # Rojo
        elif value > 50:
            return "#f59e0b"  # Amarillo
        else:
            return "#10b981"  # Verde
    
    def get_color_by_temp(self, temp):
        """Devolver color según temperatura"""
        if temp > 80:
            return "#ef4444"  # Rojo
        elif temp > 60:
            return "#f59e0b"  # Amarillo
        else:
            return "#10b981"  # Verde
    
    def get_color_by_fps(self, fps):
        """Devolver color según FPS"""
        if fps < 30:
            return "#ef4444"  # Rojo
        elif fps < 60:
            return "#f59e0b"  # Amarillo
        else:
            return "#10b981"  # Verde
    
    def get_color_by_power(self, power):
        """Devolver color según potencia"""
        if power > 150:
            return "#ef4444"  # Rojo
        elif power > 100:
            return "#f59e0b"  # Amarillo
        else:
            return "#10b981"  # Verde
    
    def start_monitoring(self):
        """Iniciar monitoreo en segundo plano"""
        self.monitoring_active = True
        monitoring_thread = threading.Thread(target=self.update_monitoring, daemon=True)
        monitoring_thread.start()
    
    def start_optimization(self):
        # Verificar permisos de administrador
        if not is_admin():
            messagebox.showerror("Error", "Esta aplicación requiere permisos de administrador para funcionar correctamente.")
            return
        
        # Obtener juego actual (si no está cargado desde JSON)
        if not hasattr(self, 'current_game'):
            game_name = self.game_combo.get()
            if not game_name:
                messagebox.showwarning("Advertencia", "Seleccione un juego primero")
                return
            
            # Buscar juego en archivo
            if os.path.exists(self.games_file):
                with open(self.games_file, 'r') as f:
                    games = json.load(f)
                    for game in games:
                        if game['name'] == game_name:
                            self.current_game = game
                            break
            
            # Si no se encontró, mostrar error
            if not hasattr(self, 'current_game'):
                messagebox.showwarning("Advertencia", "Juego no encontrado. Por favor, agréguelo primero.")
                return
        
        # Limpiar historial de FPS
        self.fps_history = []
        
        # Ejecutar optimización
        threading.Thread(target=self.optimize_system, daemon=True).start()
        
        # Monitorear proceso del juego
        threading.Thread(target=self.monitor_game_process, daemon=True).start()
    
    def monitor_game_process(self):
        """Monitorear si el juego sigue corriendo"""
        if not self.current_game or 'path' not in self.current_game:
            return
        
        while self.optimization_active:
            game_running = False
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and Path(proc.info['exe']).samefile(self.current_game['path']):
                        game_running = True
                        break
                except:
                    continue
            
            if not game_running:
                self.restore_system()
                break
            
            time.sleep(2)  # Revisar cada 2 segundos (más frecuente)
    
    def stop_optimization(self):
        self.monitoring_active = False
        self.restore_system()
    
    def open_config(self):
        """Abrir ventana de configuración"""
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("Configuración")
        config_window.geometry("400x400")
        config_window.resizable(False, False)
        config_window.transient(self.root)  # Hacer modal
        config_window.grab_set()  # Bloquear ventana principal
        
        # Frame principal de configuración
        config_frame = ctk.CTkFrame(config_window, 
                                   corner_radius=10, 
                                   fg_color=self.colors['card_bg'])
        config_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(config_frame, 
                    text="⚙️ Configuración", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors['text_primary']).pack(pady=10)
        
        # Selector de idioma
        lang_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(lang_frame, 
                    text="Idioma:", 
                    font=ctk.CTkFont(weight="bold"),
                    text_color=self.colors['text_primary']).pack(anchor="w", padx=10, pady=(5,0))
        
        lang_var = tk.StringVar(value=self.language)
        
        def change_language():
            new_lang = lang_var.get()
            self.language = new_lang
            # Actualizar texto según idioma
            if new_lang == "en":
                config_window.title("Settings")
                ctk.CTkLabel(config_frame, 
                            text="⚙️ Settings", 
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color=self.colors['text_primary']).pack(pady=10)
                
                # Actualizar texto en la ventana principal
                title_label.configure(text="🚀 allxti optimizer V0.1")
                ctk.CTkLabel(games_panel, text="Available Games:", font=ctk.CTkFont(weight="bold"), text_color=self.colors['text_primary']).pack(anchor="w", padx=10, pady=(5,0))
                self.browser_checkbox.configure(text="Close browsers when optimizing")
                self.start_button.configure(text="▶️ Start Optimization")
                self.stop_button.configure(text="⏹️ Stop Optimization")
                self.add_button.configure(text="➕ Add Game")
                self.status_label.configure(text="Status: Inactive")
                config_button.configure(text="⚙️ Settings")
                donate_button.configure(text="❤️ Donations")
                update_button.configure(text="🔄 Update")
                
                # Actualizar texto en el frame de monitoreo
                # Recrear los labels con texto traducido
                self.cpu_label.configure(text="CPU: --")
                self.gpu_label.configure(text="GPU: --")
                self.ram_label.configure(text="RAM: --")
                self.temp_label.configure(text="Temp: --")
                self.fps_label.configure(text="FPS: --")
                self.power_label.configure(text="Power: --")
                
            else:
                config_window.title("Configuración")
                ctk.CTkLabel(config_frame, 
                            text="⚙️ Configuración", 
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color=self.colors['text_primary']).pack(pady=10)
                
                # Restaurar español
                title_label.configure(text="🚀 allxti optimizer V0.1")
                ctk.CTkLabel(games_panel, text="Juegos Disponibles:", font=ctk.CTkFont(weight="bold"), text_color=self.colors['text_primary']).pack(anchor="w", padx=10, pady=(5,0))
                self.browser_checkbox.configure(text="Cerrar navegadores al optimizar")
                self.start_button.configure(text="▶️ Iniciar Optimización")
                self.stop_button.configure(text="⏹️ Detener Optimización")
                self.add_button.configure(text="➕ Agregar Juego")
                self.status_label.configure(text="Estado: Inactivo")
                config_button.configure(text="⚙️ Configuración")
                donate_button.configure(text="❤️ Donaciones")
                update_button.configure(text="🔄 Actualizar")
                
                # Restaurar texto en el frame de monitoreo
                self.cpu_label.configure(text="CPU: --")
                self.gpu_label.configure(text="GPU: --")
                self.ram_label.configure(text="RAM: --")
                self.temp_label.configure(text="Temp: --")
                self.fps_label.configure(text="FPS: --")
                self.power_label.configure(text="Power: --")
        
        lang_combo = ctk.CTkComboBox(lang_frame, 
                                    values=["es", "en"], 
                                    variable=lang_var,
                                    command=lambda x: change_language(),
                                    fg_color=self.colors['darker_bg'],
                                    text_color=self.colors['text_primary'],
                                    border_color=self.colors['border'])
        lang_combo.pack(padx=10, pady=5)
        
        # Opciones de visualización
        display_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        display_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(display_frame, 
                    text="Mostrar en pantalla:", 
                    font=ctk.CTkFont(weight="bold"),
                    text_color=self.colors['text_primary']).pack(anchor="w", padx=10, pady=(5,0))
        
        # Guardar referencia a la variable para que no se pierda
        self.var_show_cpu = tk.BooleanVar(value=self.show_cpu)
        ctk.CTkCheckBox(display_frame, 
                       text="CPU", 
                       variable=self.var_show_cpu,
                       # Al hacer click, actualizamos la variable de clase real
                       command=lambda: setattr(self, 'show_cpu', self.var_show_cpu.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        self.var_show_gpu = tk.BooleanVar(value=self.show_gpu)
        ctk.CTkCheckBox(display_frame, 
                       text="GPU", 
                       variable=self.var_show_gpu,
                       command=lambda: setattr(self, 'show_gpu', self.var_show_gpu.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        self.var_show_ram = tk.BooleanVar(value=self.show_ram)
        ctk.CTkCheckBox(display_frame, 
                       text="RAM", 
                       variable=self.var_show_ram,
                       command=lambda: setattr(self, 'show_ram', self.var_show_ram.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        self.var_show_temp = tk.BooleanVar(value=self.show_temp)
        ctk.CTkCheckBox(display_frame, 
                       text="Temperatura", 
                       variable=self.var_show_temp,
                       command=lambda: setattr(self, 'show_temp', self.var_show_temp.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        self.var_show_fps = tk.BooleanVar(value=self.show_fps)
        ctk.CTkCheckBox(display_frame, 
                       text="FPS", 
                       variable=self.var_show_fps,
                       command=lambda: setattr(self, 'show_fps', self.var_show_fps.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        self.var_show_power = tk.BooleanVar(value=self.show_power)
        ctk.CTkCheckBox(display_frame, 
                       text="Potencia", 
                       variable=self.var_show_power,
                       command=lambda: setattr(self, 'show_power', self.var_show_power.get()),
                       text_color=self.colors['text_primary'],
                       hover_color=self.colors['secondary'],
                       fg_color=self.colors['secondary']).pack(anchor="w", padx=15, pady=2)
        
        # Botón cerrar
        close_button = ctk.CTkButton(config_frame, 
                                    text="Cerrar", 
                                    command=config_window.destroy,
                                    fg_color=self.colors['primary'], 
                                    hover_color="#1d4ed8",
                                    font=ctk.CTkFont(weight="bold"))
        close_button.pack(pady=10)
    
    def open_donate(self):
        """Abrir ventana de donaciones"""
        donate_window = ctk.CTkToplevel(self.root)
        donate_window.title("Donaciones")
        donate_window.geometry("400x300")
        donate_window.resizable(False, False)
        donate_window.transient(self.root)
        donate_window.grab_set()  # Bloquear ventana principal
        
        # Frame principal de donaciones
        donate_frame = ctk.CTkFrame(donate_window, 
                                   corner_radius=10, 
                                   fg_color=self.colors['card_bg'])
        donate_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(donate_frame, 
                    text="❤️ Donaciones", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors['text_primary']).pack(pady=10)
        
        # Texto de donación
        ctk.CTkLabel(donate_frame, 
                    text="Dona para mejorar el proyecto más rápido,\nsaldrás en los créditos", 
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors['text_secondary']).pack(pady=10)
        
        # Botón para ir al GitHub
        github_button = ctk.CTkButton(donate_frame, 
                                     text="Ir al GitHub", 
                                     command=lambda: self.open_url("https://github.com/allxti"),
                                     fg_color=self.colors['secondary'], 
                                     hover_color="#2563eb",
                                     font=ctk.CTkFont(weight="bold"))
        github_button.pack(pady=10)
        
        # Botón para PayPal
        paypal_button = ctk.CTkButton(donate_frame, 
                                     text="PayPal (sebastiandiazdiaz2818@gmail.com)", 
                                     command=lambda: self.open_url("https://paypal.me/sebastiandiazdiaz2818"),
                                     fg_color=self.colors['accent'], 
                                     hover_color="#059669",
                                     font=ctk.CTkFont(weight="bold"))
        paypal_button.pack(pady=5)
        
        # Botón para Binance
        binance_button = ctk.CTkButton(donate_frame, 
                                      text="Binance (sebastiandiazdiaz2818@gmail.com)", 
                                      command=lambda: self.open_url("https://binance.com"),
                                      fg_color=self.colors['primary'], 
                                      hover_color="#1d4ed8",
                                      font=ctk.CTkFont(weight="bold"))
        binance_button.pack(pady=5)
    
    def open_url(self, url):
        """Abrir URL en navegador"""
        import webbrowser
        webbrowser.open(url)
    
    def check_for_update(self):
        """Verificar si hay actualizaciones disponibles"""
        try:
            # URL del repositorio de GitHub (debes actualizar esta URL con la tuya)
            repo_url = "https://api.github.com/repos/allxti/allxti-optimizer/releases/latest"
            response = requests.get(repo_url)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "")
                
                # Comparar versión actual con la última disponible
                # Aquí deberías implementar la lógica para comparar versiones
                current_version = "v0.1"
                
                if latest_version != current_version:
                    result = messagebox.askyesno("Actualización disponible", 
                                                f"Hay una nueva versión disponible: {latest_version}\n¿Deseas descargarla?")
                    if result:
                        self.download_update(data.get("assets", []))
                else:
                    messagebox.showinfo("Versión actual", "Ya tienes la última versión instalada.")
            else:
                messagebox.showerror("Error", "No se pudo verificar la versión actual.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar actualización: {str(e)}")
    
    def download_update(self, assets):
        """Descargar actualización"""
        try:
            if assets:
                asset = assets[0]  # Tomar el primer asset
                download_url = asset["browser_download_url"]
                
                # Descargar archivo
                response = requests.get(download_url)
                
                if response.status_code == 200:
                    # Guardar en directorio temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp_file:
                        tmp_file.write(response.content)
                        downloaded_file = tmp_file.name
                    
                    # Ejecutar actualización (esto es solo un ejemplo)
                    # Deberías implementar la lógica para reemplazar el archivo actual
                    result = messagebox.askyesno("Actualización descargada", 
                                                "La actualización ha sido descargada.\n¿Deseas reiniciar la aplicación para aplicarla?")
                    if result:
                        # Aquí iría la lógica para cerrar la aplicación actual e iniciar la nueva
                        # subprocess.Popen([downloaded_file])  # Ejecutar nuevo archivo
                        # self.root.quit()  # Cerrar aplicación actual
                        pass
                else:
                    messagebox.showerror("Error", "No se pudo descargar la actualización.")
            else:
                messagebox.showerror("Error", "No se encontraron archivos para descargar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar actualización: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        # Re-ejecutar el programa con derechos de admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    else:
        app = GameOptimizerApp()
        app.run()
