
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageTk
from fontTools.ttLib import TTFont
import os

def browse_font_file():
    filepath = filedialog.askopenfilename(
        defaultextension=".ttf",
        filetypes=[("TTF files", "*.ttf"), ("All files", "*.*")],
        title="Select Noto Emoji TTF Font File"
    )
    font_path_entry.delete(0, tk.END)
    font_path_entry.insert(0, filepath)
    if filepath:
        load_emoji_names_from_font(filepath)

def load_emoji_names_from_font(font_path):
    try:
        font = TTFont(font_path)
        emoji_cmap = None
        for table in font['cmap'].tables:
            if table.format == 4 and (103 or 0) in table.platformID:  
                emoji_cmap = table
                break

        if emoji_cmap:
            emoji_unicodes = sorted([u for u in emoji_cmap.cmap.keys() if 0x1F000 <= u <= 0x1FFFF or 0x1F300 <= u <= 0x1F6FF or 0x1F680 <= u <= 0x1F6FF or 0x1F900 <= u <= 0x1F9FF or 0x1FA00 <= u <= 0x1FAFF]) # Basic emoji ranges
            emoji_names = [f"U+{u:04X}" for u in emoji_unicodes] 
            emoji_listbox.delete(0, tk.END)
            for name in emoji_names:
                emoji_listbox.insert(tk.END, name)
            emoji_list = list(emoji_unicodes)
            global emoji_unicode_map
            emoji_unicode_map = dict(zip(emoji_names, emoji_list))
        else:
            messagebox.showerror("Error", "No suitable Unicode cmap table found in the font for emojis.")
            emoji_listbox.delete(0, tk.END)
            global emoji_unicode_map
            emoji_unicode_map = {}

        font.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error loading or reading font file: {e}")
        emoji_listbox.delete(0, tk.END)
        global emoji_unicode_map
        emoji_unicode_map = {}

def render_glyph_to_image(font_path, unicode_codepoint, size):
    try:
        font = TTFont(font_path)
        glyphset = font.getGlyphSet()
        cmap = font.getBestCmap()

        if unicode_codepoint in cmap:
            glyph_name = cmap[unicode_codepoint]
            if glyph_name in glyphset:
                glyph = glyphset[glyph_name]
                bounds = glyph.getBounds()
                width = int(bounds.xMax - bounds.xMin)
                height = int(bounds.yMax - bounds.yMin)

                if width > 0 and height > 0:
                    img_size = size
                    image = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(image)


                    messagebox.showerror("Limitation", "Direct rendering from TTF with color information is complex and not fully implemented in this basic example. The output will likely be a monochrome outline or not render correctly.")
                    return None

                else:
                    messagebox.showerror("Error", f"Glyph '{glyph_name}' has zero dimensions.")
                    return None
            else:
                messagebox.showerror("Error", f"Glyph '{glyph_name}' not found in font.")
                return None
        else:
            messagebox.showerror("Error", f"Unicode codepoint {unicode_codepoint:04X} not found in font cmap.")
            return None

        font.close()
        return image

    except Exception as e:
        messagebox.showerror("Error", f"Error rendering glyph: {e}")
        return None

def save_image(image, filepath, format):
    if image:
        try:
            image.save(filepath, format=format)
            messagebox.showinfo("Success", f"Emoji saved to '{filepath}'")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {e}")

def extract_emoji():
    font_path = font_path_entry.get()
    selected_emoji_name = emoji_listbox.get(emoji_listbox.curselection()) if emoji_listbox.curselection() else None
    size = int(size_entry.get()) if size_entry.get().isdigit() else 128
    format = format_combobox.get().split(" ")[0].upper()

    if not font_path:
        messagebox.showerror("Error", "Please select a Noto Emoji TTF font file.")
        return

    if not selected_emoji_name:
        messagebox.showerror("Error", "Please select an emoji.")
        return

    unicode_codepoint = emoji_unicode_map.get(selected_emoji_name)
    if unicode_codepoint is None:
        messagebox.showerror("Error", f"Unicode for '{selected_emoji_name}' not found.")
        return

    output_filename = f"{selected_emoji_name.replace('+', '')}_{size}.{format.lower()}"
    output_filepath = filedialog.asksaveasfilename(
        defaultextension=f".{format.lower()}",
        initialfile=output_filename,
        title="Save Emoji As"
    )

    if output_filepath:
        image = render_glyph_to_image(font_path, unicode_codepoint, size)
        if image:
            save_image(image, output_filepath, format)

# GUI Setup
root = tk.Tk()
root.title("Noto Emoji Extractor (from TTF - Limited)")

font_path_label = tk.Label(root, text="Noto Emoji TTF Font:")
font_path_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

font_path_entry = tk.Entry(root, width=50)
font_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

browse_button = tk.Button(root, text="Browse", command=browse_font_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

emoji_label = tk.Label(root, text="Select Emoji:")
emoji_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

emoji_listbox = tk.Listbox(root, height=10, width=40)
emoji_listbox.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

size_label = tk.Label(root, text="Size:")
size_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

size_entry = tk.Entry(root, width=10)
size_entry.insert(0, "128")
size_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
tk.Label(root, text="pixels").grid(row=3, column=1, padx=80, pady=5, sticky="w")

format_label = tk.Label(root, text="Format:")
format_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

formats = ["PNG", "GIF", "JPG (Not Recommended)"]
format_combobox = ttk.Combobox(root, values=formats, state="readonly")
format_combobox.set("PNG")
format_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

extract_button = tk.Button(root, text="Extract Emoji", command=extract_emoji)
extract_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

emoji_unicode_map = {} 

root.mainloop()
