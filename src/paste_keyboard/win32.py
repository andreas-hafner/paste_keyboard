from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import threading
import time
import uuid


if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
    LONG_PTR = ctypes.c_longlong
else:
    ULONG_PTR = ctypes.c_ulong
    LONG_PTR = ctypes.c_long


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)

INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

MAPVK_VK_TO_VSC = 0

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

PM_REMOVE = 0x0001
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
WM_DESTROY = 0x0002
WM_APP = 0x8000
WM_LBUTTONDBLCLK = 0x0203
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205

IDI_APPLICATION = 32512

NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIF_INFO = 0x00000010
NIIF_INFO = 0x00000001

MF_STRING = 0x00000000
TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100
TPM_NONOTIFY = 0x0080

TRAY_ICON_ID = 1
TRAY_CALLBACK_MESSAGE = WM_APP + 1
TRAY_COMMAND_SHOW = 1001
TRAY_COMMAND_EXIT = 1002
ERROR_ALREADY_EXISTS = 183
MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
SINGLE_INSTANCE_MUTEX_NAME = "Local\\PasteKeyboardSingleInstance"

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_LCONTROL = 0xA2
VK_RMENU = 0xA5
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_SPACE = 0x20
VK_ESCAPE = 0x1B
VK_BACK = 0x08
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_HOME = 0x24
VK_END = 0x23
VK_PRIOR = 0x21
VK_NEXT = 0x22
VK_DELETE = 0x2E
VK_INSERT = 0x2D

EXTENDED_KEYS = {
    VK_RMENU,
    VK_LCONTROL,
    VK_LEFT,
    VK_RIGHT,
    VK_UP,
    VK_DOWN,
    VK_HOME,
    VK_END,
    VK_PRIOR,
    VK_NEXT,
    VK_DELETE,
    VK_INSERT,
}

KLID_DE_DE = "00000407"
KLID_EN_US = "00000409"
KLID_EN_US_INTL = "00020409"


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("data", INPUTUNION),
    ]


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
        ("lPrivate", wintypes.DWORD),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uTimeoutOrVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", GUID),
        ("hBalloonIcon", wintypes.HICON),
    ]


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
user32.LoadKeyboardLayoutW.restype = wintypes.HKL
user32.VkKeyScanExW.argtypes = [wintypes.WCHAR, wintypes.HKL]
user32.VkKeyScanExW.restype = ctypes.c_short
user32.MapVirtualKeyExW.argtypes = [wintypes.UINT, wintypes.UINT, wintypes.HKL]
user32.MapVirtualKeyExW.restype = wintypes.UINT
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ULONG_PTR]
user32.keybd_event.restype = None
user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.PeekMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
user32.PeekMessageW.restype = wintypes.BOOL
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadIconW.restype = wintypes.HICON
user32.CreateIcon.argtypes = [
    wintypes.HINSTANCE,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.BYTE,
    wintypes.BYTE,
    ctypes.POINTER(wintypes.BYTE),
    ctypes.POINTER(wintypes.BYTE),
]
user32.CreateIcon.restype = wintypes.HICON
user32.DestroyIcon.argtypes = [wintypes.HICON]
user32.DestroyIcon.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.CreatePopupMenu.argtypes = []
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ULONG_PTR, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL
user32.TrackPopupMenu.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.LPVOID,
]
user32.TrackPopupMenu.restype = wintypes.BOOL
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = LONG_PTR
WNDPROC = ctypes.WINFUNCTYPE(LONG_PTR, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LONG_PTR
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
kernel32.GetCurrentThreadId.argtypes = []
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE
kernel32.GetLastError.argtypes = []
kernel32.GetLastError.restype = wintypes.DWORD
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.ReleaseMutex.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


class Win32Error(RuntimeError):
    pass


class SingleInstanceLock:
    def __init__(self, name: str = SINGLE_INSTANCE_MUTEX_NAME) -> None:
        self.name = name
        self.handle: wintypes.HANDLE | None = None
        self.acquired = False

    def acquire(self) -> bool:
        if self.handle is not None:
            return self.acquired

        handle = kernel32.CreateMutexW(None, True, self.name)
        if not handle:
            raise Win32Error("Single-Instance-Sperre konnte nicht erstellt werden.")

        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(handle)
            return False

        self.handle = handle
        self.acquired = True
        return True

    def close(self) -> None:
        if self.handle is None:
            return
        if self.acquired:
            kernel32.ReleaseMutex(self.handle)
        kernel32.CloseHandle(self.handle)
        self.handle = None
        self.acquired = False

    def __enter__(self) -> SingleInstanceLock:
        if not self.acquire():
            raise Win32Error("Paste Keyboard laeuft bereits.")
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.close()


def show_info_message(title: str, message: str) -> None:
    user32.MessageBoxW(None, message, title, MB_OK | MB_ICONINFORMATION)


class HotkeyListener:
    def __init__(self, hotkey_id: int, modifiers: int, vk: int, callback) -> None:
        self.hotkey_id = hotkey_id
        self.modifiers = modifiers
        self.vk = vk
        self.callback = callback
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._ready = threading.Event()
        self._startup_error: Exception | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="HotkeyListener", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)
        if self._startup_error is not None:
            raise self._startup_error
        if self._thread_id is None:
            raise Win32Error("Hotkey-Listener konnte nicht gestartet werden.")

    def _run(self) -> None:
        self._thread_id = int(kernel32.GetCurrentThreadId())
        if not user32.RegisterHotKey(None, self.hotkey_id, self.modifiers, self.vk):
            self._startup_error = Win32Error("Globaler Hotkey konnte nicht registriert werden. Wahrscheinlich ist die Kombination bereits belegt.")
            self._ready.set()
            return

        self._ready.set()
        message = MSG()
        try:
            while user32.GetMessageW(ctypes.byref(message), None, 0, 0) != 0:
                if message.message == WM_HOTKEY:
                    self.callback(int(message.wParam))
                elif message.message == WM_QUIT:
                    break
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)

    def close(self) -> None:
        if self._thread_id is not None:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._thread = None
        self._thread_id = None


