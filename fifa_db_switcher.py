import os
import shutil
import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog

WINDOW_WIDTH = 280
WINDOW_HEIGHT = 90
ROW_WIDTH = 259
ROW_HEIGHT = 22
CREDIT_RIGHT_PADDING = 6
CREDIT_BOTTOM_PADDING = 1


def get_default_fifa_root() -> str:
    default_path = r"C:\Program Files (x86)\EA SPORTS\FIFA 07"
    return default_path if os.path.isdir(default_path) else str(Path.home())


def get_app_base_dirs() -> list[Path]:
    dirs = []

    # Normal Python run: script folder
    if "__file__" in globals():
        dirs.append(Path(__file__).resolve().parent)

    # PyInstaller onefile: temporary extraction folder
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        dirs.append(Path(meipass))

    # PyInstaller executable folder
    if getattr(sys, "frozen", False):
        dirs.append(Path(sys.executable).resolve().parent)

    # Keep unique order
    unique_dirs = []
    for item in dirs:
        if item not in unique_dirs:
            unique_dirs.append(item)
    return unique_dirs


def find_source_db(file_name: str) -> Path | None:
    for base_dir in get_app_base_dirs():
        candidates = [base_dir / "data" / file_name, base_dir / file_name]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return None


def find_image_asset(file_name: str) -> Path | None:
    for base_dir in get_app_base_dirs():
        candidates = [base_dir / "assets" / file_name, base_dir / file_name]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return None


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mart Majör Yaması")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.selected_folder = tk.StringVar(value=get_default_fifa_root())
        self.status_var = tk.StringVar(value="")
        self.path_font = tkfont.Font(family="Segoe UI", size=8)
        self.base_window_height = WINDOW_HEIGHT
        self.app_icon = None
        self.install_img = None
        self.restore_img = None
        self.browse_img = None
        self.textholder_img = None
        self.path_canvas = None
        self.path_text_id = None
        self.status_y = 0

        self._set_window_icon()
        self._build_ui()
        self.selected_folder.trace_add("write", self._on_path_changed)
        self._update_path_text()

    def _set_window_icon(self):
        icon_path = find_image_asset("app_icon.png")
        if icon_path is None:
            return
        try:
            self.app_icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.app_icon)
        except Exception:
            # Keep app running even if icon format is not supported in current environment.
            self.app_icon = None

    def _build_ui(self):
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.pack(fill="both", expand=True)

        self.credit_label = tk.Label(
            container,
            text="by kaufman",
            bg="#1e1e1e",
            fg="#808080",
            font=("Segoe UI", 7),
        )
        self.credit_label.place(
            x=WINDOW_WIDTH - CREDIT_RIGHT_PADDING,
            y=WINDOW_HEIGHT - CREDIT_BOTTOM_PADDING,
            anchor="se",
        )

        self.status_label = tk.Label(
            container,
            textvariable=self.status_var,
            bg="#1e1e1e",
            fg="#a7f3d0",
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=ROW_WIDTH,
        )

        browse_path = find_image_asset("button_browse.png")
        holder_path = find_image_asset("path_holder.png")
        if browse_path is None or holder_path is None:
            self.set_status("Arayüz dosyaları eksik (button_browse.png / path_holder.png).", is_error=True)
            return

        self.browse_img = tk.PhotoImage(file=str(browse_path))
        self.textholder_img = tk.PhotoImage(file=str(holder_path))

        holder_w = self.textholder_img.width()
        holder_h = self.textholder_img.height()
        browse_w = self.browse_img.width()
        browse_h = self.browse_img.height()
        top_h = max(holder_h, browse_h)
        top_gap = ROW_WIDTH - holder_w - browse_w
        if top_gap < 0:
            self.set_status("Arayüz görselleri boyutu uyumsuz.", is_error=True)
            return

        # Top row occupies exactly 259px in width.
        path_frame = tk.Frame(container, bg="#1e1e1e", width=ROW_WIDTH, height=top_h)
        path_frame.place(x=12, y=8, width=ROW_WIDTH, height=top_h)

        self.path_canvas = tk.Canvas(
            path_frame,
            width=holder_w,
            height=holder_h,
            highlightthickness=0,
            bd=0,
            bg="#1e1e1e",
        )
        self.path_canvas.place(x=0, y=(top_h - holder_h) // 2, width=holder_w, height=holder_h)
        self.path_canvas.create_image(0, 0, image=self.textholder_img, anchor="nw")
        self.path_text_id = self.path_canvas.create_text(
            8,
            holder_h // 2,
            text="",
            fill="#eaeaea",
            font=self.path_font,
            anchor="w",
        )

        browse_btn = tk.Button(
            path_frame,
            image=self.browse_img,
            command=self.choose_folder,
            bg="#313131",
            activebackground="#3b3b3b",
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        browse_btn.place(x=holder_w + top_gap, y=((top_h - browse_h) // 2) + 1, width=browse_w, height=browse_h)

        # Bottom row occupies exactly 259px in width.
        buttons_frame = tk.Frame(container, bg="#1e1e1e", width=ROW_WIDTH)
        buttons_y = 8 + top_h + 6
        buttons_frame.place(x=12, y=buttons_y, width=ROW_WIDTH)

        install_path = find_image_asset("button_install.png")
        restore_path = find_image_asset("button_restore.png")
        if install_path is None or restore_path is None:
            self.set_status("Arayüz dosyaları eksik (button_install.png / button_restore.png).", is_error=True)
            return

        self.install_img = tk.PhotoImage(file=str(install_path))
        self.restore_img = tk.PhotoImage(file=str(restore_path))

        left_width = self.install_img.width()
        right_width = self.restore_img.width()
        button_row_height = max(self.install_img.height(), self.restore_img.height())
        gap = max(0, ROW_WIDTH - left_width - right_width)
        # Keep both buttons within 259px total width.
        if left_width + right_width > ROW_WIDTH:
            self.set_status("Arayüz görselleri boyutu uyumsuz.", is_error=True)
            return

        buttons_frame.place_configure(height=button_row_height)

        install_btn = tk.Button(
            buttons_frame,
            image=self.install_img,
            command=lambda: self.copy_db("fifa_patched.db"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            bg="#1e1e1e",
            activebackground="#1e1e1e",
            cursor="hand2",
        )
        install_btn.place(x=0, y=0, width=left_width, height=self.install_img.height())

        restore_btn = tk.Button(
            buttons_frame,
            image=self.restore_img,
            command=lambda: self.copy_db("fifa.db"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            bg="#1e1e1e",
            activebackground="#1e1e1e",
            cursor="hand2",
        )
        restore_btn.place(x=left_width + gap, y=0, width=right_width, height=self.restore_img.height())

        status_y = buttons_y + button_row_height + 4
        self.status_y = status_y
        self.status_label.place(x=12, y=status_y, width=ROW_WIDTH, height=0)
        self._update_status_layout()


    def set_status(self, message: str, is_error: bool = False):
        self.status_var.set(message)
        color = "#C73939" if is_error else "#40c533"
        self.status_label.configure(fg=color)
        self._update_status_layout()

    def _update_status_layout(self):
        message = self.status_var.get().strip()
        if not message:
            self.status_label.place_configure(height=0)
            self.root.geometry(f"{WINDOW_WIDTH}x{self.base_window_height}")
            self.credit_label.place_configure(
                x=WINDOW_WIDTH - CREDIT_RIGHT_PADDING,
                y=self.base_window_height - CREDIT_BOTTOM_PADDING,
            )
            return

        # Let Tk calculate required wrapped label height, then resize window.
        self.status_label.place_configure(height=1)
        self.root.update_idletasks()
        needed_label_height = max(18, self.status_label.winfo_reqheight() + 2)
        self.status_label.place_configure(height=needed_label_height)

        # Keep credit text below status messages when window expands.
        needed_window_height = max(self.base_window_height, self.status_y + needed_label_height + 18)
        self.root.geometry(f"{WINDOW_WIDTH}x{needed_window_height}")
        self.credit_label.place_configure(
            x=WINDOW_WIDTH - CREDIT_RIGHT_PADDING,
            y=needed_window_height - CREDIT_BOTTOM_PADDING,
        )

    def _on_path_changed(self, *_args):
        self._update_path_text()

    def _truncate_text_to_width(self, text: str, max_width: int) -> str:
        if self.path_font.measure(text) <= max_width:
            return text
        ellipsis = "..."
        keep = text
        while keep and self.path_font.measure(ellipsis + keep) > max_width:
            keep = keep[1:]
        return ellipsis + keep

    def _update_path_text(self):
        if self.path_canvas is None or self.path_text_id is None or self.textholder_img is None:
            return
        max_text_width = max(20, self.textholder_img.width() - 14)
        display_text = self._truncate_text_to_width(self.selected_folder.get(), max_text_width)
        self.path_canvas.itemconfigure(self.path_text_id, text=display_text)

    def choose_folder(self):
        initial_dir = self.selected_folder.get().strip() or get_default_fifa_root()
        chosen = filedialog.askdirectory(parent=self.root, initialdir=initial_dir)
        if chosen:
            self.selected_folder.set(chosen)
            self.set_status("Klasör seçildi.", is_error=False)

    def copy_db(self, file_name: str):
        source = find_source_db(file_name)
        if source is None:
            self.set_status("Gerekli yama dosyaları bulunamadı.", is_error=True)
            return

        selected = self.selected_folder.get().strip()
        if not selected or not os.path.isdir(selected):
            self.set_status("Geçerli bir FIFA 07 klasörü seçin.", is_error=True)
            return

        destination_dir = Path(selected) / "data" / "cmn"
        if not destination_dir.exists():
            self.set_status("Seçilen klasörde data\\cmn bulunamadı.", is_error=True)
            return

        destination_file = destination_dir / "fifa.db"

        try:
            shutil.copy2(source, destination_file)
            if file_name == "fifa_patched.db":
                self.set_status("Yama başarıyla kuruldu.", is_error=False)
            else:
                self.set_status("Oyununuz orijinal haline geri getirildi.", is_error=False)
        except PermissionError:
            self.set_status("Yazma izni yok. Aracı yönetici olarak çalıştırın.", is_error=True)
        except FileNotFoundError:
            self.set_status("Seçilen FIFA klasöründe gerekli dosyalar bulunamadı.", is_error=True)
        except Exception as exc:
            _ = exc
            self.set_status("Kopyalama sırasında beklenmeyen bir hata oluştu.", is_error=True)


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
