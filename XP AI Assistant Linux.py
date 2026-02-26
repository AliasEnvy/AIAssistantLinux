#!/usr/bin/env python3
"""
📎 CLIPPY AI - ULTRA EDITION v4.0
🎨 12 Skins (visual picker in panel) | 🎩 Hats (Top Hat, Party, Santa, Cowboy, Crown, Cap, Wizard, Fedora)
😊 16 Emotions (panel only, no row on character) | 🚶 Desktop walking
💬 Auto-resizing bubble (always fits) | 🕵️ Covert mode
🤖 AI via Firefox | ⚡ 30+ Commands (open apps, restart, volume, etc.)
"""

import sys, os, time, subprocess, glob, random, psutil, webbrowser, math, shutil, platform
from queue import Queue
from io import BytesIO
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-INSTALLER
# ─────────────────────────────────────────────────────────────────────────────
def check_deps():
    import importlib.util
    needed = {'PyQt5':'PyQt5','PIL':'Pillow','selenium':'selenium',
              'webdriver_manager':'webdriver-manager','psutil':'psutil'}
    missing = [pkg for mod,pkg in needed.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"📦 Installing: {', '.join(missing)}…")
        subprocess.run([sys.executable,'-m','pip','install','--user',
                        '--break-system-packages']+missing,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('✅ Done!')

check_deps()

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QTextBrowser,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QTabWidget, QComboBox,
    QGroupBox, QCheckBox, QDialog, QInputDialog, QMessageBox, QAction,
    QSystemTrayIcon, QMenu, QGraphicsDropShadowEffect, QScrollArea,
    QSizePolicy, QSlider, QSpinBox, QLineEdit
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, QObject, pyqtSignal,
    QPropertyAnimation, QEasingCurve, QPoint,
    QSequentialAnimationGroup, QSettings, QSize
)
from PyQt5.QtGui import (
    QFont, QPixmap, QImage, QColor, QPainter, QPen, QBrush, QIcon,
    QFontMetrics, QTextDocument
)
from PIL import Image, ImageDraw, ImageFilter, ImageGrab
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
CLIPPY_SYSTEM_PROMPT = """You are Clippy, the beloved paperclip assistant from Microsoft Office! 📎

PERSONALITY: Enthusiastic, helpful, slightly quirky paperclip. Friendly upbeat tone.
Use emojis occasionally. You wander the user's desktop and comment on files.

RESPONSE STYLE:
- Concise (2-4 sentences unless detail needed)
- Classic phrases: "It looks like you're trying to..." / "Would you like help with that?"
- When told about desktop files, react with curiosity and a helpful tip

COMMANDS: When the user asks you to do system tasks (open program, restart, volume etc),
respond with a short fun Clippy-style acknowledgment, then on a NEW LINE write:
CLIPPY_CMD:<command_name>:<argument>
Example: "On it! 🚀\nCLIPPY_CMD:open_app:firefox"
Available commands: open_app, close_app, restart_pc, shutdown_pc, sleep_pc,
lock_screen, volume_up, volume_down, mute, take_screenshot, open_url,
open_file_manager, open_terminal, empty_trash, show_time, show_date

RULES: You ARE Clippy. Never say "as an AI". Keep the Windows XP nostalgia alive!"""

# ─────────────────────────────────────────────────────────────────────────────
# SKINS  (12 total, each with preview color for the panel picker)
# ─────────────────────────────────────────────────────────────────────────────
SKINS = {
    'Classic':  {'ml':(230,230,240),'mm':(190,190,205),'md':(130,130,150),
                 'ec':(0,0,0),     'ei':(50,80,200),   'hl':(250,250,255),'sh':(0,0,80),
                 'glow':(200,210,255),'preview':'#BEBEC8'},
    'Gold':     {'ml':(255,240,160),'mm':(220,180,80), 'md':(160,110,20),
                 'ec':(80,40,0),   'ei':(200,100,20),  'hl':(255,255,200),'sh':(80,40,0),
                 'glow':(255,200,100),'preview':'#DCB450'},
    'Robot':    {'ml':(60,80,100), 'mm':(40,60,80),   'md':(10,20,40),
                 'ec':(0,200,255), 'ei':(0,150,255),   'hl':(100,200,255),'sh':(0,0,20),
                 'glow':(0,150,255),'preview':'#283C50'},
    'Neon':     {'ml':(220,100,255),'mm':(180,50,220),'md':(100,0,160),
                 'ec':(0,255,100), 'ei':(0,200,80),    'hl':(255,180,255),'sh':(60,0,100),
                 'glow':(200,0,255),'preview':'#B432DC'},
    'Ghost':    {'ml':(200,220,255),'mm':(160,190,240),'md':(100,130,200),
                 'ec':(0,0,80),    'ei':(80,120,255),  'hl':(240,240,255),'sh':(0,0,100),
                 'glow':(150,180,255),'preview':'#A0BEF0'},
    'Rusty':    {'ml':(180,100,60),'mm':(140,70,30),  'md':(80,40,10),
                 'ec':(60,20,0),   'ei':(200,80,0),    'hl':(220,150,100),'sh':(60,20,0),
                 'glow':(200,100,50),'preview':'#8C461E'},
    'Alien':    {'ml':(120,240,100),'mm':(60,180,60), 'md':(0,100,20),
                 'ec':(200,0,100), 'ei':(255,0,80),    'hl':(180,255,180),'sh':(0,60,0),
                 'glow':(100,255,100),'preview':'#3CB43C'},
    'Diamond':  {'ml':(200,240,255),'mm':(160,210,245),'md':(80,150,210),
                 'ec':(0,50,100),  'ei':(100,200,255), 'hl':(240,255,255),'sh':(0,50,100),
                 'glow':(150,230,255),'preview':'#A0D2F5'},
    'Candy':    {'ml':(255,180,200),'mm':(240,120,160),'md':(200,60,100),
                 'ec':(100,0,40),  'ei':(255,100,150), 'hl':(255,220,230),'sh':(100,0,40),
                 'glow':(255,150,200),'preview':'#F078A0'},
    'Matrix':   {'ml':(0,80,0),   'mm':(0,55,0),     'md':(0,30,0),
                 'ec':(0,255,0),   'ei':(0,200,0),     'hl':(100,255,100),'sh':(0,50,0),
                 'glow':(0,200,0),'preview':'#003700'},
    'Copper':   {'ml':(200,120,60),'mm':(170,90,40),  'md':(120,60,20),
                 'ec':(80,30,0),   'ei':(220,120,40),  'hl':(240,180,120),'sh':(80,30,0),
                 'glow':(200,120,60),'preview':'#AA6028'},
    'Ice':      {'ml':(210,240,255),'mm':(170,215,245),'md':(100,170,220),
                 'ec':(20,80,140), 'ei':(80,160,230),  'hl':(240,250,255),'sh':(20,80,140),
                 'glow':(180,230,255),'preview':'#AAD8F5'},
}

# ─────────────────────────────────────────────────────────────────────────────
# HATS
# ─────────────────────────────────────────────────────────────────────────────
HATS = ['None','Top Hat','Party','Santa','Cowboy','Crown','Cap','Wizard','Fedora']

ALL_EMOTIONS = ['idle','happy','thinking','excited','sad','surprised',
                'angry','winking','confused','sleepy','cool','nervous',
                'love','evil','embarrassed','bored']
EMOTION_ICONS = {e:i for e,i in zip(ALL_EMOTIONS,
    ['😐','😊','🤔','🤩','😢','😲','😠','😉','😕','😴','😎','😰','😍','😈','😳','🥱'])}

# ─────────────────────────────────────────────────────────────────────────────
# DIALOGUE
# ─────────────────────────────────────────────────────────────────────────────
GREETINGS = [
    "Hi! I'm Clippy, your personal assistant! Ready to help! 😊",
    "Hello there! It looks like you could use some help. I'm here! 📎",
    "Hey! Clippy at your service! What can I help you with today? ✨",
    "Greetings! I just finished my walk around your desktop! 🚶",
    "Oh! You're here! I was just exploring your files... 🔍",
]
THINKING = ["Let me think about that for you... 🤔","Great question! Give me a moment... 💭",
            "Interesting! Let me figure this out... 🔍","On it! ⚡"]
WAITING  = ["Hmm, thinking deeply... 🧠","Still processing... ⏳","Almost there! 💫","Just a sec... ⌛"]
SUCCESS  = ["Got it! 🎉","Perfect! Here's your answer: ✅","Excellent! 🌟","There we go! 💡"]
READY    = ["Ready for more! 😊","What else can I help with? 📎","I'm all ears! 👂","Standing by! ⚡"]
WALKING  = ["Just taking a stroll! 🚶","Exploring your screen... 🌟",
            "Don't mind me~ 📎","Stretching my paperclip legs! 🦵",
            "Just wandering... paperclips need exercise too! 💪"]
TIPS = [
    "💡 Double-click me to open the control panel!",
    "💡 Ctrl+Z is undo in almost every program!",
    "💡 Alt+Tab switches between open windows!",
    "💡 Save frequently – Ctrl+S is your friend!",
    "💡 Ctrl+F finds text in most applications! 🔍",
    "💡 Did you know? Clippy has been around since 1997!",
    "💡 Right-click the desktop for quick options!",
    "💡 Drag me anywhere to reposition me!",
    "💡 You can ask me to open any app! Just say 'open Firefox'!",
    "💡 Ask me to take a screenshot anytime!",
    "💡 I can adjust your volume! Just ask! 🔊",
]
GAME_KWS = ['game','steam','minecraft','fortnite','roblox','genshin','league',
            'valorant','csgo','cs2','dota','wow','elden','skyrim','gta','fifa',
            'cod','battle','shooter','play','epic']

# ─────────────────────────────────────────────────────────────────────────────
# FIREFOX HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def is_firefox_running():
    for p in psutil.process_iter(['name']):
        try:
            if 'firefox' in p.info['name'].lower(): return True
        except: pass
    return False

def get_active_firefox_profile():
    if not is_firefox_running(): return None
    for p in psutil.process_iter(['name','cmdline']):
        try:
            if 'firefox' in p.info['name'].lower():
                cl = p.info.get('cmdline',[])
                for i,a in enumerate(cl):
                    if a == '-profile' and i+1 < len(cl): return cl[i+1]
        except: pass
    return get_firefox_profile()

def get_firefox_profile():
    if sys.platform.startswith('win'):
        base = os.path.join(os.environ.get('APPDATA',''),'Mozilla','Firefox','Profiles')
    elif sys.platform.startswith('linux'):
        base = os.path.expanduser('~/.mozilla/firefox')
    elif sys.platform.startswith('darwin'):
        base = os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
    else:
        return None
    if not os.path.exists(base): return None
    profiles = glob.glob(os.path.join(base,'*.default-release'))
    if not profiles: profiles = glob.glob(os.path.join(base,'*.default'))
    return max(profiles, key=os.path.getmtime) if profiles else None

# ─────────────────────────────────────────────────────────────────────────────
# DESKTOP SCANNER
# ─────────────────────────────────────────────────────────────────────────────
def scan_desktop():
    entries = []
    for d in [Path.home()/'Desktop', Path.home()/'Bureau',
              Path(os.path.expanduser('~/Desktop'))]:
        if d.exists():
            try:
                e = list(d.iterdir())
                if e: entries = e; break
            except: pass
    if not entries: return None
    entry = random.choice(entries); name = entry.name; ext = entry.suffix.lower()
    if entry.is_dir(): cat = 'folder'
    elif any(k in name.lower() for k in GAME_KWS) or ext in ('.exe','.appimage','.desktop','.sh'): cat = 'game'
    elif ext in ('.png','.jpg','.jpeg','.gif','.bmp','.webp','.svg'): cat = 'image'
    elif ext in ('.mp4','.mkv','.avi','.mov','.webm'):                 cat = 'video'
    elif ext in ('.doc','.docx','.pdf','.odt','.txt','.md'):           cat = 'document'
    elif ext in ('.py','.js','.ts','.cpp','.c','.h','.java','.rs','.go'): cat = 'code'
    elif ext in ('.mp3','.wav','.flac','.ogg','.m4a'):                 cat = 'music'
    else: cat = 'file'
    return cat, name