class TrayIcon:
    def __init__(self, tooltip: str, callback) -> None:
        self.tooltip = tooltip
        self.callback = callback
        self.hwnd: wintypes.HWND | None = None
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._hinstance: wintypes.HINSTANCE | None = None
        self._class_name = f"PasteKeyboardTray-{uuid.uuid4()}"
        self._ready = threading.Event()
        self._startup_error: Exception | None = None
        self._icon_added = False
        self._icon_handle: wintypes.HICON | None = None
        self._wndproc = WNDPROC(self._handle_window_message)

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="TrayIcon", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)
        if self._startup_error is not None:
            raise self._startup_error
        if self.hwnd is None:
            raise Win32Error("Tray-Fenster konnte nicht gestartet werden.")

    def _run(self) -> None:
        self._thread_id = int(kernel32.GetCurrentThreadId())
        self._hinstance = kernel32.GetModuleHandleW(None)
        window_class = WNDCLASSW()
        window_class.lpfnWndProc = ctypes.cast(self._wndproc, ctypes.c_void_p).value
        window_class.hInstance = self._hinstance
        window_class.lpszClassName = self._class_name

        if not user32.RegisterClassW(ctypes.byref(window_class)):
            self._startup_error = Win32Error("Tray-Fensterklasse konnte nicht registriert werden.")
            self._ready.set()
            return

        self.hwnd = user32.CreateWindowExW(
            0,
            self._class_name,
            self.tooltip,
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            self._hinstance,
            None,
        )
        if not self.hwnd:
            self._startup_error = Win32Error("Tray-Fenster konnte nicht erstellt werden.")
            user32.UnregisterClassW(self._class_name, self._hinstance)
            self._ready.set()
            return

        if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self._notify_data())):
            self._startup_error = Win32Error("Tray-Symbol konnte nicht erstellt werden.")
            user32.DestroyWindow(self.hwnd)
            user32.UnregisterClassW(self._class_name, self._hinstance)
            self.hwnd = None
            self._ready.set()
            return

        self._icon_added = True
        self._ready.set()

        message = MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) != 0:
            user32.DispatchMessageW(ctypes.byref(message))

        self._delete_icon()
        self._destroy_icon_handle()
        if self.hwnd:
            user32.DestroyWindow(self.hwnd)
            self.hwnd = None
        if self._hinstance:
            user32.UnregisterClassW(self._class_name, self._hinstance)
            self._hinstance = None

    def remove(self) -> None:
        self.close()

    def close(self) -> None:
        if self.hwnd is not None:
            self._delete_icon()
        if self._thread_id is not None:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._thread = None
        self._thread_id = None

    def update_tooltip(self, tooltip: str) -> None:
        self.tooltip = tooltip
        if self._icon_added and self.hwnd is not None:
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self._notify_data()))

    def notify(self, title: str, message: str) -> None:
        if not self._icon_added or self.hwnd is None:
            return
        data = self._notify_data()
        data.uFlags |= NIF_INFO
        data.szInfoTitle = title[:63]
        data.szInfo = message[:255]
        data.dwInfoFlags = NIIF_INFO
        shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(data))

    def _delete_icon(self) -> None:
        if self._icon_added and self.hwnd is not None:
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self._notify_data()))
            self._icon_added = False

    def _destroy_icon_handle(self) -> None:
        if self._icon_handle is not None:
            user32.DestroyIcon(self._icon_handle)
            self._icon_handle = None

    def _notify_data(self) -> NOTIFYICONDATAW:
        data = NOTIFYICONDATAW()
        data.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        data.hWnd = self.hwnd
        data.uID = TRAY_ICON_ID
        data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        data.uCallbackMessage = TRAY_CALLBACK_MESSAGE
        data.hIcon = self._app_icon()
        data.szTip = self.tooltip[:127]
        return data

    def _app_icon(self) -> wintypes.HICON:
        if self._icon_handle is None:
            self._icon_handle = create_app_icon()
        return self._icon_handle

    def _handle_window_message(self, hwnd, message, w_param, l_param):
        if message == TRAY_CALLBACK_MESSAGE:
            event = int(l_param)
            if event in {WM_LBUTTONDBLCLK, WM_LBUTTONUP}:
                self.callback("show")
                return 0
            if event == WM_RBUTTONUP:
                self._show_menu()
                return 0

        if message == WM_DESTROY:
            return 0

        return user32.DefWindowProcW(hwnd, message, w_param, l_param)

    def _show_menu(self) -> None:
        menu = user32.CreatePopupMenu()
        if not menu:
            return
        try:
            user32.AppendMenuW(menu, MF_STRING, TRAY_COMMAND_SHOW, "Oeffnen")
            user32.AppendMenuW(menu, MF_STRING, TRAY_COMMAND_EXIT, "Beenden")

            point = POINT()
            if not user32.GetCursorPos(ctypes.byref(point)):
                return
            user32.SetForegroundWindow(self.hwnd)
            command = user32.TrackPopupMenu(
                menu,
                TPM_RIGHTBUTTON | TPM_RETURNCMD | TPM_NONOTIFY,
                point.x,
                point.y,
                0,
                self.hwnd,
                None,
            )
            if command == TRAY_COMMAND_SHOW:
                self.callback("show")
            elif command == TRAY_COMMAND_EXIT:
                self.callback("exit")
            user32.PostMessageW(self.hwnd, 0, 0, 0)
        finally:
            user32.DestroyMenu(menu)


