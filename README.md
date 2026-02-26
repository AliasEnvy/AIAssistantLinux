# AIAssistantLinux
A Linux based AI assistant in windows XP style.

AI Assistant Version 1.0

A modern AI assistant styled after the classic Windows XP Office companion.

Overview

Clippy AI Ultimate recreates the Windows XP assistant and connects it to modern AI services such as Claude, ChatGPT, and DeepSeek. It combines a retro interface with current AI capabilities.

Key Features

- Windows XP Luna-style interface
- Integration with Firefox through remote debugging
- Support for multiple AI backends (Claude, ChatGPT, DeepSeek)
- Six selectable assistants with distinct personalities
- Persistent chat history with export options
- Classic system sound effects
- Smooth animations with a retro design
- System tray support
- Draggable window interface
- Customizable settings
- Tabbed layout (Chat / Settings / About)

Assistants

Clippy – General help  
Rover – Search and research  
Merlin – Complex questions  
Dot – Quick responses  
Links – Creative tasks  
Peedy – Conversational interaction  

Requirements

- Python 3.8+
- Firefox with geckodriver
- Linux (tested on Fedora, works on Ubuntu/Debian)
- X11 display server

Dependencies

- PyQt5
- Pillow
- selenium
- psutil
- requests

Installation

1. Clone the repository
2. Make the main script executable
3. Run the script with Python 3

Dependencies install automatically on first launch. If that fails, install them manually using pip.

Firefox Setup

Firefox must run with remote debugging enabled. This can be done automatically from the Settings tab or manually by starting Firefox with the remote debugging port enabled.

Usage

First-time setup:
- Launch the application
- Open the chat panel
- Use Settings to start Firefox with debugging
- Start the AI connection
- Ensure you are logged into the selected AI service
- Begin chatting

On future launches:
- Start the script
- Open the assistant
- Start the AI connection
- Chat

Configuration

Settings are stored locally in a JSON configuration file in the user directory.
Chat history is stored locally and can be exported as TXT or JSON.

Customization

- Switch assistants from the dropdown menu
- Change AI backend in Settings
- Enable or disable sounds in Settings

Troubleshooting

Firefox connection issues:
- Close all Firefox windows
- Restart Firefox with remote debugging enabled
- Use the Detect Firefox option in Settings

No AI response:
- Confirm internet connection
- Ensure you are logged into the AI service
- Restart the AI connection

Missing dependencies:
- Upgrade pip
- Reinstall required packages manually

Geckodriver not found:
- Install it via your distribution package manager
- Or download and place it in a system path

FAQ

Platform support:
Currently Linux only.

API key requirement:
No API key required. The application uses the web interfaces of supported AI services.

Privacy:
No data is sent to third parties by the application itself.
Chat history is stored locally.
All AI communication occurs directly between the user and the selected AI service.

Offline use:
Internet connection is required.

License

MIT License

Credits

Original Office Assistant concept – Microsoft  
AI services – Anthropic (Claude), OpenAI (ChatGPT), DeepSeek  
UI Framework – PyQt5  
Automation – Selenium WebDriver