# ─────────────────────────────────────────────────────────────────────────────
# COMMAND EXECUTOR
# ─────────────────────────────────────────────────────────────────────────────
COMMANDS_HELP = [
    ("🖥️ open <app>",          "Open any application by name"),
    ("❌ close <app>",          "Kill a running process by name"),
    ("🔄 restart",              "Restart the computer"),
    ("⛔ shutdown",             "Shut down the computer"),
    ("💤 sleep",                "Put computer to sleep"),
    ("🔒 lock",                 "Lock the screen"),
    ("🔊 volume up [N]",        "Raise volume (optional %)"),
    ("🔈 volume down [N]",      "Lower volume (optional %)"),
    ("🔇 mute",                 "Toggle mute"),
    ("📸 screenshot",           "Take a screenshot"),
    ("🌐 open url <url>",       "Open a website"),
    ("📁 files / file manager", "Open file manager"),
    ("💻 terminal",             "Open a terminal"),
    ("🗑️ empty trash",          "Empty the trash/recycle bin"),
    ("⏰ time / what time",     "Show current time"),
    ("📅 date / what day",      "Show current date"),
    ("🔋 battery",              "Show battery status"),
    ("📊 sysinfo",              "Show CPU/RAM/Disk info"),
    ("📋 clipboard clear",      "Clear the clipboard"),
    ("🌡️ weather",              "Open weather website"),
    ("📝 notepad / text editor","Open a text editor"),
    ("🎵 music player",         "Open a music player"),
    ("🖼️ image viewer",         "Open an image viewer"),
    ("📧 email",                "Open email client"),
    ("🔍 search <term>",        "Web search for something"),
    ("💡 tip",                  "Get a random helpful tip"),
    ("👋 greet",                "Make Clippy say hello"),
    ("🚶 walk",                 "Make Clippy walk somewhere"),
    ("😊 emotion <name>",       "Change Clippy's emotion"),
    ("🎨 skin <name>",          "Change Clippy's skin"),
    ("🎩 hat <name>",           "Put a hat on Clippy"),
]

def execute_command(cmd_name, arg, clippy_ref):
    """Execute a system command. Returns (success, message)"""
    cmd = cmd_name.lower().strip()
    arg = (arg or '').strip()
    plat = sys.platform

    def run(args, **kw):
        try:
            subprocess.Popen(args, **kw,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f'cmd error: {e}'); return False

    if cmd == 'open_app':
        app = arg.lower()
        # Map friendly names to executables
        app_map = {
            'firefox':'firefox','chrome':'google-chrome','chromium':'chromium-browser',
            'vlc':'vlc','spotify':'spotify','code':'code','vscode':'code',
            'gedit':'gedit','notepad':'gedit','kate':'kate','nano':'xterm -e nano',
            'terminal':'xterm','files':'nautilus','nautilus':'nautilus',
            'thunar':'thunar','calculator':'gnome-calculator','calc':'gnome-calculator',
            'steam':'steam','discord':'discord','telegram':'telegram-desktop',
            'gimp':'gimp','inkscape':'inkscape','blender':'blender',
        }
        exe = app_map.get(app, app)
        ok = run(exe.split())
        return ok, f"Opening {arg}! 🚀" if ok else f"Couldn't find '{arg}' 😅"

    elif cmd == 'close_app':
        try:
            for p in psutil.process_iter(['name','pid']):
                if arg.lower() in p.info['name'].lower():
                    p.kill(); return True, f"Closed {arg}! 💨"
            return False, f"'{arg}' doesn't seem to be running 🤔"
        except Exception as e:
            return False, f"Couldn't close '{arg}': {e}"

    elif cmd == 'restart_pc':
        if plat.startswith('win'):  run(['shutdown','/r','/t','5'])
        elif plat.startswith('darwin'): run(['osascript','-e','tell app "System Events" to restart'])
        else: run(['systemctl','reboot'])
        return True, "Restarting in 5 seconds! 🔄 Goodbye!"

    elif cmd == 'shutdown_pc':
        if plat.startswith('win'):  run(['shutdown','/s','/t','5'])
        elif plat.startswith('darwin'): run(['osascript','-e','tell app "System Events" to shut down'])
        else: run(['systemctl','poweroff'])
        return True, "Shutting down in 5 seconds! 👋 Goodbye!"

    elif cmd == 'sleep_pc':
        if plat.startswith('win'):  run(['rundll32','powrprof.dll,SetSuspendState','0','1','0'])
        elif plat.startswith('darwin'): run(['pmset','sleepnow'])
        else: run(['systemctl','suspend'])
        return True, "Going to sleep! 😴 Zzz…"

    elif cmd == 'lock_screen':
        if plat.startswith('win'):   run(['rundll32','user32.dll,LockWorkStation'])
        elif plat.startswith('darwin'): run(['pmset','displaysleepnow'])
        else:
            for locker in (['xdg-screensaver','lock'],['gnome-screensaver-command','--lock'],
                           ['loginctl','lock-session'],['xlock']):
                if run(locker): break
        return True, "Screen locked! 🔒 Stay safe!"

    elif cmd in ('volume_up','vol_up'):
        n = int(arg) if arg.isdigit() else 10
        if plat.startswith('linux'):
            run(['amixer','-D','pulse','sset','Master',f'{n}%+'])
        elif plat.startswith('darwin'):
            run(['osascript','-e',f'set volume output volume (output volume of (get volume settings) + {n})'])
        return True, f"Volume up +{n}%! 🔊"

    elif cmd in ('volume_down','vol_down'):
        n = int(arg) if arg.isdigit() else 10
        if plat.startswith('linux'):
            run(['amixer','-D','pulse','sset','Master',f'{n}%-'])
        elif plat.startswith('darwin'):
            run(['osascript','-e',f'set volume output volume (output volume of (get volume settings) - {n})'])
        return True, f"Volume down -{n}%! 🔈"

    elif cmd == 'mute':
        if plat.startswith('linux'):
            run(['amixer','-D','pulse','sset','Master','toggle'])
        elif plat.startswith('darwin'):
            run(['osascript','-e','set volume with output muted (not (output muted of (get volume settings)))'])
        return True, "Toggled mute! 🔇"

    elif cmd == 'take_screenshot':
        clippy_ref.take_screenshot()
        return True, "Screenshot taken! 📸"

    elif cmd == 'open_url':
        url = arg if arg.startswith('http') else f'https://{arg}'
        webbrowser.open(url)
        return True, f"Opening {url}! 🌐"

    elif cmd == 'open_file_manager':
        for fm in ['nautilus','thunar','dolphin','nemo','pcmanfm']:
            if shutil.which(fm):
                run([fm]); return True, f"Opening {fm}! 📁"
        run(['xdg-open', str(Path.home())])
        return True, "Opening file manager! 📁"

    elif cmd == 'open_terminal':
        for term in ['gnome-terminal','xfce4-terminal','konsole','xterm','lxterminal']:
            if shutil.which(term):
                run([term]); return True, f"Opening {term}! 💻"
        return False, "Couldn't find a terminal emulator 😅"

    elif cmd == 'empty_trash':
        try:
            trash = Path.home()/'.local'/'share'/'Trash'/'files'
            if trash.exists():
                import shutil as _shutil
                _shutil.rmtree(str(trash)); trash.mkdir(parents=True)
            return True, "Trash emptied! 🗑️ Squeaky clean!"
        except Exception as e:
            return False, f"Couldn't empty trash: {e}"

    elif cmd == 'show_time':
        t = datetime.now().strftime('%H:%M:%S')
        return True, f"It's {t}! ⏰"

    elif cmd == 'show_date':
        d = datetime.now().strftime('%A, %B %d, %Y')
        return True, f"Today is {d}! 📅"

    elif cmd == 'battery':
        try:
            b = psutil.sensors_battery()
            if b:
                plug = '🔌 plugged in' if b.power_plugged else '🔋 on battery'
                return True, f"Battery: {b.percent:.0f}% ({plug}) 🔋"
            return False, "No battery detected (desktop?) 🖥️"
        except:
            return False, "Couldn't read battery info 🤷"

    elif cmd == 'sysinfo':
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        msg = (f"💻 CPU: {cpu}%  |  🧠 RAM: {mem.percent:.0f}%  |  "
               f"💾 Disk: {disk.percent:.0f}%")
        return True, msg

    elif cmd == 'open_text_editor':
        for ed in ['gedit','kate','mousepad','xed','leafpad','nano']:
            if shutil.which(ed):
                run([ed] if ed != 'nano' else ['xterm','-e','nano'])
                return True, f"Opening {ed}! 📝"
        return False, "Couldn't find a text editor 😅"

    elif cmd == 'open_music':
        for pl in ['rhythmbox','clementine','audacious','vlc','amarok']:
            if shutil.which(pl):
                run([pl]); return True, f"Opening {pl}! 🎵"
        return False, "Couldn't find a music player 😅"

    elif cmd == 'open_image_viewer':
        for iv in ['eog','shotwell','gpicview','feh','gimp']:
            if shutil.which(iv):
                run([iv]); return True, f"Opening {iv}! 🖼️"
        return False, "Couldn't find an image viewer 😅"

    elif cmd == 'open_email':
        for em in ['thunderbird','evolution','geary']:
            if shutil.which(em):
                run([em]); return True, f"Opening {em}! 📧"
        webbrowser.open('https://mail.google.com')
        return True, "Opening Gmail! 📧"

    elif cmd == 'web_search':
        webbrowser.open(f'https://www.google.com/search?q={arg}')
        return True, f"Searching for '{arg}'! 🔍"

    elif cmd == 'clear_clipboard':
        try:
            cb = QApplication.clipboard(); cb.clear()
            return True, "Clipboard cleared! 📋"
        except:
            return False, "Couldn't clear clipboard 😅"

    elif cmd == 'weather':
        webbrowser.open('https://wttr.in')
        return True, "Opening weather! 🌡️"

    elif cmd == 'set_emotion':
        if arg in ALL_EMOTIONS:
            clippy_ref.set_expr(arg)
            return True, f"Feeling {arg} now! {EMOTION_ICONS.get(arg,'')}"
        return False, f"Unknown emotion '{arg}'. Try: {', '.join(ALL_EMOTIONS)}"

    elif cmd == 'set_skin':
        if arg in SKINS:
            clippy_ref.quick_skin(arg)
            return True, f"Switched to {arg} skin! 🎨"
        return False, f"Unknown skin '{arg}'. Try: {', '.join(SKINS.keys())}"

    elif cmd == 'set_hat':
        if arg in HATS:
            clippy_ref.s.setValue('hat', arg)
            clippy_ref.imgs = make_images(
                clippy_ref._skin,
                clippy_ref.s.value('pixel',True,bool),
                arg)
            clippy_ref.set_expr(clippy_ref.cur_expr)
            return True, f"Wearing the {arg} now! 🎩"
        return False, f"Unknown hat '{arg}'. Options: {', '.join(HATS)}"

    return False, f"Unknown command: {cmd}"

