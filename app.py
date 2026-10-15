import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# --- Configuration ---
DIR_UNSORTED = "unsorted_images"
DIR_POSITIVE = "positive_images"
DIR_NEGATIVE = "negative_images"
DIR_UNCERTAIN = "uncertain_images"

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
DISPLAY_MARGIN_CM = 2


def ensure_directories():
    for directory in [DIR_UNSORTED, DIR_POSITIVE, DIR_NEGATIVE, DIR_UNCERTAIN]:
        os.makedirs(directory, exist_ok=True)

class ImageSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Sorter")
        self.root.geometry("850x720")

        ensure_directories()

        self.current_image_path = None
        self.photo_ref = None  # Prevent garbage collection of Tkinter image
        self.original_image = None
        self.base_image_size = None
        self.zoom_factor = 1.0

        # UI Setup
        self._build_ui()

        # Keyboard bindings
        self.root.bind("<Right>", lambda event: self.sort_image(DIR_POSITIVE))
        self.root.bind("<Left>", lambda event: self.sort_image(DIR_NEGATIVE))
        self.root.bind("<Down>", lambda event: self.sort_image(DIR_UNCERTAIN))
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        # Load first image
        self.load_next_image()

    def _build_ui(self):
        # Folder counters header
        self.stats_label = tk.Label(self.root, font=("Helvetica", 13, "bold"), pady=8)
        self.stats_label.pack()

        # Image viewport
        self.image_label = tk.Label(self.root)
        self.image_label.pack(expand=True, fill="both", padx=self._get_margin_pixels(), pady=self._get_margin_pixels())
        self.root.bind("<MouseWheel>", self.zoom_image)
        self.root.bind("<Button-4>", self.zoom_image)
        self.root.bind("<Button-5>", self.zoom_image)

        # Instructions / Shortcut legend
        help_text = "Controls: [Left Arrow] Move to Negative  |  [Right Arrow] Move to Positive  |  [Down Arrow] Move to Uncertain  |  [Esc] Quit"
        self.help_label = tk.Label(self.root, text=help_text, font=("Helvetica", 10), fg="#555", pady=8)
        self.help_label.pack()

    def _get_margin_pixels(self):
        if not self.root.winfo_exists():
            return 0
        self.root.update_idletasks()
        pixels_per_cm = self.root.winfo_fpixels("1c")
        return max(10, int(DISPLAY_MARGIN_CM * pixels_per_cm))

    def _get_display_size(self):
        self.root.update_idletasks()
        margin = self._get_margin_pixels()
        width = max(1, self.root.winfo_width() - (margin * 2))
        height = max(1, self.root.winfo_height() - (margin * 2))
        return (width, height)

    def _get_image_list(self, folder):
        return [
            f for f in os.listdir(folder)
            if os.path.splitext(f.lower())[1] in SUPPORTED_EXTS
        ]

    def update_counts(self):
        unsorted_count = len(self._get_image_list(DIR_UNSORTED))
        pos_count = len(self._get_image_list(DIR_POSITIVE))
        neg_count = len(self._get_image_list(DIR_NEGATIVE))
        uncertain_count = len(self._get_image_list(DIR_UNCERTAIN))

        self.stats_label.config(
            text=(
                f"Unsorted: {unsorted_count}   |   Positive: {pos_count}   |   "
                f"Negative: {neg_count}   |   Uncertain: {uncertain_count}"
            )
        )

    def load_next_image(self):
        self.update_counts()
        images = sorted(self._get_image_list(DIR_UNSORTED))

        if not images:
            self.image_label.config(image="", text="All images sorted!", font=("Helvetica", 18))
            self.current_image_path = None
            self.original_image = None
            self.base_image_size = None
            if messagebox.askyesno("Complete", "No unsorted images remain.\nWould you like to close the application?"):
                self.root.destroy()
            return

        self.current_image_path = os.path.join(DIR_UNSORTED, images[0])
        self.original_image = None
        self.base_image_size = None
        self.zoom_factor = 1.0

        try:
            with Image.open(self.current_image_path) as img:
                self.original_image = img.copy()
            display_size = self._get_display_size()
            fit_image = self.original_image.copy()
            fit_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            self.base_image_size = fit_image.size
            self.zoom_factor = 1.0

            self.photo_ref = ImageTk.PhotoImage(fit_image)
            self.image_label.config(image=self.photo_ref, text="")
        except Exception as e:
            print(f"Error loading {self.current_image_path}: {e}")
            self.image_label.config(image="", text=f"Failed to load image:\n{images[0]}")

    def zoom_image(self, event):
        if self.original_image is None or self.base_image_size is None:
            return "break"

        if getattr(event, "num", None) == 4:
            direction = 1
        elif getattr(event, "num", None) == 5:
            direction = -1
        else:
            direction = 1 if event.delta > 0 else -1

        self.zoom_factor = min(8.0, max(0.1, self.zoom_factor * (1.1 ** direction)))
        width = max(1, round(self.base_image_size[0] * self.zoom_factor))
        height = max(1, round(self.base_image_size[1] * self.zoom_factor))
        zoomed_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo_ref = ImageTk.PhotoImage(zoomed_image)
        self.image_label.config(image=self.photo_ref, text="")
        return "break"

    def sort_image(self, target_folder):
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            return

        filename = os.path.basename(self.current_image_path)
        dest_path = os.path.join(target_folder, filename)

        # Handle filename collisions in target folder
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
            counter += 1

        shutil.move(self.current_image_path, dest_path)
        self.load_next_image()

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))
    window = tk.Tk()
    app = ImageSorterApp(window)
    window.mainloop()