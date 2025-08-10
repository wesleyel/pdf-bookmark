from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Optional

from .core import generate_bookmarks, parse_toc_lines


# Run blocking CPU/IO bound function in thread to keep UI responsive
async def run_in_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Bookmark")
        self.root.geometry("820x640")

        self.input_path: Optional[Path] = None
        self.output_path: Optional[Path] = None

        self._build_ui()
        self._setup_event_loop()

    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Input selector
        in_row = ttk.Frame(frm)
        in_row.pack(fill=tk.X)
        ttk.Label(in_row, text="Input PDF:").pack(side=tk.LEFT)
        self.in_var = tk.StringVar()
        self.in_entry = ttk.Entry(in_row, textvariable=self.in_var)
        self.in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(in_row, text="Browse", command=self.choose_input).pack(side=tk.LEFT)

        # Output path
        out_row = ttk.Frame(frm)
        out_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(out_row, text="Output PDF:").pack(side=tk.LEFT)
        self.out_var = tk.StringVar()
        self.out_entry = ttk.Entry(out_row, textvariable=self.out_var)
        self.out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(out_row, text="Browse", command=self.choose_output).pack(side=tk.LEFT)

        # Offset + Controls
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill=tk.X, pady=10)
        ttk.Label(ctrl, text="Page Offset:").pack(side=tk.LEFT)
        self.offset_var = tk.StringVar(value="0")
        self.offset_entry = ttk.Entry(ctrl, textvariable=self.offset_var, width=6)
        self.offset_entry.pack(side=tk.LEFT, padx=(4, 12))
        ttk.Button(ctrl, text="Generate", command=self._on_generate).pack(side=tk.LEFT, padx=8)

        # TOC input
        toc_row = ttk.Frame(frm)
        toc_row.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(toc_row)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = ttk.Frame(toc_row, width=260)
        right.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="TOC text:").pack(anchor=tk.W)
        self.toc_text = tk.Text(left, height=10)
        self.toc_text.pack(fill=tk.BOTH, expand=True)
        btns = ttk.Frame(left)
        btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Parse TOC Text", command=self._on_parse_toc_text).pack(side=tk.LEFT)

        # Tree view for headings
        self.tree = ttk.Treeview(right, columns=("title", "page", "level"), show="headings", height=15)
        self.tree.heading("title", text="Title")
        self.tree.heading("page", text="Page")
        self.tree.heading("level", text="Level")
        self.tree.column("title", width=160)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status_var).pack(anchor=tk.W, pady=(8, 0))

    def _setup_event_loop(self) -> None:
        # tkinter mainloop is blocking; integrate asyncio by polling
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()
        self.root.after(50, self._poll_loop)

    def _poll_loop(self) -> None:
        # UI heartbeat
        if self.root.winfo_exists():
            self.root.after(50, self._poll_loop)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.root.update_idletasks()

    def choose_input(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_path = Path(path)
            self.in_var.set(path)
            if not self.out_var.get():
                self.out_var.set(str(self.input_path.with_suffix(".bookmarked.pdf")))

    def choose_output(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if path:
            self.output_path = Path(path)
            self.out_var.set(path)

    def _clear_tree(self) -> None:
        for i in self.tree.get_children():
            self.tree.delete(i)

    def _populate_tree(self, headings) -> None:
        self._clear_tree()
        for h in headings:
            self.tree.insert("", tk.END, values=(h.title, h.page, h.level))

    # Auto analysis removed

    def _on_generate(self) -> None:
        if not self.in_var.get():
            messagebox.showwarning("Missing", "Please choose an input PDF")
            return
        if not self.out_var.get():
            messagebox.showwarning("Missing", "Please choose an output path")
            return

        async def task():
            self._set_status("Generating…")
            # Prefer TOC from text if present
            text = self.toc_text.get("1.0", tk.END).strip()
            hs = []
            if text:
                try:
                    offset = int(self.offset_var.get() or 0)
                except ValueError:
                    offset = 0
                hs = await run_in_thread(parse_toc_lines, text, offset)
            else:
                hs = []
            await run_in_thread(generate_bookmarks, self.in_var.get(), self.out_var.get(), hs)
            self._set_status("Done")
            messagebox.showinfo("Success", f"Wrote: {self.out_var.get()}")

        asyncio.run_coroutine_threadsafe(task(), self.loop)

    def _on_parse_toc_text(self) -> None:
        text = self.toc_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty", "Please paste TOC text or URL first")
            return
        try:
            offset = int(self.offset_var.get() or 0)
        except ValueError:
            offset = 0

        async def task():
            self._set_status("Parsing TOC…")
            hs = await run_in_thread(parse_toc_lines, text, offset)
            self._populate_tree(hs)
            self._set_status(f"Parsed {len(hs)} entries")

        asyncio.run_coroutine_threadsafe(task(), self.loop)

    # URL fetch removed: manual TOC input only


def main() -> None:  # pragma: no cover
    root = tk.Tk()
    App(root)
    root.mainloop()