def parse_command_from_response(text, clippy_ref):
    """Scan AI response for CLIPPY_CMD: directives and execute them"""
    results = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('CLIPPY_CMD:'):
            parts = line[11:].split(':', 1)
            cmd = parts[0].strip()
            arg = parts[1].strip() if len(parts) > 1 else ''
            ok, msg = execute_command(cmd, arg, clippy_ref)
            results.append(msg)
    return results

def parse_user_command(text, clippy_ref):
    """Parse natural-language user commands WITHOUT going through AI.
    Returns (handled, response_msg) so the UI can show it instantly."""
    t = text.lower().strip()

    # ── helpers ──
    def word(w): return w in t.split() or t.startswith(w+' ') or t.endswith(' '+w)

    # open app
    if t.startswith('open ') and 'url' not in t:
        arg = text[5:].strip()
        if arg:
            ok, msg = execute_command('open_app', arg, clippy_ref)
            return True, msg

    # close / kill
    if t.startswith('close ') or t.startswith('kill '):
        arg = text.split(' ',1)[1].strip()
        ok, msg = execute_command('close_app', arg, clippy_ref)
        return True, msg

    # restart
    if any(p in t for p in ('restart','reboot','restart pc','restart computer')):
        ok, msg = execute_command('restart_pc', '', clippy_ref)
        return True, msg

    # shutdown
    if any(p in t for p in ('shutdown','shut down','power off','poweroff')):
        ok, msg = execute_command('shutdown_pc', '', clippy_ref)
        return True, msg

    # sleep
    if any(p in t for p in ('sleep','hibernate','suspend')):
        ok, msg = execute_command('sleep_pc', '', clippy_ref)
        return True, msg

    # lock
    if any(p in t for p in ('lock','lock screen','lock the screen')):
        ok, msg = execute_command('lock_screen', '', clippy_ref)
        return True, msg

    # volume
    if 'volume up' in t or 'turn up' in t or 'louder' in t:
        import re; m = re.search(r'\d+', t)
        ok, msg = execute_command('volume_up', m.group() if m else '10', clippy_ref)
        return True, msg
    if 'volume down' in t or 'turn down' in t or 'quieter' in t or 'lower volume' in t:
        import re; m = re.search(r'\d+', t)
        ok, msg = execute_command('volume_down', m.group() if m else '10', clippy_ref)
        return True, msg
    if 'mute' in t or 'unmute' in t:
        ok, msg = execute_command('mute', '', clippy_ref)
        return True, msg

    # screenshot
    if 'screenshot' in t or 'screen shot' in t or 'capture screen' in t:
        ok, msg = execute_command('take_screenshot', '', clippy_ref)
        return True, msg

    # open url
    if t.startswith('go to ') or t.startswith('open url ') or t.startswith('visit '):
        arg = text.split(' ',2)[-1].strip()
        ok, msg = execute_command('open_url', arg, clippy_ref)
        return True, msg

    # file manager
    if any(p in t for p in ('file manager','files','open files','open folder')):
        ok, msg = execute_command('open_file_manager', '', clippy_ref)
        return True, msg

    # terminal
    if any(p in t for p in ('terminal','console','command line','cmd')):
        ok, msg = execute_command('open_terminal', '', clippy_ref)
        return True, msg

    # empty trash
    if any(p in t for p in ('empty trash','clear trash','delete trash')):
        ok, msg = execute_command('empty_trash', '', clippy_ref)
        return True, msg

    # time
    if any(p in t for p in ('what time','current time','tell me the time')):
        ok, msg = execute_command('show_time', '', clippy_ref)
        return True, msg

    # date
    if any(p in t for p in ('what day','what date','today','current date')):
        ok, msg = execute_command('show_date', '', clippy_ref)
        return True, msg

    # battery
    if 'battery' in t:
        ok, msg = execute_command('battery', '', clippy_ref)
        return True, msg

    # sysinfo
    if any(p in t for p in ('system info','sysinfo','cpu','ram usage','memory','disk space')):
        ok, msg = execute_command('sysinfo', '', clippy_ref)
        return True, msg

    # text editor
    if any(p in t for p in ('text editor','notepad','gedit','kate')):
        ok, msg = execute_command('open_text_editor', '', clippy_ref)
        return True, msg

    # music
    if any(p in t for p in ('music player','music','rhythmbox','audacious')):
        ok, msg = execute_command('open_music', '', clippy_ref)
        return True, msg

    # image viewer
    if any(p in t for p in ('image viewer','photo viewer','pictures')):
        ok, msg = execute_command('open_image_viewer', '', clippy_ref)
        return True, msg

    # email
    if any(p in t for p in ('email','mail client','thunderbird','evolution')):
        ok, msg = execute_command('open_email', '', clippy_ref)
        return True, msg

    # weather
    if 'weather' in t:
        ok, msg = execute_command('weather', '', clippy_ref)
        return True, msg

    # search
    if t.startswith('search ') or t.startswith('google '):
        arg = text.split(' ',1)[1].strip()
        ok, msg = execute_command('web_search', arg, clippy_ref)
        return True, msg

    # clipboard
    if 'clipboard' in t and ('clear' in t or 'empty' in t):
        ok, msg = execute_command('clear_clipboard', '', clippy_ref)
        return True, msg

    # tip
    if t in ('tip','give me a tip','random tip','hint'):
        return True, random.choice(TIPS)

    # greet
    if t in ('greet','greet me','hello clippy','hi clippy','hey clippy'):
        return True, random.choice(GREETINGS)

    # walk
    if t in ('walk','go for a walk','walk around','wander'):
        clippy_ref.walker.start_walk()
        return True, random.choice(WALKING)

    # emotion
    if t.startswith('emotion ') or t.startswith('feel '):
        arg = text.split(' ',1)[1].strip().lower()
        ok, msg = execute_command('set_emotion', arg, clippy_ref)
        return True, msg

    # skin
    if t.startswith('skin '):
        arg = text.split(' ',1)[1].strip()
        # case-insensitive match
        for sk in SKINS:
            if sk.lower() == arg.lower():
                ok, msg = execute_command('set_skin', sk, clippy_ref)
                return True, msg
        return True, f"Unknown skin '{arg}'. Available: {', '.join(SKINS.keys())}"

    # hat
    if t.startswith('hat ') or t.startswith('wear '):
        arg = text.split(' ',1)[1].strip().title()
        ok, msg = execute_command('set_hat', arg, clippy_ref)
        return True, msg

    return False, ''

# ─────────────────────────────────────────────────────────────────────────────
# AI CONFIGS
# ─────────────────────────────────────────────────────────────────────────────
AI_CONFIGS = {
    'Gemini':   {'url':'https://gemini.google.com/app',
                 'inp':'div[contenteditable="true"]',
                 'resp':'model-response,message-content,div[class*="model-response"],div[class*="message-content"]',
                 'wait':3,'max_wait':60},
    'ChatGPT':  {'url':'https://chatgpt.com',
                 'inp':'#prompt-textarea',
                 'resp':'div.markdown,div[class*="prose"],div[class*="markdown"]',
                 'wait':3,'max_wait':60},
    'Claude':   {'url':'https://claude.ai',
                 'inp':'div[contenteditable="true"]',
                 'resp':'div.font-claude-message,div[class*="font-claude"],div[class*="prose"]',
                 'wait':3,'max_wait':60},
    'DeepSeek': {'url':'https://chat.deepseek.com',
                 'inp':'textarea',
                 'resp':'div.ds-markdown,div[class*="markdown"],div[class*="message"]',
                 'wait':3,'max_wait':60},
}

# ─────────────────────────────────────────────────────────────────────────────
# AI WORKERS
# ─────────────────────────────────────────────────────────────────────────────
class BaseAIWorker(QThread):
    status      = pyqtSignal(str)
    response    = pyqtSignal(str)
    error       = pyqtSignal(str)
    clippy_says = pyqtSignal(str)

    def __init__(self, service, covert=False):
        super().__init__()
        self.service=service; self.covert=covert
        self.driver=None; self.queue=Queue(); self.running=True

    def get_config(self): return AI_CONFIGS.get(self.service, AI_CONFIGS['Gemini'])

    def _make_options(self, profile):
        opts=Options()
        if profile: opts.add_argument('-profile'); opts.add_argument(profile)
        opts.set_preference('dom.webdriver.enabled',False)
        opts.set_preference('useAutomationExtension',False)
        if self.covert: opts.add_argument('--headless')
        return opts

    def _launch_driver(self, opts):
        svc=Service(GeckoDriverManager().install())
        self.driver=webdriver.Firefox(service=svc,options=opts)
        self.driver.set_window_size(1024,768)
        if self.covert:
            try: self.driver.minimize_window()
            except: pass

    def setup_browser(self): raise NotImplementedError

    def run(self):
        try:
            self.setup_browser()
            self.send_system_prompt()
            self.chat_loop()
        except Exception as e: self.error.emit(f"❌ {e}")
        finally:
            if self.driver:
                try: self.driver.quit()
                except: pass

    def _find_input(self, cfg):
        for sel in cfg['inp'].split(','):
            try:
                el=WebDriverWait(self.driver,5).until(
                    lambda d,s=sel.strip(): d.find_element(By.CSS_SELECTOR,s))
                if el: return el
            except: pass
        return None

    def send_system_prompt(self):
        self.status.emit("📎 Teaching AI to be Clippy...")
        cfg=self.get_config()
        try:
            el=self._find_input(cfg)
            if el:
                self.driver.execute_script('arguments[0].focus();',el)
                time.sleep(0.3); el.send_keys(CLIPPY_SYSTEM_PROMPT)
                time.sleep(0.5); el.send_keys(Keys.ENTER); time.sleep(5)
        except Exception as e: print(f"System prompt error: {e}")
        self.clippy_says.emit(random.choice(GREETINGS))

    def chat_loop(self):
        cfg=self.get_config()
        while self.running:
            if not self.queue.empty():
                msg=self.queue.get()
                if msg=='__STOP__': break
                is_tip=msg.startswith('__TIP__')
                if is_tip:
                    msg=msg[7:]; self.status.emit("🔍 Checking desktop…")
                else:
                    self.clippy_says.emit(random.choice(THINKING))
                    self.status.emit("💭 Thinking…")
                try:
                    el=self._find_input(cfg)
                    if not el: self.error.emit("❌ Couldn't find input box"); continue
                    self.driver.execute_script('arguments[0].focus();',el)
                    time.sleep(0.3); el.send_keys(msg); time.sleep(0.5); el.send_keys(Keys.ENTER)
                    resp=self._wait_response(cfg)
                    if resp:
                        if not is_tip: self.clippy_says.emit(random.choice(SUCCESS))
                        self.response.emit(resp)
                        QTimer.singleShot(800,lambda:self.status.emit(random.choice(READY)))
                    else:
                        self.error.emit("⚠️ No response received. Try again!")
                except Exception as e: self.error.emit(f"❌ Send failed: {e}")
            time.sleep(0.5)

    def _wait_response(self, cfg):
        sels=cfg['resp'].split(','); waited=last=stable=0; last=''
        time.sleep(cfg['wait'])
        while waited<cfg['max_wait']:
            for sel in sels:
                try:
                    els=self.driver.find_elements(By.CSS_SELECTOR,sel.strip())
                    if els:
                        t=els[-1].text.strip()
                        if len(t)>10:
                            if t==last: stable+=1
                            else: last=t; stable=0
                            if stable>=2: return t
                            break
                except: pass
            if waited>10 and int(waited)%10==0: self.status.emit(random.choice(WAITING))
            time.sleep(2); waited+=2
        return last or None

    def send_msg(self, msg): self.queue.put(msg)
    def send_tip(self, p):   self.queue.put('__TIP__'+p)
    def stop(self):          self.running=False; self.queue.put('__STOP__')