def create_app_icon(size: int = 32) -> wintypes.HICON:
    pixels = bytearray()
    keyboard_left = size // 5
    keyboard_right = size - keyboard_left
    keyboard_top = size // 3
    keyboard_bottom = size - size // 4

    for y in range(size):
        for x in range(size):
            r, g, b, a = 0x18, 0x7F, 0xA7, 0xFF
            if keyboard_left <= x < keyboard_right and keyboard_top <= y < keyboard_bottom:
                r, g, b = 0xF4, 0xF7, 0xFB
                if (
                    x in {keyboard_left, keyboard_right - 1}
                    or y in {keyboard_top, keyboard_bottom - 1}
                    or (y == keyboard_top + 4 and keyboard_left + 3 <= x < keyboard_right - 3)
                    or ((y - keyboard_top) % 5 == 0 and (x - keyboard_left) % 5 == 0)
                ):
                    r, g, b = 0x0F, 0x3F, 0x56
            elif x >= size - size // 3 and y < size // 3 and x - y > size // 4:
                r, g, b = 0xFF, 0xC8, 0x34
            pixels.extend((b, g, r, a))

    and_mask = (wintypes.BYTE * ((size * size) // 8))()
    xor_mask = (wintypes.BYTE * len(pixels)).from_buffer_copy(bytes(pixels))
    icon = user32.CreateIcon(None, size, size, 1, 32, and_mask, xor_mask)
    if not icon:
        return user32.LoadIconW(None, ctypes.cast(ctypes.c_void_p(IDI_APPLICATION), wintypes.LPCWSTR))
    return icon


@dataclass(frozen=True, slots=True)
class KeyPress:
    vk: int
    scan_code: int
    modifiers: tuple[str, ...] = ()
    literal_space_after: bool = False


def load_keyboard_layout(klid: str) -> int:
    handle = user32.LoadKeyboardLayoutW(klid, 0)
    if not handle:
        raise Win32Error(f"Keyboard-Layout {klid} konnte nicht geladen werden.")
    return int(handle)


def vk_key_scan_ex(char: str, layout_handle: int) -> int:
    return int(user32.VkKeyScanExW(char, wintypes.HKL(layout_handle)))


def map_virtual_key_ex(vk: int, layout_handle: int) -> int:
    return int(user32.MapVirtualKeyExW(vk, MAPVK_VK_TO_VSC, wintypes.HKL(layout_handle)))


def register_hotkey(hwnd: int, hotkey_id: int, modifiers: int, vk: int) -> None:
    if not user32.RegisterHotKey(wintypes.HWND(hwnd), hotkey_id, modifiers, vk):
        raise Win32Error("Globaler Hotkey konnte nicht registriert werden. Wahrscheinlich ist die Kombination bereits belegt.")


def unregister_hotkey(hwnd: int, hotkey_id: int) -> None:
    user32.UnregisterHotKey(wintypes.HWND(hwnd), hotkey_id)


def poll_hotkey_ids() -> list[int]:
    message = MSG()
    hotkey_ids: list[int] = []
    while user32.PeekMessageW(ctypes.byref(message), None, WM_HOTKEY, WM_HOTKEY, PM_REMOVE):
        hotkey_ids.append(int(message.wParam))
    return hotkey_ids


def is_key_down(vk: int) -> bool:
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0


def _keyboard_input(scan_code: int, flags: int) -> INPUT:
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )


def _modifier_scan_code(name: str) -> tuple[int, int]:
    if name == "shift":
        return map_virtual_key_ex(VK_SHIFT, 0), 0
    if name == "ctrl":
        return map_virtual_key_ex(VK_LCONTROL, 0), 0
    if name == "alt":
        return map_virtual_key_ex(VK_RMENU, 0), KEYEVENTF_EXTENDEDKEY
    raise Win32Error(f"Unbekannter Modifier: {name}")


def _modifier_vk(name: str) -> tuple[int, int]:
    if name == "shift":
        return VK_SHIFT, 0
    if name == "ctrl":
        return VK_CONTROL, 0
    if name == "alt":
        return VK_RMENU, KEYEVENTF_EXTENDEDKEY
    raise Win32Error(f"Unbekannter Modifier: {name}")


def send_key_press(press: KeyPress) -> None:
    try:
        _send_key_press_send_input(press)
        return
    except Win32Error as exc:
        send_input_error = ctypes.get_last_error()
        if send_input_error != 87:
            raise exc

    try:
        _send_key_press_keybd_event(press)
    except Exception as exc:
        raise Win32Error(f"Tasteneingabe fehlgeschlagen. SendInput-Fehler 87, keybd_event-Fehler: {exc}") from exc


def _send_key_press_send_input(press: KeyPress) -> None:
    inputs: list[INPUT] = []
    modifier_data = [_modifier_scan_code(name) for name in press.modifiers]

    for scan_code, extra_flags in modifier_data:
        inputs.append(_keyboard_input(scan_code, KEYEVENTF_SCANCODE | extra_flags))

    main_flags = KEYEVENTF_SCANCODE
    if press.vk in EXTENDED_KEYS:
        main_flags |= KEYEVENTF_EXTENDEDKEY

    inputs.append(_keyboard_input(press.scan_code, main_flags))
    inputs.append(_keyboard_input(press.scan_code, main_flags | KEYEVENTF_KEYUP))

    for scan_code, extra_flags in reversed(modifier_data):
        inputs.append(_keyboard_input(scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP | extra_flags))

    if press.literal_space_after:
        space_scan = map_virtual_key_ex(VK_SPACE, 0)
        inputs.append(_keyboard_input(space_scan, KEYEVENTF_SCANCODE))
        inputs.append(_keyboard_input(space_scan, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP))

    array_type = INPUT * len(inputs)
    sent = user32.SendInput(len(inputs), array_type(*inputs), ctypes.sizeof(INPUT))
    if sent != len(inputs):
        raise Win32Error("SendInput konnte nicht alle Tastendrücke senden.")


def _send_virtual_key(vk: int, scan_code: int, flags: int) -> None:
    user32.keybd_event(vk & 0xFF, scan_code & 0xFF, flags, 0)


def _send_key_press_keybd_event(press: KeyPress) -> None:
    modifier_data = [_modifier_vk(name) for name in press.modifiers]

    for vk, extra_flags in modifier_data:
        scan_code = map_virtual_key_ex(vk, 0)
        _send_virtual_key(vk, scan_code, extra_flags)

    main_flags = 0
    if press.vk in EXTENDED_KEYS:
        main_flags |= KEYEVENTF_EXTENDEDKEY

    _send_virtual_key(press.vk, press.scan_code, main_flags)
    _send_virtual_key(press.vk, press.scan_code, main_flags | KEYEVENTF_KEYUP)

    for vk, extra_flags in reversed(modifier_data):
        scan_code = map_virtual_key_ex(vk, 0)
        _send_virtual_key(vk, scan_code, extra_flags | KEYEVENTF_KEYUP)

    if press.literal_space_after:
        space_scan = map_virtual_key_ex(VK_SPACE, 0)
        _send_virtual_key(VK_SPACE, space_scan, 0)
        _send_virtual_key(VK_SPACE, space_scan, KEYEVENTF_KEYUP)


def wait_for_modifiers_release(timeout_ms: int = 1000) -> None:
    watched_keys = [VK_SHIFT, VK_CONTROL, VK_MENU]
    deadline = time.monotonic() + (timeout_ms / 1000.0)

    while time.monotonic() < deadline:
        if all((user32.GetAsyncKeyState(key) & 0x8000) == 0 for key in watched_keys):
            return
        time.sleep(0.01)
