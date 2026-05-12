from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from . import win32
from .config import DEFAULT_SETTINGS, AppSettings, load_settings, save_settings
from .hotkeys import ParsedHotkey, parse_hotkey
from .layouts import BUILTIN_LAYOUTS
from .typing import TypingError, type_text


HOTKEY_ID = 1
MAX_CLIPBOARD_TEXT_CHARS = DEFAULT_SETTINGS.clipboard_typing_limit
MINIMIZE_RETRY_DELAYS_MS = (50, 250, 750)
APP_TITLE = "Paste Keyboard"
TASKBAR_STATUS_MAX_CHARS = 96
FINISH_POPUP_MAX_CHARS = 180
FINISH_POPUP_MARGIN_X = 24
FINISH_POPUP_MARGIN_Y = 64
FINISH_POPUP_DURATION_MS = 3500
HOTKEY_CAPTURE_MODIFIER_KEYSYMS = {
    "Alt_L",
    "Alt_R",
    "Control_L",
    "Control_R",
    "Shift_L",
    "Shift_R",
    "Super_L",
    "Super_R",
    "Win_L",
    "Win_R",
}
HOTKEY_CAPTURE_SPECIAL_KEYS = {
    "Delete": "Delete",
    "End": "End",
    "Escape": "Escape",
    "Home": "Home",
    "Insert": "Insert",
    "Next": "PageDown",
    "Prior": "PageUp",
    "Return": "Enter",
    "space": "Space",
    "Tab": "Tab",
}