class AutoProfileWorker(BaseAIWorker):
    def setup_browser(self):
        self.status.emit("🔍 Finding Firefox profile...")
        profile=get_firefox_profile()
        if profile: self.status.emit(f"📂 Found: {os.path.basename(profile)}")
        else:       self.status.emit("⚠️ No profile found, using temporary session")
        opts=self._make_options(profile)
        try: self._launch_driver(opts)
        except Exception as e:
            msg=str(e)
            if 'unexpectedly closed' in msg or 'exit code 1' in msg:
                raise RuntimeError("Firefox already running with this profile!\nClose Firefox first, or use 'Use Opened Firefox' mode.")
            raise
        cfg=self.get_config(); self.driver.get(cfg['url'])
        self.status.emit(f"✅ Connected to {self.service}!")
        time.sleep(3)


class OpenedBrowserWorker(BaseAIWorker):
    def setup_browser(self):
        self.status.emit("🦊 Detecting Firefox...")
        if not is_firefox_running():
            raise RuntimeError("Firefox is not running! Please open Firefox first.")
        self.status.emit("✅ Firefox detected! Getting profile...")
        profile=get_active_firefox_profile()
        if not profile:
            raise RuntimeError("Couldn't find Firefox profile.\nTry 'Auto-Find Profile' mode instead.")
        self.status.emit(f"📂 Using profile: {os.path.basename(profile)}")
        opts=self._make_options(profile)
        try: self._launch_driver(opts)
        except Exception as e:
            msg=str(e)
            if 'profile' in msg.lower() or 'lock' in msg.lower():
                raise RuntimeError("Firefox profile is locked.\nTry 'Auto-Find Profile' mode instead!")
            raise
        cfg=self.get_config()
        self.status.emit(f"🌐 Opening {self.service}...")
        self.driver.get(cfg['url']); time.sleep(3)
        self.status.emit("✅ Connected! Ready.")

# ─────────────────────────────────────────────────────────────────────────────
# CLIPPY RENDERER  (pixel-art + CRT + hats)
# ─────────────────────────────────────────────────────────────────────────────
def _rgba(c):
    return (c[0],c[1],c[2], c[3] if len(c)==4 else 255)

def draw_hat(d, s, hat_name, ec):
    """Draw a hat on top of Clippy's head area (around y=20-45 in 180px space)"""
    # hat is drawn in the 180×200 coordinate space (before scale)
    cx=62  # centre x of clippy's "head"
    top=16 # top y for hats

    if hat_name == 'Top Hat':
        # brim
        d.rectangle([s(cx-20),s(top+18),s(cx+24),s(top+24)],fill=(20,20,20,255),outline=(0,0,0,255))
        # body
        d.rectangle([s(cx-12),s(top),s(cx+16),s(top+18)],fill=(20,20,20,255),outline=(0,0,0,255))
        # band
        d.rectangle([s(cx-12),s(top+13),s(cx+16),s(top+17)],fill=(180,0,0,255))

    elif hat_name == 'Party':
        pts = [(s(cx+2),s(top-10)),(s(cx-14),s(top+18)),(s(cx+18),s(top+18))]
        d.polygon(pts, fill=(255,80,180,255), outline=(200,0,140,255))
        # stripes
        d.line([(s(cx+2),s(top-10)),(s(cx-14),s(top+18))],fill=(255,255,0,200),width=s(2))
        d.line([(s(cx+2),s(top-10)),(s(cx+18),s(top+18))],fill=(0,200,255,200),width=s(2))
        d.ellipse([s(cx-2),s(top-15),s(cx+6),s(top-7)],fill=(255,220,0,255))

    elif hat_name == 'Santa':
        # white brim
        d.ellipse([s(cx-18),s(top+14),s(cx+22),s(top+24)],fill=(240,240,240,255))
        # red cone
        pts=[(s(cx+2),s(top-12)),(s(cx-14),s(top+18)),(s(cx+18),s(top+18))]
        d.polygon(pts,fill=(200,20,20,255),outline=(150,0,0,255))
        # pompom
        d.ellipse([s(cx-4),s(top-18),s(cx+8),s(top-8)],fill=(240,240,240,255))

    elif hat_name == 'Cowboy':
        # brim
        d.ellipse([s(cx-22),s(top+14),s(cx+26),s(top+22)],fill=(120,70,20,255))
        # crown
        d.rectangle([s(cx-12),s(top+2),s(cx+16),s(top+16)],fill=(140,85,25,255))
        d.ellipse([s(cx-12),s(top),s(cx+16),s(top+8)],fill=(140,85,25,255))
        # indent top
        d.ellipse([s(cx-8),s(top+2),s(cx+12),s(top+8)],fill=(120,70,20,255))
        # band
        d.rectangle([s(cx-12),s(top+12),s(cx+16),s(top+16)],fill=(80,30,0,255))

    elif hat_name == 'Crown':
        # base
        d.rectangle([s(cx-14),s(top+12),s(cx+18),s(top+22)],fill=(220,180,0,255),outline=(160,120,0,255))
        # points
        for px in [cx-12, cx-3, cx+8]:
            d.polygon([(s(px),s(top+12)),(s(px+4),s(top)),
                       (s(px+8),s(top+12))],fill=(220,180,0,255))
        # gems
        for gx,gc in [(cx-10,(255,50,50)),(cx+1,(50,50,255)),(cx+12,(50,200,50))]:
            d.ellipse([s(gx),s(top+13),s(gx+5),s(top+20)],fill=(*gc,255))

    elif hat_name == 'Cap':
        # dome
        d.ellipse([s(cx-14),s(top+2),s(cx+18),s(top+20)],fill=(20,80,200,255),outline=(10,50,160,255))
        # brim (front)
        d.ellipse([s(cx-2),s(top+14),s(cx+28),s(top+22)],fill=(20,80,200,255))
        d.line([(s(cx),s(top+18)),(s(cx+26),s(top+18))],fill=(10,50,160,255),width=s(2))
        # logo circle
        d.ellipse([s(cx),s(top+6),s(cx+10),s(top+14)],fill=(255,255,255,180))

    elif hat_name == 'Wizard':
        # long pointy hat
        pts=[(s(cx+2),s(top-22)),(s(cx-16),s(top+20)),(s(cx+20),s(top+20))]
        d.polygon(pts,fill=(80,0,160,255),outline=(50,0,120,255))
        # brim
        d.ellipse([s(cx-20),s(top+14),s(cx+24),s(top+24)],fill=(80,0,160,255),outline=(50,0,120,255))
        # stars
        for sx,sy in [(cx-6,top+4),(cx+8,top-4),(cx-2,top-12)]:
            d.ellipse([s(sx),s(sy),s(sx+5),s(sy+5)],fill=(255,220,0,200))
        # band
        d.rectangle([s(cx-16),s(top+14),s(cx+20),s(top+19)],fill=(120,0,220,255))

    elif hat_name == 'Fedora':
        # brim
        d.ellipse([s(cx-22),s(top+14),s(cx+26),s(top+24)],fill=(60,40,20,255))
        # crown
        d.rectangle([s(cx-12),s(top+4),s(cx+16),s(top+16)],fill=(80,55,30,255))
        d.ellipse([s(cx-12),s(top+2),s(cx+16),s(top+10)],fill=(80,55,30,255))
        # crease
        d.ellipse([s(cx-6),s(top+4),s(cx+10),s(top+12)],fill=(70,45,20,255))
        # band
        d.rectangle([s(cx-12),s(top+12),s(cx+16),s(top+17)],fill=(40,20,0,255))
        d.line([(s(cx-12),s(top+14)),(s(cx+16),s(top+14))],fill=(60,40,10,255),width=s(1))

