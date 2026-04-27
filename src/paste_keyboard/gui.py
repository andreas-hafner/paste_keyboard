from __future__ import annotations

import ctypes
import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from . import win32
from .config import AppSettings, load_settings, save_settings
from .hotkeys import ParsedHotkey, parse_hotkey
from .layouts import BUILTIN_LAYOUTS
from .typing import TypingError, type_text


HOTKEY_ID = 1
MAX_CLIPBOARD_TEXT_CHARS = 1000
MINIMIZE_RETRY_DELAYS_MS = (50, 250, 750)
SW_FORCEMINIMIZE = 11
APP_TITLE = "Paste Keyboard"
TASKBAR_STATUS_MAX_CHARS = 96


class PasteKeyboardApp:
    def __init__(self, start_minimized: bool = False) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("760x520")
        self.root.minsize(680, 480)

        self.settings = load_settings()
        self.hotkey_queue: queue.SimpleQueue[int] = queue.SimpleQueue()
        self.hotkey_listener: win32.HotkeyListener | None = None
        self.current_hotkey: ParsedHotkey | None = None
        self.typing_in_progress = False

        self.hotkey_var = tk.StringVar(value=self.settings.hotkey)
        self.layout_var = tk.StringVar(value=self.settings.layout_id)
        self.start_delay_var = tk.IntVar(value=self.settings.start_delay_ms)
        self.key_delay_var = tk.IntVar(value=self.settings.key_delay_ms)
        self.skip_unsupported_var = tk.BooleanVar(value=self.settings.skip_unsupported)
        self.status_var = tk.StringVar(value="")

        self._build_ui()
        self._set_status("Bereit.")
        self._register_hotkey_from_form(initial=True)
        self._poll_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if start_minimized:
            self._schedule_minimized_start()

    def _schedule_minimized_start(self) -> None:
        for delay_ms in MINIMIZE_RETRY_DELAYS_MS:
            self.root.after(delay_ms, self._minimize_window)

    def _minimize_window(self) -> None:
        self.root.update_idletasks()
        self.root.state("iconic")
        try:
            ctypes.windll.user32.ShowWindowAsync(self.root.winfo_id(), SW_FORCEMINIMIZE)
        except (AttributeError, tk.TclError, OSError):
            pass

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        settings_frame = ttk.LabelFrame(self.root, text="Einstellungen", padding=12)
        settings_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Globaler Hotkey").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(settings_frame, textvariable=self.hotkey_var).grid(row=0, column=1, sticky="ew", pady=4)

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

        ttk.Checkbutton(
            settings_frame,
            text="Nicht unterstuetzte Zeichen ueberspringen",
            variable=self.skip_unsupported_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))

        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))

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

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)
        if not hasattr(self, "root"):
            return
        taskbar_message = self._taskbar_status_text(message)
        if taskbar_message:
            self.root.title(f"{APP_TITLE} - {taskbar_message}")
        else:
            self.root.title(APP_TITLE)

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
        )

    def _save_settings(self) -> None:
        try:
            settings = self._collect_settings()
            parsed = parse_hotkey(settings.hotkey)
            if settings.layout_id not in BUILTIN_LAYOUTS:
                raise ValueError("Bitte ein gueltiges Ziel-Layout waehlen.")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Ungueltige Einstellungen", str(exc))
            return

        try:
            self._register_hotkey(parsed)
        except win32.Win32Error as exc:
            self._sync_hotkey_form_with_active_listener()
            self._set_status(self._active_hotkey_status())
            messagebox.showerror("Hotkey konnte nicht aktiviert werden", str(exc))
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

    def _sync_hotkey_form_with_active_listener(self) -> None:
        if self.current_hotkey is not None:
            self.hotkey_var.set(self.current_hotkey.display)

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
        if len(text) > MAX_CLIPBOARD_TEXT_CHARS:
            raise RuntimeError(
                f"Zwischenablage ist zu gross zum Tippen ({len(text)} Zeichen, Limit {MAX_CLIPBOARD_TEXT_CHARS})."
            )
        return text

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
            count, skipped = type_text(
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
            suffix = ""
            if skipped:
                rendered = ", ".join(ch.encode("unicode_escape").decode("ascii") for ch in skipped[:8])
                suffix = f" Uebersprungen: {rendered}"
            self._finish_typing(success=f"{source_label}: {count} Tastendruecke gesendet.{suffix}")

        self.root.after(0, finish)

    def _finish_typing(self, success: str | None = None, error: str | None = None) -> None:
        self.typing_in_progress = False
        if success is not None:
            self._set_status(success)
        elif error is not None:
            self._set_status(error)

    def _on_close(self) -> None:
        if self.hotkey_listener is not None:
            self.hotkey_listener.close()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_app(start_minimized: bool = False) -> None:
    app = PasteKeyboardApp(start_minimized=start_minimized)
    app.run()