class PasteKeyboardApp:
    def __init__(self, start_minimized: bool = False) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("760x520")
        self.root.minsize(680, 480)
        self._hide_window_from_taskbar()

        self.settings = load_settings()
        self.hotkey_queue: queue.SimpleQueue[int] = queue.SimpleQueue()
        self.tray_queue: queue.SimpleQueue[str] = queue.SimpleQueue()
        self.hotkey_listener: win32.HotkeyListener | None = None
        self.current_hotkey: ParsedHotkey | None = None
        self.tray_icon: win32.TrayIcon | None = None
        self.typing_in_progress = False
        self.exiting = False
        self.hotkey_capture_active = False
        self.hotkey_capture_bind_id: str | None = None
        self.hotkey_capture_paused_hotkey: ParsedHotkey | None = None

        self.hotkey_var = tk.StringVar(value=self.settings.hotkey)
        self.layout_var = tk.StringVar(value=self.settings.layout_id)
        self.start_delay_var = tk.IntVar(value=self.settings.start_delay_ms)
        self.key_delay_var = tk.IntVar(value=self.settings.key_delay_ms)
        self.clipboard_typing_limit_var = tk.IntVar(value=self.settings.clipboard_typing_limit)
        self.notify_on_finish_var = tk.BooleanVar(value=self.settings.notify_on_finish)
        self.skip_unsupported_var = tk.BooleanVar(value=self.settings.skip_unsupported)
        self.status_var = tk.StringVar(value="")

        self._build_ui()
        self._set_status("Bereit.")
        self._setup_tray_icon()
        self._register_hotkey_from_form(initial=True)
        self._poll_hotkeys()
        self._poll_tray_events()
        self.root.bind("<Unmap>", self._on_unmap)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if start_minimized:
            self._schedule_minimized_start()

    def _schedule_minimized_start(self) -> None:
        for delay_ms in MINIMIZE_RETRY_DELAYS_MS:
            self.root.after(delay_ms, self._minimize_window)

    def _hide_window_from_taskbar(self) -> None:
        try:
            self.root.attributes("-toolwindow", True)
        except tk.TclError:
            pass

    def _minimize_window(self) -> None:
        self.root.update_idletasks()
        self._hide_to_tray()

    def _setup_tray_icon(self) -> None:
        try:
            self.tray_icon = win32.TrayIcon(
                APP_TITLE,
                self.tray_queue.put,
            )
            self.tray_icon.start()
        except (tk.TclError, win32.Win32Error):
            self.tray_icon = None

    def _on_unmap(self, _event: tk.Event) -> None:
        if self.exiting:
            return
        try:
            if self.root.state() == "iconic":
                self.root.after(0, self._hide_to_tray)
        except tk.TclError:
            pass

    def _hide_to_tray(self) -> None:
        if self.exiting:
            return
        try:
            self.root.withdraw()
        except tk.TclError:
            pass

    def _show_from_tray(self) -> None:
        try:
            self.root.deiconify()
            self.root.state("normal")
            self.root.lift()
            self.root.focus_force()
        except tk.TclError:
            pass

    def _poll_tray_events(self) -> None:
        if self.exiting:
            return
        while True:
            try:
                event = self.tray_queue.get_nowait()
            except queue.Empty:
                break
            if event == "show":
                self._show_from_tray()
            elif event == "exit":
                self._exit_app()
                return
        if not self.exiting:
            self.root.after(100, self._poll_tray_events)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        settings_frame = ttk.LabelFrame(self.root, text="Einstellungen", padding=12)
        settings_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Globaler Hotkey").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        hotkey_frame = ttk.Frame(settings_frame)
        hotkey_frame.grid(row=0, column=1, sticky="ew", pady=4)
        hotkey_frame.columnconfigure(0, weight=1)
        self.hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, state="readonly")
        self.hotkey_entry.grid(row=0, column=0, sticky="ew")
        self.hotkey_capture_button = ttk.Button(hotkey_frame, text="Aufzeichnen", command=self._toggle_hotkey_capture)
        self.hotkey_capture_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(settings_frame, text="Ziel-Layout").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        layout_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.layout_var,
            state="readonly",
            values=list(BUILTIN_LAYOUTS.keys()),
        )
        layout_combo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(settings_frame, text="Startverzoegerung (ms)").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Spinbox(settings_frame, from_=0, to=5000, increment=50, textvariable=self.start_delay_var).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(settings_frame, text="Tastendelay (ms)").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Spinbox(settings_frame, from_=0, to=1000, increment=5, textvariable=self.key_delay_var).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(settings_frame, text="Zwischenablage-Limit beim Tippen").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Spinbox(
            settings_frame,
            from_=1,
            to=1000000,
            increment=100,
            textvariable=self.clipboard_typing_limit_var,
        ).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Checkbutton(
            settings_frame,
            text="Nicht unterstuetzte Zeichen ueberspringen",
            variable=self.skip_unsupported_var,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 0))

        ttk.Checkbutton(
            settings_frame,
            text="Benachrichtigung nach Tippvorgang",
            variable=self.notify_on_finish_var,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 0))

        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(button_frame, text="Einstellungen speichern", command=self._save_settings).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_frame, text="Zwischenablage tippen", command=self._type_clipboard_from_button).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_frame, text="Zwischenablage laden", command=self._load_clipboard_into_editor).grid(row=0, column=2)

        editor_frame = ttk.LabelFrame(self.root, text="Test- / Vorschautext", padding=12)
        editor_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(editor_frame, wrap="word", font=("Consolas", 11))
        self.editor.grid(row=0, column=0, sticky="nsew")

        editor_buttons = ttk.Frame(editor_frame)
        editor_buttons.grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Button(editor_buttons, text="Textfeld tippen", command=self._type_editor_text).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(editor_buttons, text="Textfeld leeren", command=lambda: self.editor.delete("1.0", "end")).grid(row=0, column=1)

    def _toggle_hotkey_capture(self) -> None:
        if self.hotkey_capture_active:
            self._stop_hotkey_capture(restore_listener=True)
            self._set_status("Hotkey-Aufzeichnung abgebrochen.")
            return
        self._start_hotkey_capture()

    def _start_hotkey_capture(self) -> None:
        self.hotkey_capture_active = True
        self.hotkey_capture_paused_hotkey = self.current_hotkey
        if self.hotkey_listener is not None:
            self.hotkey_listener.close()
            self.hotkey_listener = None

        self.hotkey_entry.configure(state="normal")
        self.hotkey_capture_button.configure(text="Abbrechen")
        self.hotkey_capture_bind_id = self.hotkey_entry.bind("<KeyPress>", self._on_hotkey_capture_key, add="+")
        self.hotkey_entry.focus_set()
        self.hotkey_entry.selection_range(0, "end")
        self.hotkey_entry.configure(state="readonly")
        self._set_status("Hotkey-Aufzeichnung aktiv: Tastenkombination druecken. Escape bricht ab.")

    def _stop_hotkey_capture(self, restore_listener: bool) -> None:
        if self.hotkey_capture_bind_id is not None:
            self.hotkey_entry.unbind("<KeyPress>", self.hotkey_capture_bind_id)
            self.hotkey_capture_bind_id = None
        self.hotkey_capture_active = False
        self.hotkey_entry.configure(state="readonly")
        self.hotkey_capture_button.configure(text="Aufzeichnen")
        if restore_listener:
            self._restore_hotkey_listener_after_capture()
        self.hotkey_capture_paused_hotkey = None

    def _restore_hotkey_listener_after_capture(self) -> None:
        if self.hotkey_listener is not None or self.hotkey_capture_paused_hotkey is None:
            return
        try:
            self.hotkey_listener = self._start_hotkey_listener(self.hotkey_capture_paused_hotkey)
            self.current_hotkey = self.hotkey_capture_paused_hotkey
        except win32.Win32Error as exc:
            self.current_hotkey = None
            self._set_status(f"Hotkey konnte nach Aufzeichnung nicht wieder aktiviert werden: {exc}")

    def _on_hotkey_capture_key(self, event: tk.Event) -> str:
        captured = self._hotkey_from_key_event(event)
        if captured is None:
            if getattr(event, "keysym", "") == "Escape":
                self._stop_hotkey_capture(restore_listener=True)
                self._set_status("Hotkey-Aufzeichnung abgebrochen.")
            return "break"

        self.hotkey_var.set(captured)
        self._stop_hotkey_capture(restore_listener=True)
        self._set_status(f"Hotkey uebernommen: {captured}. Einstellungen speichern, um ihn zu aktivieren.")
        return "break"

    def _hotkey_from_key_event(self, event: tk.Event) -> str | None:
        keysym = getattr(event, "keysym", "")
        if keysym in HOTKEY_CAPTURE_MODIFIER_KEYSYMS:
            return None
        key = self._hotkey_main_key_from_event(event)
        if key is None:
            return None

        modifiers = self._hotkey_modifiers_from_keyboard()
        if not modifiers:
            return None
        return "+".join([*modifiers, key])

    def _hotkey_modifiers_from_keyboard(self) -> list[str]:
        modifiers: list[str] = []
        if win32.is_key_down(win32.VK_CONTROL):
            modifiers.append("Ctrl")
        if win32.is_key_down(win32.VK_MENU):
            modifiers.append("Alt")
        if win32.is_key_down(win32.VK_SHIFT):
            modifiers.append("Shift")
        if win32.is_key_down(win32.VK_LWIN) or win32.is_key_down(win32.VK_RWIN):
            modifiers.append("Win")
        return modifiers

    def _hotkey_main_key_from_event(self, event: tk.Event) -> str | None:
        keysym = getattr(event, "keysym", "")
        char = getattr(event, "char", "")
        if keysym in HOTKEY_CAPTURE_SPECIAL_KEYS:
            return HOTKEY_CAPTURE_SPECIAL_KEYS[keysym]
        if keysym.startswith("F") and keysym[1:].isdigit():
            index = int(keysym[1:])
            if 1 <= index <= 24:
                return keysym
        if len(keysym) == 1 and keysym.isalnum():
            return keysym.upper()
        if len(char) == 1 and char.isalnum():
            return char.upper()
        return None

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)
        if not hasattr(self, "root"):
            return
        taskbar_message = self._taskbar_status_text(message)
        if taskbar_message:
            self.root.title(f"{APP_TITLE} - {taskbar_message}")
        else:
            self.root.title(APP_TITLE)
        if getattr(self, "tray_icon", None) is not None:
            self.tray_icon.update_tooltip(f"{APP_TITLE} - {taskbar_message}" if taskbar_message else APP_TITLE)

    def _taskbar_status_text(self, message: str) -> str:
        collapsed = " ".join(message.split())
        if len(collapsed) <= TASKBAR_STATUS_MAX_CHARS:
            return collapsed
        return f"{collapsed[: TASKBAR_STATUS_MAX_CHARS - 3]}..."

    def _collect_settings(self) -> AppSettings:
        return AppSettings(
            hotkey=self.hotkey_var.get().strip(),
            layout_id=self.layout_var.get().strip(),
            start_delay_ms=int(self.start_delay_var.get()),
            key_delay_ms=int(self.key_delay_var.get()),
            skip_unsupported=bool(self.skip_unsupported_var.get()),
            clipboard_typing_limit=int(self.clipboard_typing_limit_var.get()),
            notify_on_finish=bool(self.notify_on_finish_var.get()),
        )

    def _save_settings(self) -> None:
        try:
            settings = self._collect_settings()
            parsed = parse_hotkey(settings.hotkey)
            if settings.layout_id not in BUILTIN_LAYOUTS:
                raise ValueError("Bitte ein gueltiges Ziel-Layout waehlen.")
            if settings.clipboard_typing_limit < 1:
                raise ValueError("Zwischenablage-Limit muss mindestens 1 sein.")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Ungueltige Einstellungen", str(exc))
            return

        try:
            self._register_hotkey(parsed)
        except win32.Win32Error as exc:
            message = f"Hotkey konnte nicht aktiviert werden: {exc} {self._active_hotkey_status()}"
            self._set_status(f"Einstellungen nicht gespeichert. {message}")
            messagebox.showerror("Hotkey nicht gespeichert", message)
            return

        self.settings = settings
        self.hotkey_var.set(parsed.display)
        save_settings(settings)
        self._set_status(f"Einstellungen gespeichert. Hotkey aktiv: {parsed.display}")

    def _register_hotkey_from_form(self, initial: bool = False) -> None:
        try:
            parsed = parse_hotkey(self.hotkey_var.get())
            self.hotkey_var.set(parsed.display)
            self._register_hotkey(parsed)
            if initial:
                self._set_status(f"Bereit. Hotkey aktiv: {parsed.display}")
        except ValueError as exc:
            if initial:
                self._set_status(f"Hotkey ungueltig: {exc}")
        except win32.Win32Error as exc:
            if initial:
                self._set_status(f"Hotkey nicht aktiv: {exc}")

    def _register_hotkey(self, parsed: ParsedHotkey) -> None:
        if parsed == self.current_hotkey and self.hotkey_listener is not None:
            return

        previous_listener = self.hotkey_listener
        previous_hotkey = self.current_hotkey

        if previous_listener is None:
            listener = self._start_hotkey_listener(parsed)
            self.hotkey_listener = listener
            self.current_hotkey = parsed
            return

        self.hotkey_listener = None
        self.current_hotkey = None
        previous_listener.close()

        try:
            listener = self._start_hotkey_listener(parsed)
        except win32.Win32Error as exc:
            if previous_hotkey is None:
                raise
            try:
                restored_listener = self._start_hotkey_listener(previous_hotkey)
            except win32.Win32Error as restore_exc:
                raise win32.Win32Error(
                    f"{exc} Vorheriger Hotkey konnte nicht wiederhergestellt werden: {restore_exc}"
                ) from exc
            self.hotkey_listener = restored_listener
            self.current_hotkey = previous_hotkey
            raise exc

        self.hotkey_listener = listener
        self.current_hotkey = parsed

    def _start_hotkey_listener(self, parsed: ParsedHotkey) -> win32.HotkeyListener:
        listener = win32.HotkeyListener(HOTKEY_ID, parsed.modifiers, parsed.vk, self.hotkey_queue.put)
        listener.start()
        return listener

    def _active_hotkey_status(self) -> str:
        if self.current_hotkey is None:
            return "Kein Hotkey aktiv."
        return f"Hotkey weiter aktiv: {self.current_hotkey.display}"

    def _poll_hotkeys(self) -> None:
        while True:
            try:
                hotkey_id = self.hotkey_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_hotkey(hotkey_id)
        self.root.after(50, self._poll_hotkeys)

    def _handle_hotkey(self, hotkey_id: int) -> None:
        if hotkey_id == HOTKEY_ID:
            self._type_clipboard_from_hotkey()

    def _load_clipboard_text(self) -> str:
        try:
            text = self.root.clipboard_get()
        except tk.TclError as exc:
            raise RuntimeError(
                "Zwischenablage enthaelt keinen Text. Bilder, Dateien und andere Formate werden nicht unterstuetzt."
            ) from exc
        if not text:
            raise RuntimeError("Zwischenablage ist leer.")
        return text

    def _load_clipboard_text_for_typing(self) -> str:
        text = self._load_clipboard_text()
        limit = self._clipboard_typing_limit()
        if len(text) > limit:
            raise RuntimeError(
                f"Zwischenablage ist zu gross zum Tippen ({len(text)} Zeichen, Limit {limit})."
            )
        return text

    def _clipboard_typing_limit(self) -> int:
        try:
            limit_var = self.clipboard_typing_limit_var
        except AttributeError:
            return DEFAULT_SETTINGS.clipboard_typing_limit
        try:
            return max(1, int(limit_var.get()))
        except (ValueError, tk.TclError):
            return DEFAULT_SETTINGS.clipboard_typing_limit

    def _load_clipboard_into_editor(self) -> None:
        try:
            text = self._load_clipboard_text()
        except RuntimeError as exc:
            messagebox.showerror("Zwischenablage", str(exc))
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        self._set_status("Zwischenablage in das Textfeld geladen.")

    def _type_clipboard_from_button(self) -> None:
        try:
            text = self._load_clipboard_text_for_typing()
        except RuntimeError as exc:
            messagebox.showerror("Zwischenablage", str(exc))
            return
        self._start_typing(text, source_label="Zwischenablage")

    def _type_clipboard_from_hotkey(self) -> None:
        try:
            text = self._load_clipboard_text_for_typing()
        except RuntimeError as exc:
            self._set_status(str(exc))
            return
        self._start_typing(text, source_label="Zwischenablage via Hotkey")

    def _type_editor_text(self) -> None:
        text = self.editor.get("1.0", "end-1c")
        if not text:
            messagebox.showerror("Textfeld", "Im Textfeld steht nichts.")
            return
        self._start_typing(text, source_label="Textfeld")

    def _start_typing(self, text: str, source_label: str) -> None:
        if self.typing_in_progress:
            self._set_status("Es laeuft bereits ein Tippvorgang.")
            return

        try:
            settings = self._collect_settings()
            if settings.layout_id not in BUILTIN_LAYOUTS:
                raise ValueError("Bitte ein gueltiges Ziel-Layout waehlen.")
            if settings.clipboard_typing_limit < 1:
                raise ValueError("Zwischenablage-Limit muss mindestens 1 sein.")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Ungueltige Einstellungen", str(exc))
            return

        self.typing_in_progress = True
        self._set_status(f"{source_label}: sende Tastendruecke...")

        thread = threading.Thread(
            target=self._typing_worker,
            args=(text, settings, source_label),
            daemon=True,
        )
        thread.start()

    def _typing_worker(self, text: str, settings: AppSettings, source_label: str) -> None:
        try:
            _count, skipped = type_text(
                text=text,
                layout_id=settings.layout_id,
                start_delay_ms=settings.start_delay_ms,
                key_delay_ms=settings.key_delay_ms,
                skip_unsupported=settings.skip_unsupported,
            )
        except (TypingError, win32.Win32Error) as exc:
            message = str(exc)
            self.root.after(0, lambda message=message: self._finish_typing(error=message))
            return
        except Exception as exc:
            message = f"Unerwarteter Fehler: {exc}"
            self.root.after(0, lambda message=message: self._finish_typing(error=message))
            return

        def finish() -> None:
            message = "Einfuegen beendet."
            if skipped:
                rendered = ", ".join(ch.encode("unicode_escape").decode("ascii") for ch in skipped[:8])
                message = f"{message} Uebersprungen: {rendered}"
            self._finish_typing(success=message)

        self.root.after(0, finish)

    def _finish_typing(self, success: str | None = None, error: str | None = None) -> None:
        self.typing_in_progress = False
        if success is not None:
            self._set_status(success)
            self._notify_typing_finished(success)
        elif error is not None:
            self._set_status(error)
            self._notify_typing_finished(error)

    def _notify_typing_finished(self, message: str) -> None:
        try:
            enabled = bool(self.notify_on_finish_var.get())
        except (AttributeError, tk.TclError):
            enabled = False
        if not enabled:
            return
        if getattr(self, "tray_icon", None) is not None:
            try:
                self.tray_icon.notify("Paste Keyboard", message)
            except win32.Win32Error:
                pass
        self._show_finish_popup(message)

    def _show_finish_popup(self, message: str) -> None:
        try:
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            popup.configure(background="#1f2937")

            content = tk.Frame(popup, background="#1f2937", padx=14, pady=10)
            content.grid(row=0, column=0, sticky="nsew")
            tk.Label(
                content,
                text="Paste Keyboard",
                background="#1f2937",
                foreground="#ffffff",
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=0, sticky="w")
            tk.Label(
                content,
                text=self._finish_popup_text(message),
                background="#1f2937",
                foreground="#e5e7eb",
                font=("Segoe UI", 9),
                justify="left",
                wraplength=320,
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

            popup.update_idletasks()
            popup.geometry(self._finish_popup_geometry(popup.winfo_reqwidth(), popup.winfo_reqheight()))
            popup.after(FINISH_POPUP_DURATION_MS, popup.destroy)
        except tk.TclError:
            return

    def _finish_popup_text(self, message: str) -> str:
        collapsed = " ".join(message.split())
        if len(collapsed) <= FINISH_POPUP_MAX_CHARS:
            return collapsed
        return f"{collapsed[: FINISH_POPUP_MAX_CHARS - 3]}..."

    def _finish_popup_geometry(self, width: int, height: int) -> str:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, screen_width - width - FINISH_POPUP_MARGIN_X)
        y = max(0, screen_height - height - FINISH_POPUP_MARGIN_Y)
        return f"{width}x{height}+{x}+{y}"

    def _on_close(self) -> None:
        self._hide_to_tray()

    def _exit_app(self) -> None:
        self.exiting = True
        if self.tray_icon is not None:
            self.tray_icon.close()
            self.tray_icon = None
        if self.hotkey_listener is not None:
            self.hotkey_listener.close()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_app(start_minimized: bool = False) -> None:
    app = PasteKeyboardApp(start_minimized=start_minimized)
    app.run()