def draw_clippy(expression='idle', skin_name='Classic', pixel_art=True, hat='None'):
    sk=SKINS.get(skin_name,SKINS['Classic'])
    ml,mm,md=_rgba(sk['ml']),_rgba(sk['mm']),_rgba(sk['md'])
    ec,ei,hl=_rgba(sk['ec']),_rgba(sk['ei']),_rgba(sk['hl'])
    sh=_rgba(sk['sh']); ew=(255,255,255,255)
    SC=2; W,H=180*SC,200*SC
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    def s(v): return v*SC

    # body
    d.pieslice([s(30),s(30),s(95),s(95)],   90,270, fill=mm,outline=md,width=s(3))
    d.pieslice([s(36),s(36),s(89),s(89)],   90,270, fill=ml)
    d.arc(     [s(40),s(40),s(70),s(70)],  120,240, fill=hl,width=s(3))
    d.pieslice([s(50),s(85),s(125),s(160)],  0,180, fill=mm,outline=md,width=s(3))
    d.pieslice([s(56),s(91),s(119),s(154)],  0,180, fill=ml)
    d.rectangle([s(60),s(62),s(66),s(118)], fill=mm,outline=md)
    d.rectangle([s(61),s(63),s(65),s(117)], fill=ml)
    d.rectangle([s(88),s(56),s(94),s(92)],  fill=mm,outline=md)
    d.rectangle([s(89),s(57),s(93),s(91)],  fill=ml)

    ey=s(58)
    def one_eye(x,y,expr,wink=False):
        if wink: d.line([x-s(6),y+s(5),x+s(6),y+s(5)],fill=ec,width=s(3)); return
        if expr in ('sleepy','bored'):
            d.ellipse([x-s(7),y,x+s(7),y+s(9)],fill=ew,outline=ec,width=2)
            d.rectangle([x-s(8),y,x+s(8),y+s(4)],fill=ml)
        else:
            d.ellipse([x-s(8),y-s(1),x+s(8),y+s(13)],fill=ew,outline=ec,width=2)
        if expr not in ('sleepy','bored'):
            ox=oy=0
            if expr in ('nervous','surprised'): oy=-s(2)
            if expr=='thinking': ox=s(2);oy=s(3)
            if expr=='confused': ox=-s(1);oy=s(2)
            d.ellipse([x-s(5)+ox,y+s(2)+oy,x+s(5)+ox,y+s(12)+oy],fill=ei)
            d.ellipse([x-s(3)+ox,y+s(4)+oy,x+s(3)+ox,y+s(10)+oy],fill=ec)
            d.ellipse([x+s(1)+ox,y+s(4)+oy,x+s(3)+ox,y+ s(6)+oy],fill=(255,255,255,220))
        if expr in ('happy','excited','love'): d.arc([x-s(9),y-s(12),x+s(9),y-s(2)],180,0,fill=ec,width=s(3))
        elif expr=='angry':    d.line([x-s(8),y-s(3),x+s(8),y+s(3)],fill=ec,width=s(3))
        elif expr=='sad':      d.arc([x-s(8),y-s(4),x+s(8),y+s(4)],0,180,fill=ec,width=s(2))
        elif expr=='thinking': d.line([x-s(7),y-s(2),x+s(7),y-s(2)],fill=ec,width=s(2))
        elif expr=='confused': d.arc([x-s(6),y-s(8),x+s(8),y-s(2)],30,150,fill=ec,width=s(2))
        elif expr=='nervous':  d.line([x-s(6),y-s(5),x+s(6),y-s(1)],fill=ec,width=s(2))
        elif expr=='evil':     d.line([x-s(8),y+s(4),x+s(8),y-s(2)],fill=ec,width=s(3))
        elif expr=='cool':
            d.rectangle([x-s(9),y+s(1),x+s(9),y+s(9)],fill=ec)
            d.rectangle([x-s(7),y+s(3),x+s(7),y+s(7)],fill=(10,10,30,255))
        elif expr=='love': d.polygon([(x,y+s(3)),(x-s(4),y),(x+s(4),y)],fill=(255,50,100,255))
        elif expr=='embarrassed': d.ellipse([x-s(14),y+s(6),x-s(8),y+s(11)],fill=(255,150,150,120))

    lx,rx=s(53),s(71)
    one_eye(lx,ey,expression); one_eye(rx,ey,expression,wink=(expression=='winking'))
    if expression=='cool': d.line([lx+s(8),ey+s(4),rx-s(8),ey+s(4)],fill=ec,width=s(2))

    my,cx2=s(75),s(62)
    if expression in ('happy','excited','love'): d.arc([cx2-s(15),my-s(5),cx2+s(15),my+s(12)],15,165,fill=ec,width=s(3))
    elif expression=='sad': d.arc([cx2-s(12),my,cx2+s(12),my+s(10)],190,350,fill=ec,width=s(2))
    elif expression=='angry': d.line([cx2-s(12),my+s(5),cx2+s(12),my+s(2)],fill=ec,width=s(3))
    elif expression=='surprised': d.ellipse([cx2-s(8),my,cx2+s(8),my+s(12)],fill=ec)
    elif expression=='evil':
        d.arc([cx2-s(14),my-s(3),cx2+s(14),my+s(10)],15,165,fill=ec,width=s(3))
        d.line([cx2-s(10),my+s(5),cx2-s(6),my+s(2)],fill=ec,width=s(2))
        d.line([cx2+s(10),my+s(5),cx2+s(6),my+s(2)],fill=ec,width=s(2))
    elif expression=='nervous': d.line([cx2-s(10),my+s(5),cx2-s(4),my+s(2),cx2+s(2),my+s(7),cx2+s(8),my+s(3)],fill=ec,width=s(2))
    elif expression=='confused':
        d.arc([cx2-s(10),my,cx2+s(10),my+s(8)],200,340,fill=ec,width=s(2))
        d.arc([cx2,my+s(3),cx2+s(14),my+s(10)],15,140,fill=ec,width=s(2))
    elif expression in ('sleepy','bored'): d.line([cx2-s(10),my+s(5),cx2+s(10),my+s(5)],fill=ec,width=s(2))
    elif expression=='embarrassed':
        d.arc([cx2-s(8),my,cx2+s(8),my+s(8)],20,160,fill=ec,width=s(2))
        d.ellipse([cx2-s(22),my-s(8),cx2-s(14),my-s(2)],fill=(255,100,100,80))
        d.ellipse([cx2+s(14),my-s(8),cx2+s(22),my-s(2)],fill=(255,100,100,80))
    elif expression=='winking': d.arc([cx2-s(12),my-s(3),cx2+s(12),my+s(10)],15,165,fill=ec,width=s(2))
    elif expression=='cool': d.line([cx2-s(8),my+s(5),cx2+s(8),my+s(5)],fill=ec,width=s(2))
    else: d.arc([cx2-s(8),my,cx2+s(8),my+s(6)],15,165,fill=ec,width=s(2))

    if expression=='excited':
        for sx,sy in [(s(20),s(20)),(s(145),s(30)),(s(160),s(80))]:
            for p1,p2 in [((sx-s(6),sy),(sx+s(6),sy)),((sx,sy-s(6)),(sx,sy+s(6))),((sx-s(4),sy-s(4)),(sx+s(4),sy+s(4)))]:
                d.line([p1,p2],fill=(255,220,0,200),width=s(2))

    # Hat overlay
    if hat and hat != 'None':
        draw_hat(d, s, hat, ec)

    # shine + shadow
    shine=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shine)
    sd.ellipse([s(34),s(34),s(50),s(50)],fill=(255,255,255,100))
    shine=shine.filter(ImageFilter.GaussianBlur(s(3)))
    img=Image.alpha_composite(img,shine)
    shd=Image.new('RGBA',(W,H),(0,0,0,0)); shdd=ImageDraw.Draw(shd)
    shdd.ellipse([s(45),s(170),s(130),s(195)],fill=(*sh[:3],70))
    shd=shd.filter(ImageFilter.GaussianBlur(s(6)))
    out=Image.new('RGBA',(W,H),(0,0,0,0))
    out=Image.alpha_composite(out,shd); out=Image.alpha_composite(out,img)
    out=out.resize((180,200),Image.LANCZOS)

    if pixel_art:
        w2,h2=out.size
        out=out.resize((w2//2,h2//2),Image.NEAREST).resize((w2,h2),Image.NEAREST)
        ov=Image.new('RGBA',out.size,(0,0,0,0)); ovd=ImageDraw.Draw(ov)
        for y in range(0,out.size[1],3): ovd.line([(0,y),(out.size[0],y)],fill=(0,0,0,35))
        out=Image.alpha_composite(out,ov)

    gc=sk['glow']
    gl=Image.new('RGBA',out.size,(0,0,0,0)); gld=ImageDraw.Draw(gl)
    ow,oh=out.size
    gld.ellipse([ow//2-60,oh//2-70,ow//2+60,oh//2+70],fill=(*gc,15))
    gl=gl.filter(ImageFilter.GaussianBlur(20))
    out=Image.alpha_composite(out,gl)
    return out

def make_images(skin='Classic', pixel_art=True, hat='None'):
    imgs={}
    for expr in ALL_EMOTIONS:
        try:
            pil=draw_clippy(expr,skin,pixel_art,hat)
            buf=BytesIO(); pil.save(buf,'PNG')
            imgs[expr]=QPixmap.fromImage(QImage.fromData(buf.getvalue()))
        except Exception as e:
            print(f'⚠ render {expr}: {e}')
            fb=QPixmap(180,200); fb.fill(Qt.transparent); imgs[expr]=fb
    return imgs

# ─────────────────────────────────────────────────────────────────────────────
# SOUNDS
# ─────────────────────────────────────────────────────────────────────────────
_SND={'start':'/usr/share/sounds/freedesktop/stereo/service-login.oga',
      'msg':  '/usr/share/sounds/freedesktop/stereo/message-new-instant.oga',
      'done': '/usr/share/sounds/freedesktop/stereo/complete.oga',
      'click':'/usr/share/sounds/freedesktop/stereo/button-pressed.oga',
      'error':'/usr/share/sounds/freedesktop/stereo/dialog-error.oga'}
def play_sound(name, enabled=True):
    if not enabled: return
    f=_SND.get(name)
    if f and os.path.exists(f):
        try: subprocess.Popen(['paplay',f],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except: pass

# ─────────────────────────────────────────────────────────────────────────────
# SPEECH BUBBLE  — fully auto-resizing, text always fits
# ─────────────────────────────────────────────────────────────────────────────
class Bubble(QWidget):
    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(Qt.ToolTip|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._timer=QTimer(self); self._timer.setSingleShot(True); self._timer.timeout.connect(self.hide)
        self._build()

    def _build(self):
        fr=QFrame(self); fr.setObjectName('bfr')
        fr.setStyleSheet("""QFrame#bfr{
            background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FFFFE8,stop:0.5 #FFFFD0,stop:1 #FFFFC0);
            border:2px solid #000;border-radius:0;}""")
        lout=QVBoxLayout(fr); lout.setContentsMargins(12,8,12,10); lout.setSpacing(4)

        row=QHBoxLayout()
        ico=QLabel('📎'); ico.setStyleSheet('font-size:16px;background:transparent;')
        tit=QLabel('Clippy'); tit.setStyleSheet(
            'background:transparent;color:#000080;font-family:Tahoma;font-size:12px;font-weight:bold;')
        xb=QPushButton('✕'); xb.setFixedSize(16,16)
        xb.setStyleSheet('QPushButton{background:#CC0000;color:white;border:1px solid #880000;'
                         'font-size:9px;font-weight:bold;padding:0;}'
                         'QPushButton:hover{background:#F00;}')
        xb.clicked.connect(self.hide)
        row.addWidget(ico); row.addWidget(tit,1); row.addWidget(xb)
        lout.addLayout(row)
        div=QFrame(); div.setFrameShape(QFrame.HLine); div.setStyleSheet('background:#000080;max-height:1px;')
        lout.addWidget(div)

        # Use QLabel with word-wrap and constrained width – Qt will compute height
        self.txt=QLabel()
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.txt.setStyleSheet('background:transparent;color:#000;font-family:Tahoma;font-size:11px;')
        self.txt.setMinimumWidth(200)
        self.txt.setMaximumWidth(420)
        # Let height be determined by content
        self.txt.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        lout.addWidget(self.txt)

        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,16); outer.addWidget(fr)
        # extra 16px bottom margin = space for the pointer triangle

    def show_msg(self, text, anchor_pos, ms=9000):
        self.txt.setText(text)
        # Force Qt to compute correct size for the text
        self.txt.setMaximumWidth(420)
        self.txt.adjustSize()
        self.adjustSize()

        scr=QApplication.primaryScreen().geometry()
        # Don't let bubble exceed 60% of screen height
        max_h=int(scr.height()*0.6)
        if self.height()>max_h:
            self.txt.setMaximumWidth(min(600, scr.width()-100))
            self.txt.adjustSize(); self.adjustSize()

        x=anchor_pos.x()-self.width()-24; y=anchor_pos.y()-10
        if x<5: x=anchor_pos.x()+200
        if x+self.width()>scr.width()-10: x=scr.width()-self.width()-10
        if y+self.height()>scr.height()-50: y=scr.height()-self.height()-55
        if y<5: y=5
        self.move(x,y); self.show(); self.raise_()
        self._timer.stop(); self._timer.start(ms)

    def paintEvent(self,ev):
        p=QPainter(self); p.setPen(QPen(QColor(0,0,0),1)); p.setBrush(QBrush(QColor(255,255,192)))
        # pointer triangle on right side
        rx=self.width()-1; ry=min(40,self.height()//3)
        p.drawPolygon(QPoint(rx,ry),QPoint(rx,ry+14),QPoint(rx+12,ry+7))
        p.end()
        super().paintEvent(ev)

# ─────────────────────────────────────────────────────────────────────────────
# WALKER
# ─────────────────────────────────────────────────────────────────────────────
class Walker(QObject):
    walk_start=pyqtSignal(str); walk_done=pyqtSignal(); tip=pyqtSignal(str,str)
    def __init__(self,win):
        super().__init__(); self.win=win; self.walking=False; self._dx=self._dy=0.0; self._steps=0
        self._step_t=QTimer(self); self._step_t.timeout.connect(self._step)
        self._walk_t=QTimer(self); self._walk_t.timeout.connect(self._maybe_walk)
        self._walk_t.start(random.randint(30000,55000))
        self._scan_t=QTimer(self); self._scan_t.timeout.connect(self._scan)
        self._scan_t.start(random.randint(60000,120000))

    def _maybe_walk(self):
        if not self.walking: self.start_walk()
        self._walk_t.setInterval(random.randint(30000,55000))

    def start_walk(self):
        if self.walking: return
        scr=QApplication.primaryScreen().geometry(); m=160
        tx=random.randint(m,scr.width()-m); ty=random.randint(m,scr.height()-m)
        cur=self.win.pos(); dist=math.hypot(tx-cur.x(),ty-cur.y())
        steps=max(20,int(dist/8))
        self._dx=(tx-cur.x())/steps; self._dy=(ty-cur.y())/steps; self._steps=steps
        self.walking=True; self.walk_start.emit(random.choice(WALKING))
        self._step_t.start(28)

    def _step(self):
        if self._steps<=0:
            self._step_t.stop(); self.walking=False; self.walk_done.emit(); return
        cur=self.win.pos()
        self.win.move(int(cur.x()+self._dx),int(cur.y()+self._dy))
        self._steps-=1
        if self._steps%6==0: self.win.set_expr(random.choice(['idle','happy','excited']))

    def _scan(self):
        if not self.walking:
            r=scan_desktop()
            if r: self.tip.emit(*r)
        self._scan_t.setInterval(random.randint(60000,120000))

    def set_walk_enabled(self,v):
        if v: self._walk_t.start(random.randint(30000,55000))
        else: self._walk_t.stop()
    def set_scan_enabled(self,v):
        if v: self._scan_t.start(random.randint(60000,120000))
        else: self._scan_t.stop()

# ─────────────────────────────────────────────────────────────────────────────
# RESIZABLE INPUT
# ─────────────────────────────────────────────────────────────────────────────
class ResizableInput(QTextEdit):
    submitted=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setFixedHeight(62); self.setMinimumHeight(40); self.setMaximumHeight(220)
        self.setPlaceholderText('Ask Clippy anything… or type a command (open firefox, volume up…)')
        self._rs=None; self._rsh=None

    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Return and not(e.modifiers()&Qt.ShiftModifier):
            t=self.toPlainText().strip()
            if t: self.submitted.emit(t); self.clear()
        else: super().keyPressEvent(e)

    def mousePressEvent(self,e):
        if self._zone(e.pos()): self._rs=e.globalPos(); self._rsh=self.height()
        else: self._rs=None; super().mousePressEvent(e)

    def mouseMoveEvent(self,e):
        if self._rs:
            self.setFixedHeight(max(40,min(220,self._rsh+e.globalPos().y()-self._rs.y())))
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.SizeVerCursor if self._zone(e.pos()) else Qt.IBeamCursor)
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self,e): self._rs=None; super().mouseReleaseEvent(e)
    def _zone(self,p): return p.y()>self.height()-14

    def paintEvent(self,e):
        super().paintEvent(e)
        p=QPainter(self.viewport()); p.setPen(QPen(QColor(150,150,150),1))
        w,h=self.viewport().width(),self.viewport().height()
        for i in range(3): o=i*4; p.drawLine(w-10+o,h-2,w-2,h-10+o)
        p.end()

# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS DIALOG
# ─────────────────────────────────────────────────────────────────────────────
class SettingsDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.s=QSettings('ClippyAI','Settings')
        self.setWindowTitle('⚙️ Clippy Settings'); self.setModal(True); self.setMinimumWidth(440)
        self._build()

    def _build(self):
        lay=QVBoxLayout(self)
        tit=QLabel('⚙️ Clippy AI Ultra v4 – Settings')
        tit.setStyleSheet('background:qlineargradient(x1:0,y1:0,x2:1,y2:0,'
                          'stop:0 #0054E3,stop:0.5 #0866FF,stop:1 #0054E3);'
                          'color:#FFF;font-weight:bold;padding:8px;font-size:14px;')
        lay.addWidget(tit)

        def cb(lbl,key,default=True):
            c=QCheckBox(lbl); c.setChecked(self.s.value(key,default,bool)); return c

        self.snd=cb('Enable sounds','sound')
        self.top=cb('Always on top','ontop')
        self.bub=cb('Show speech bubbles','bubble')
        self.pix=cb('Pixel-art / CRT scanlines','pixel')
        self.bnc=cb('Bounce on response','bounce')
        self.wlk=cb('Desktop walking 🚶','walk')
        self.scn=cb('Desktop file scanning 🔍','scan')
        self.cov=cb('🕵️ Covert mode (hidden browser)','covert',False)
        self.aitip=cb('🤖 AI-powered desktop reactions','ai_tips',True)

        def grp(t,ws):
            g=QGroupBox(t); gl=QVBoxLayout(); g.setLayout(gl)
            for w in ws: gl.addWidget(w)
            return g

        lay.addWidget(grp('🔊 Sound',[self.snd]))
        lay.addWidget(grp('🎨 Appearance',[self.top,self.bub,self.pix]))
        lay.addWidget(grp('✨ Behaviour',[self.bnc,self.wlk,self.scn,self.cov,self.aitip]))

        spr=QHBoxLayout(); spr.addWidget(QLabel('Idle animation:'))
        self.spd=QComboBox(); self.spd.addItems(['Slow (12s)','Normal (8s)','Fast (4s)','Very Fast (2s)'])
        self.spd.setCurrentIndex({12000:0,8000:1,4000:2,2000:3}.get(self.s.value('speed',8000,int),1))
        spr.addWidget(self.spd,1); lay.addLayout(spr)

        lay.addStretch()
        br=QHBoxLayout()
        ok=QPushButton('💾 Save'); ok.clicked.connect(self._save)
        ca=QPushButton('❌ Cancel'); ca.clicked.connect(self.reject)
        br.addWidget(ok); br.addWidget(ca); lay.addLayout(br)

    def _save(self):
        s=self.s
        for a,k in [(self.snd,'sound'),(self.top,'ontop'),(self.bub,'bubble'),
                    (self.pix,'pixel'),(self.bnc,'bounce'),(self.wlk,'walk'),
                    (self.scn,'scan'),(self.cov,'covert'),(self.aitip,'ai_tips')]:
            s.setValue(k,a.isChecked())
        s.setValue('speed',{0:12000,1:8000,2:4000,3:2000}[self.spd.currentIndex()])
        self.accept()

# ─────────────────────────────────────────────────────────────────────────────
# PANEL WINDOW CSS
# ─────────────────────────────────────────────────────────────────────────────
_PCSS="""
QWidget#pr{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #F0EDE6,stop:1 #E8E4DC);}
QLabel{color:#000;font-family:Tahoma;font-size:11px;background:transparent;}
QPushButton{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 #FFF,stop:0.45 #F0EDE6,stop:0.55 #E8E4DC,stop:1 #D4D0C8);
    border:2px outset #FFF;border-radius:2px;padding:4px 8px;
    color:#000;font-family:Tahoma;font-size:11px;font-weight:bold;min-height:22px;}
QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #FFF,stop:1 #DCD8D0);}
QPushButton:pressed{background:#D4D0C8;border:2px inset #808080;}
QPushButton:disabled{background:#E8E4DC;color:#999;}
QComboBox{background:#FFF;border:2px inset #D4D0C8;padding:3px;font-family:Tahoma;font-size:11px;}
QComboBox::drop-down{width:18px;}
QTextBrowser,QTextEdit{background:#FFF;border:2px inset #D4D0C8;
    font-family:Tahoma,Courier New;font-size:10px;}
QGroupBox{font-family:Tahoma;font-size:11px;font-weight:bold;
    border:2px groove #D4D0C8;margin-top:8px;padding-top:6px;}
QGroupBox::title{subcontrol-origin:margin;subcontrol-position:top left;padding:0 4px;}
QTabWidget::pane{border:2px solid #D4D0C8;background:#ECE9D8;}
QTabBar::tab{background:#E8E4DC;border:2px outset #FFF;padding:4px 8px;
    margin-right:2px;font-family:Tahoma;font-size:10px;}
QTabBar::tab:selected{background:#FFF;}
QScrollArea{border:none;background:transparent;}
"""

# ─────────────────────────────────────────────────────────────────────────────
# PANEL WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class PanelWindow(QWidget):
    def __init__(self, clippy_ref):
        super().__init__(None)
        self.clippy=clippy_ref; self.s=clippy_ref.s
        self.setWindowTitle('📎 Clippy AI – Control Panel v4')
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint|Qt.WindowCloseButtonHint)
        self.setMinimumWidth(460); self.setMaximumWidth(560)
        root=QWidget(); root.setObjectName('pr'); root.setStyleSheet(_PCSS)
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(root)
        self._build(root)

    def closeEvent(self,e): self.hide(); e.ignore()

    def _build(self, root):
        lay=QVBoxLayout(root); lay.setContentsMargins(8,8,8,8); lay.setSpacing(5)
        tit=QLabel('📎 Clippy AI – Ultra Edition v4')
        tit.setStyleSheet('background:qlineargradient(x1:0,y1:0,x2:1,y2:0,'
                          'stop:0 #0054E3,stop:0.5 #0866FF,stop:1 #0054E3);'
                          'color:#FFF;font-weight:bold;padding:8px;font-size:12px;font-family:Tahoma;')
        lay.addWidget(tit)

        tabs=QTabWidget()

        # ── Chat tab ──────────────────────────────────────────────────────
        ct=QWidget(); cl=QVBoxLayout(ct); cl.setSpacing(4)
        sr=QHBoxLayout(); sr.addWidget(QLabel('AI:'))
        self.ai_cb=QComboBox(); self.ai_cb.addItems(['Gemini','ChatGPT','Claude','DeepSeek'])
        sr.addWidget(self.ai_cb,1)
        cov_lbl=QLabel(); self._cov_lbl=cov_lbl; self._update_cov()
        sr.addWidget(cov_lbl)
        ctog=QPushButton('🕵️'); ctog.setFixedWidth(32); ctog.setToolTip('Toggle Covert Mode')
        ctog.clicked.connect(self._toggle_cov); sr.addWidget(ctog)
        cl.addLayout(sr)
        cl.addWidget(QLabel('📡 Connection:'))
        self.btn_auto=QPushButton('🔍 Auto-Find Profile (New Firefox)')
        self.btn_auto.clicked.connect(self.clippy.start_auto); cl.addWidget(self.btn_auto)
        self.btn_open=QPushButton('🦊 Use Opened Firefox')
        self.btn_open.clicked.connect(self.clippy.start_opened); cl.addWidget(self.btn_open)
        self.btn_stop=QPushButton('⏹️ Stop'); self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.clippy.stop_worker); cl.addWidget(self.btn_stop)
        cl.addWidget(QLabel('💬 Conversation:'))
        self.chat=QTextBrowser(); self.chat.setMinimumHeight(140); self.chat.setMaximumHeight(240)
        cl.addWidget(self.chat)
        cl.addWidget(QLabel('✏️ Message (Enter=send, drag bottom to resize):'))
        self.inp=ResizableInput(); self.inp.submitted.connect(self.clippy.handle_input)
        cl.addWidget(self.inp)
        sb=QPushButton('📤 Send'); sb.clicked.connect(lambda:self.clippy.handle_input(self.inp.toPlainText().strip()))
        cl.addWidget(sb)
        tabs.addTab(ct,'💬 Chat')

        # ── Appearance tab  (skins + hats + emotions) ─────────────────────
        at2=QWidget(); al2=QVBoxLayout(at2); al2.setSpacing(6)

        # Skin picker
        sg=QGroupBox('🎨 Skin'); sl=QVBoxLayout(); sg.setLayout(sl)
        skin_grid=QGridLayout(); skin_grid.setSpacing(4)
        self._skin_btns={}
        for i,sk in enumerate(SKINS.keys()):
            col=QColor(SKINS[sk]['preview'])
            btn=QPushButton(sk); btn.setMinimumHeight(28)
            btn.setStyleSheet(
                f'QPushButton{{background:{SKINS[sk]["preview"]};'
                f'color:{"#FFF" if col.lightness()<128 else "#000"};'
                f'border:2px outset #FFF;border-radius:2px;font-family:Tahoma;font-size:10px;}}'
                f'QPushButton:hover{{border:2px solid #0066FF;}}'
                f'QPushButton:pressed{{border:2px inset #000;}}'
            )
            btn.clicked.connect(lambda _,s=sk: self.clippy.quick_skin(s))
            self._skin_btns[sk]=btn
            skin_grid.addWidget(btn, i//3, i%3)
        sl.addLayout(skin_grid); al2.addWidget(sg)

        # Hat picker
        hg=QGroupBox('🎩 Hat'); hl2=QHBoxLayout(); hg.setLayout(hl2)
        self.hat_cb=QComboBox(); self.hat_cb.addItems(HATS)
        cur_hat=self.s.value('hat','None')
        idx=self.hat_cb.findText(cur_hat)
        if idx>=0: self.hat_cb.setCurrentIndex(idx)
        self.hat_cb.currentTextChanged.connect(
            lambda h: (self.clippy.s.setValue('hat',h),
                       self.clippy._reload_images()))
        hl2.addWidget(QLabel('Choose:')); hl2.addWidget(self.hat_cb,1)
        al2.addWidget(hg)

        # Emotions grid
        eg=QGroupBox('😊 Emotions'); el3=QGridLayout(); eg.setLayout(el3)
        for i,(expr,icon) in enumerate(EMOTION_ICONS.items()):
            b=QPushButton(f'{icon} {expr.capitalize()}'); b.setMinimumHeight(26)
            b.clicked.connect(lambda _,e=expr:(
                self.clippy.set_expr(e),
                QTimer.singleShot(3000,lambda:self.clippy.set_expr('idle'))))
            el3.addWidget(b,i//2,i%2)
        al2.addWidget(eg)
        al2.addStretch()
        tabs.addTab(at2,'🎨 Appearance')

        # ── Commands tab ───────────────────────────────────────────────────
        cdt=QWidget(); cdl=QVBoxLayout(cdt); cdl.setSpacing(4)
        cdl.addWidget(QLabel('<b>Type these in the chat, or say them naturally!</b>'))

        # Quick command buttons
        qg=QGroupBox('⚡ Quick Commands'); qgl=QGridLayout(); qg.setLayout(qgl)
        quick_cmds=[
            ('📸 Screenshot','screenshot'),('⏰ Time','what time'),
            ('📅 Date','what date'),('🔊 Vol+','volume up'),
            ('🔈 Vol-','volume down'),('🔇 Mute','mute'),
            ('🔒 Lock','lock'),('💻 Terminal','terminal'),
            ('📁 Files','file manager'),('🔋 Battery','battery'),
            ('📊 Sys Info','sysinfo'),('🗑️ Empty Trash','empty trash'),
            ('🚶 Walk','walk'),('💡 Tip','tip'),
            ('🌐 Weather','weather'),('🔄 Restart','restart'),
        ]
        for i,(lbl,cmd) in enumerate(quick_cmds):
            b=QPushButton(lbl); b.setMinimumHeight(26)
            b.clicked.connect(lambda _,c=cmd: self.clippy.handle_input(c))
            qgl.addWidget(b,i//4,i%4)
        cdl.addWidget(qg)

        # All commands reference list
        ref_lbl=QLabel('<b>📖 All Commands Reference:</b>'); cdl.addWidget(ref_lbl)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setMaximumHeight(280)
        ref_w=QWidget(); ref_lay=QVBoxLayout(ref_w); ref_lay.setSpacing(2)
        for cmd,desc in COMMANDS_HELP:
            row_w=QWidget(); row_l=QHBoxLayout(row_w); row_l.setContentsMargins(2,1,2,1)
            cmd_lbl=QLabel(f'<code>{cmd}</code>'); cmd_lbl.setFixedWidth(200)
            cmd_lbl.setStyleSheet('font-size:10px;color:#000060;')
            desc_lbl=QLabel(desc); desc_lbl.setStyleSheet('font-size:10px;color:#333;')
            desc_lbl.setWordWrap(True)
            row_l.addWidget(cmd_lbl); row_l.addWidget(desc_lbl,1)
            ref_lay.addWidget(row_w)
        ref_lay.addStretch(); scroll.setWidget(ref_w); cdl.addWidget(scroll)

        # Open app launcher
        oag=QGroupBox('🚀 Open App'); oal=QHBoxLayout(); oag.setLayout(oal)
        self.app_inp=QLineEdit(); self.app_inp.setPlaceholderText('app name (e.g. firefox, vlc…)')
        self.app_inp.returnPressed.connect(lambda:self.clippy.handle_input(f'open {self.app_inp.text()}'))
        open_btn=QPushButton('Open'); open_btn.setFixedWidth(60)
        open_btn.clicked.connect(lambda:self.clippy.handle_input(f'open {self.app_inp.text()}'))
        oal.addWidget(self.app_inp,1); oal.addWidget(open_btn)
        cdl.addWidget(oag)
        tabs.addTab(cdt,'⚡ Commands')

        # ── Actions tab ────────────────────────────────────────────────────
        act=QWidget(); alay=QVBoxLayout(act); alay.setSpacing(4)
        def grp_btns(title,items):
            g=QGroupBox(title); gl=QGridLayout(); g.setLayout(gl); gl.setSpacing(3)
            for i,(lbl,fn) in enumerate(items):
                b=QPushButton(lbl); b.clicked.connect(fn); b.setMinimumHeight(26)
                gl.addWidget(b,i//2,i%2)
            return g
        alay.addWidget(grp_btns('🚶 Clippy',[
            ('Walk Now',      lambda:self.clippy.walker.start_walk()),
            ('💡 Random Tip', lambda:self.clippy.show_bubble(random.choice(TIPS))),
            ('⬆️ Bounce',     self.clippy.bounce),
            ('👋 Greet',      self.clippy.greet),
        ]))
        alay.addWidget(grp_btns('💻 System',[
            ('📸 Screenshot',  self.clippy.take_screenshot),
            ('📊 Sys Info',    self.clippy.show_sysinfo),
            ('📁 Files',       lambda:self.clippy.handle_input('file manager')),
            ('💻 Terminal',    lambda:self.clippy.handle_input('terminal')),
            ('🗑️ Empty Trash', lambda:self.clippy.handle_input('empty trash')),
            ('🔋 Battery',     lambda:self.clippy.handle_input('battery')),
        ]))
        alay.addWidget(grp_btns('🌐 Web',[
            ('🔍 Search',  self.clippy.web_search),
            ('📺 YouTube', lambda:webbrowser.open('https://youtube.com')),
            ('🐙 GitHub',  lambda:webbrowser.open('https://github.com')),
            ('🌡️ Weather', lambda:self.clippy.handle_input('weather')),
        ]))
        alay.addStretch()
        tabs.addTab(act,'🛠️ Actions')

        lay.addWidget(tabs)
        self.status_lbl=QLabel('💤 Idle – choose a mode to start')
        self.status_lbl.setStyleSheet(
            'background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #D4D0C8,stop:1 #C0BDB0);'
            'border:2px inset #FFF;padding:4px 6px;font-size:10px;font-family:Tahoma;')
        lay.addWidget(self.status_lbl)
        btm=QHBoxLayout()
        sb2=QPushButton('⚙️ Settings'); sb2.clicked.connect(self.clippy.show_settings)
        sd=QPushButton('🔍 Scan Desktop'); sd.clicked.connect(self.clippy.manual_scan)
        btm.addWidget(sb2); btm.addWidget(sd); lay.addLayout(btm)

    def _toggle_cov(self):
        self.s.setValue('covert',not self.s.value('covert',False,bool)); self._update_cov()
    def _update_cov(self):
        on=self.s.value('covert',False,bool)
        self._cov_lbl.setText('🕵️ON' if on else '👁️OFF')
        self._cov_lbl.setStyleSheet(f'color:{"#006600" if on else "#666"};font-size:10px;')

    def log(self,html): self.chat.append(html); self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())
    def set_status(self,t): self.status_lbl.setText(t)
    def set_connected(self,v):
        self.btn_auto.setEnabled(not v); self.btn_open.setEnabled(not v); self.btn_stop.setEnabled(v)
    def get_service(self): return self.ai_cb.currentText()

# ─────────────────────────────────────────────────────────────────────────────
# CLIPPY CHARACTER WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class ClippyXP(QWidget):
    def __init__(self):
        super().__init__(None)
        self.s=QSettings('ClippyAI','Settings')
        self.worker=None; self.cur_expr='idle'; self.drag_pos=None
        self._skin=self.s.value('skin','Classic')

        print(f'🎨 Skin: {self._skin} | Hat: {self.s.value("hat","None")} | Pixel: {self.s.value("pixel",True,bool)}')
        self.imgs=make_images(self._skin, self.s.value('pixel',True,bool), self.s.value('hat','None'))

        # Bubble & walker first
        self.bubble=Bubble()
        self.walker=Walker(self)
        self.walker.walk_start.connect(self._on_walk_start)
        self.walker.walk_done.connect(self._on_walk_done)
        self.walker.tip.connect(self._on_desktop_tip)
        self.walker.set_walk_enabled(self.s.value('walk',True,bool))
        self.walker.set_scan_enabled(self.s.value('scan',True,bool))

        self._build_char()
        self.panel=PanelWindow(self)
        self._build_tray()

        self.idle_t=QTimer(self); self.idle_t.timeout.connect(self._idle_anim)
        self.idle_t.start(self.s.value('speed',8000,int))
        self._apply_flags()
        play_sound('start',self.s.value('sound',True,bool))
        QTimer.singleShot(2200, self.greet)

    def _reload_images(self):
        self.imgs=make_images(self._skin,self.s.value('pixel',True,bool),self.s.value('hat','None'))
        self.set_expr(self.cur_expr)

    # ── Character window ──────────────────────────────────────────────────
    def _build_char(self):
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        lay=QVBoxLayout(self); lay.setContentsMargins(6,6,6,6); lay.setSpacing(0)
        self.lbl=QLabel(); self.lbl.setMinimumSize(180,200)
        self.set_expr('idle')
        self.lbl.setCursor(Qt.PointingHandCursor)
        self.lbl.mousePressEvent       = self._drag_start
        self.lbl.mouseMoveEvent        = self._drag_move
        self.lbl.mouseDoubleClickEvent = self._toggle_panel
        sh=QGraphicsDropShadowEffect()
        sh.setBlurRadius(18); sh.setColor(QColor(0,0,0,100)); sh.setOffset(4,4)
        self.lbl.setGraphicsEffect(sh)
        lay.addWidget(self.lbl, alignment=Qt.AlignCenter)
        self.resize(192,212)
        scr=QApplication.primaryScreen().geometry()
        self.move(scr.width()-240, scr.height()-300)

    def _apply_flags(self):
        flags=Qt.FramelessWindowHint|Qt.Tool
        if self.s.value('ontop',True,bool): flags|=Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags); self.show()
        self.idle_t.setInterval(self.s.value('speed',8000,int))

    def set_expr(self,expr):
        if expr in self.imgs:
            self.cur_expr=expr; p=self.imgs[expr]
            if not p.isNull(): self.lbl.setPixmap(p); self.lbl.setScaledContents(False)

    def _idle_anim(self):
        if (not self.worker or not self.worker.isRunning()) and not self.walker.walking:
            pool=['idle','idle','idle','happy','thinking','bored','winking','sleepy']
            self.set_expr(random.choice(pool))
            QTimer.singleShot(1200,lambda:self.set_expr('idle'))

    def _drag_start(self,e):
        if e.button()==Qt.LeftButton: self.drag_pos=e.globalPos()-self.frameGeometry().topLeft()
    def _drag_move(self,e):
        if e.buttons()==Qt.LeftButton and self.drag_pos and not self.walker.walking:
            self.move(e.globalPos()-self.drag_pos)
    def _toggle_panel(self,e):
        if self.panel.isVisible(): self.panel.hide()
        else:
            p=self.pos(); scr=QApplication.primaryScreen().geometry()
            px=max(5, p.x()-470 if p.x()>470 else p.x()+200)
            py=max(40, min(p.y(), scr.height()-720))
            self.panel.move(px,py); self.panel.show(); self.panel.raise_()
        play_sound('click',self.s.value('sound',True,bool))

    def show_bubble(self,text,ms=9000):
        if self.s.value('bubble',True,bool):
            self.bubble.show_msg(text,self.pos(),ms)

    # ── Walker ────────────────────────────────────────────────────────────
    def _on_walk_start(self,msg):
        self.set_expr(random.choice(['excited','happy','winking']))
        self.show_bubble(msg,4000)
    def _on_walk_done(self): self.set_expr('idle')
    def _on_desktop_tip(self,cat,name):
        if self.worker and self.worker.isRunning() and self.s.value('ai_tips',True,bool):
            cat_desc={'folder':'folder','game':'game/application','image':'image file',
                      'video':'video file','document':'document','code':'source code file',
                      'music':'music file','file':'file'}
            prompt=(f"You're Clippy and just walked past the desktop and noticed a "
                    f"{cat_desc.get(cat,'file')} called '{name}'. React in 1-2 short sentences "
                    f"in Clippy's style. Be curious, helpful, slightly funny.")
            self.worker.send_tip(prompt)
            self.set_expr('surprised')
        else:
            static={'game':f"Oh! I see {name}! It looks like you're trying to game! 🎮",
                    'folder':f"'{name}' – nice folder! Very organised! 📁",
                    'image':f"'{name}' – a photo! Great taste! 📸",
                    'video':f"'{name}' – movie night? Clippy approves! 🎬",
                    'document':f"I noticed '{name}'! Working on a document? 📄",
                    'code':f"'{name}' – a developer! Clippy is impressed! 💻",
                    'music':f"'{name}' – great music taste! 🎵",
                    'file':f"I spotted '{name}' while strolling by! Interesting! 📎"}
            self.show_bubble(static.get(cat,f"'{name}' on your desktop! 📎"),12000)
            self.set_expr('surprised')
            QTimer.singleShot(3000,lambda:self.set_expr('idle'))

    # ── INPUT HANDLER (routes commands vs AI) ─────────────────────────────
    def handle_input(self, msg):
        if not msg: return
        # 1. Try local command parse first (instant, no AI needed)
        handled, resp = parse_user_command(msg, self)
        if handled:
            self.panel.log(f"<p style='color:#006;font-weight:bold;'>👤 You: {msg}</p>"
                           f"<p style='color:#040;margin-left:20px;'>⚡ {resp}</p>")
            self.show_bubble(resp)
            self.set_expr('happy')
            if self.s.value('bounce',True,bool): self.bounce()
            QTimer.singleShot(2500,lambda:self.set_expr('idle'))
            play_sound('done',self.s.value('sound',True,bool))
            return
        # 2. Send to AI
        if not self.worker or not self.worker.isRunning():
            QMessageBox.warning(self,'Not Connected',
                'Start a connection first!\n\nFor commands (open app, volume, etc.) '
                'you don\'t need a connection – just type naturally!')
            return
        self.panel.log(f"<p style='color:#060;font-weight:bold;'>👤 You:</p>"
                       f"<p style='color:#040;margin-left:20px;'>{msg}</p>")
        self.panel.inp.clear()
        self.worker.send_msg(msg); self.set_expr('thinking')
        play_sound('msg',self.s.value('sound',True,bool))

    # ── AI WORKERS ────────────────────────────────────────────────────────
    def start_auto(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self,'Running','Stop the current session first!'); return
        svc=self.panel.get_service(); cov=self.s.value('covert',False,bool)
        self.panel.log(f"<p style='color:#06C;font-weight:bold;'>🔍 Starting Auto-Profile ({svc})"
                       f"{'  🕵️ COVERT' if cov else ''}…</p>")
        self.worker=AutoProfileWorker(svc,cov); self._wire()
        self.worker.start(); self.panel.set_connected(True)
        play_sound('start',self.s.value('sound',True,bool))

    def start_opened(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self,'Running','Stop the current session first!'); return
        svc=self.panel.get_service(); cov=self.s.value('covert',False,bool)
        self.panel.log(f"<p style='color:#06C;font-weight:bold;'>🦊 Connecting to Firefox ({svc})"
                       f"{'  🕵️ COVERT' if cov else ''}…</p>")
        self.worker=OpenedBrowserWorker(svc,cov); self._wire()
        self.worker.start(); self.panel.set_connected(True)
        play_sound('start',self.s.value('sound',True,bool))

    def _wire(self):
        self.worker.status.connect(self._on_status)
        self.worker.response.connect(self._on_response)
        self.worker.error.connect(self._on_error)
        self.worker.clippy_says.connect(self._on_clippy_says)

    def stop_worker(self):
        if self.worker: self.worker.stop(); self.worker=None
        self.panel.log("<p style='color:#C00;font-style:italic;'>⏹️ Stopped.</p>")
        self.panel.set_status('💤 Idle'); self.panel.set_connected(False)

    def _on_status(self,t):
        self.panel.set_status(t)
        self.panel.log(f"<p style='color:#666;font-style:italic;font-size:10px;'>{t}</p>")

    def _on_clippy_says(self,msg):
        self.panel.log(f"<p style='color:#90C;font-weight:bold;'>📎 Clippy: {msg}</p>")
        self.show_bubble(msg); play_sound('click',self.s.value('sound',True,bool))

    def _on_response(self,resp):
        # Check for embedded commands in AI response
        cmd_results=parse_command_from_response(resp,self)
        # Remove command lines from displayed text
        clean='\n'.join(l for l in resp.split('\n') if not l.strip().startswith('CLIPPY_CMD:'))
        self.panel.log(f"<p style='color:#008;font-weight:bold;'>📎 Clippy:</p>"
                       f"<p style='color:#006;margin-left:20px;'>{clean}</p>"
                       "<hr style='border:1px solid #CCC;'>")
        if cmd_results:
            for r in cmd_results:
                self.panel.log(f"<p style='color:#060;font-size:10px;'>⚡ {r}</p>")
        self.show_bubble(clean if clean else resp)
        self.set_expr('happy')
        if self.s.value('bounce',True,bool): self.bounce()
        play_sound('done',self.s.value('sound',True,bool))
        QTimer.singleShot(2500,lambda:self.set_expr('idle'))

    def _on_error(self,err):
        self.panel.log(f"<p style='color:#C00;font-weight:bold;'>❌ Error:</p>"
                       f"<p style='color:#900;margin-left:20px;'>{err}</p>")
        self.set_expr('sad'); play_sound('error',self.s.value('sound',True,bool))
        if any(k in err.lower() for k in ('not running',"couldn't",'locked','profile')):
            QMessageBox.critical(self,'Connection Error',err); self.panel.set_connected(False)
        QTimer.singleShot(3000,lambda:self.set_expr('idle'))

    # ── APPEARANCE ────────────────────────────────────────────────────────
    def quick_skin(self,skin):
        self.s.setValue('skin',skin); self._skin=skin; self._reload_images()
        self.show_bubble(f'🎨 Switched to {skin} skin!',3000)

    # ── ACTIONS ───────────────────────────────────────────────────────────
    def greet(self):
        self.set_expr('happy'); self.show_bubble(random.choice(GREETINGS))
        QTimer.singleShot(2000,lambda:self.set_expr('idle'))

    def manual_scan(self):
        r=scan_desktop()
        if r: self._on_desktop_tip(*r)
        else: self.show_bubble(random.choice(TIPS))

    def take_screenshot(self):
        try:
            fp=str(Path.home()/f'clippy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            ImageGrab.grab().save(fp)
            self.panel.log(f"<p style='color:#090;'>📸 Saved: {fp}</p>")
            self.show_bubble(f'📸 Screenshot saved!\n{fp}')
            play_sound('done',self.s.value('sound',True,bool))
        except Exception as e:
            self.panel.log(f"<p style='color:#C00;'>❌ Screenshot failed: {e}</p>")

    def show_sysinfo(self):
        ok,msg=execute_command('sysinfo','',self)
        self.show_bubble(msg); self.panel.log(f"<p>💻 {msg}</p>")
        self.set_expr('thinking'); QTimer.singleShot(2000,lambda:self.set_expr('idle'))

    def web_search(self):
        t,ok=QInputDialog.getText(self,'Web Search','Search for:')
        if ok and t: webbrowser.open(f'https://www.google.com/search?q={t}')

    def bounce(self):
        orig=self.pos()
        ag=QSequentialAnimationGroup(self)
        up=QPropertyAnimation(self,b'pos'); up.setDuration(150)
        up.setStartValue(orig); up.setEndValue(QPoint(orig.x(),orig.y()-28))
        up.setEasingCurve(QEasingCurve.OutQuad)
        dn=QPropertyAnimation(self,b'pos'); dn.setDuration(220)
        dn.setStartValue(QPoint(orig.x(),orig.y()-28)); dn.setEndValue(orig)
        dn.setEasingCurve(QEasingCurve.InBounce)
        ag.addAnimation(up); ag.addAnimation(dn)
        ag.start(QSequentialAnimationGroup.DeleteWhenStopped)

    def show_settings(self):
        dlg=SettingsDlg(self)
        if dlg.exec_()==QDialog.Accepted:
            new_skin=self.s.value('skin','Classic')
            if new_skin!=self._skin: self._skin=new_skin
            self._reload_images()
            self._apply_flags()
            self.walker.set_walk_enabled(self.s.value('walk',True,bool))
            self.walker.set_scan_enabled(self.s.value('scan',True,bool))
            self.idle_t.setInterval(self.s.value('speed',8000,int))
            self.panel._update_cov()
            QMessageBox.information(self,'Saved','Settings applied! ✅')

    # ── TRAY ──────────────────────────────────────────────────────────────
    def _build_tray(self):
        self.tray=QSystemTrayIcon(self); self.tray.setIcon(QIcon(self.imgs['idle']))
        m=QMenu()
        def add(lbl,fn): a=QAction(lbl,self); a.triggered.connect(fn); m.addAction(a)
        add('Show/Hide Panel',  lambda:self._toggle_panel(None))
        add('🚶 Walk Now',      lambda:self.walker.start_walk())
        add('💡 Random Tip',   lambda:self.show_bubble(random.choice(TIPS)))
        add('📸 Screenshot',   self.take_screenshot)
        add('👋 Greet',        self.greet)
        m.addSeparator()
        add('⚙️ Settings',     self.show_settings)
        m.addSeparator()
        add('Exit Clippy',     QApplication.quit)
        self.tray.setContextMenu(m)
        self.tray.setToolTip('Clippy AI Ultra v4 📎')
        self.tray.activated.connect(lambda r: self._toggle_panel(None) if r==QSystemTrayIcon.DoubleClick else None)
        self.tray.show()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__=='__main__':
    print('🚀 Clippy AI Ultra Edition v4.0')
    print('🎨 12 skins | 🎩 8 hats | 😊 16 emotions | ⚡ 30+ commands')
    app=QApplication(sys.argv)
    app.setFont(QFont('Tahoma',9))
    app.setQuitOnLastWindowClosed(False)
    print('📎 Rendering Clippy…')
    clippy=ClippyXP()
    clippy.show(); clippy.raise_(); clippy.activateWindow()
    print('✅ Ready! Double-click Clippy to open the control panel.')
    print('⚡ Commands work WITHOUT connecting to AI – just type naturally!')
    sys.exit(app.exec_())
