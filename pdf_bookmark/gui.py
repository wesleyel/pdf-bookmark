from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Optional

from .core import analyze_pdf_headings, generate_bookmarks


# Run blocking CPU/IO bound function in thread to keep UI responsive
async def run_in_thread(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Bookmark")
        self.root.geometry("700x420")

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

        # Controls
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill=tk.X, pady=10)
        ttk.Button(ctrl, text="Analyze", command=self._on_analyze).pack(side=tk.LEFT)
        ttk.Button(ctrl, text="Generate", command=self._on_generate).pack(side=tk.LEFT, padx=8)

        # Tree view for headings
        self.tree = ttk.Treeview(frm, columns=("page", "level"), show="headings")
        self.tree.heading("page", text="Page")
        self.tree.heading("level", text="Level")
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
            self.tree.insert("", tk.END, values=(h.page, h.level))

    def _on_analyze(self) -> None:
        if not self.in_var.get():
            messagebox.showwarning("Missing", "Please choose an input PDF")
            return

        async def task():
            self._set_status("Analyzing…")
            hs = await run_in_thread(analyze_pdf_headings, self.in_var.get())
            self._populate_tree(hs)
            self._set_status(f"Found {len(hs)} headings")

        asyncio.run_coroutine_threadsafe(task(), self.loop)

    def _on_generate(self) -> None:
        if not self.in_var.get():
            messagebox.showwarning("Missing", "Please choose an input PDF")
            return
        if not self.out_var.get():
            messagebox.showwarning("Missing", "Please choose an output path")
            return

        async def task():
            self._set_status("Generating…")
            hs = await run_in_thread(analyze_pdf_headings, self.in_var.get())
            await run_in_thread(generate_bookmarks, self.in_var.get(), self.out_var.get(), hs)
            self._set_status("Done")
            messagebox.showinfo("Success", f"Wrote: {self.out_var.get()}")

        asyncio.run_coroutine_threadsafe(task(), self.loop)


def main() -> None:  # pragma: no cover
    root = tk.Tk()
    App(root)
    root.mainloop()
