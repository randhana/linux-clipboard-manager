# Linux Clipboard Manager

A lightweight, local-only clipboard manager for Linux built with Python and PyQt6.

## Features
- Background daemon to monitor clipboard history.
- Popup GUI to browse and search previous items.
- Auto-paste integration with `xdotool` (X11) or `wtype` (Wayland).

## Prerequisites
- **Python 3**
- **xdotool** (for X11 users) or **wtype** (for Wayland users)

You can install `wtype` or `xdotool` on Ubuntu using:
```bash
sudo apt install xdotool wtype
```

## Installation
You can install the Clipboard Manager easily via `pip`:
```bash
pip install linux-copycache
```

### System Dependencies
The auto-pasting functionality requires `xdotool` and `xclip` to be installed on your system.
```bash
sudo apt install xdotool xclip
```

## Running the tool
Once installed, you can start the application from anywhere in your terminal:
```bash
linux-clipboard
```
The application will launch, dock itself to your system tray, and quietly monitor your copied text!

## Setting up the `Super+V` (Win+V) Shortcut in Ubuntu
For the native Windows experience, set up a custom shortcut:
1. Open **Settings** -> **Keyboard**.
2. Scroll to the bottom and click **View and Customize Shortcuts**.
3. Select **Custom Shortcuts** and click the **+** or **Add Shortcut** button.
4. **Name:** `Clipboard Manager`
5. **Command:** `linux-clipboard`
6. **Shortcut:** Press `Super + V` (Windows key + V).
7. Click **Add**.

Now, whenever you press `Super + V`, the history window will pop up!
