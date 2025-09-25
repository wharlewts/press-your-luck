import os
import random
import tkinter as tk
from PIL import Image, ImageTk, ImageOps, ImageDraw

# iPhone resolution portrait
SCREEN_WIDTH = 1170
SCREEN_HEIGHT = 2532

# Board layout
ROWS = 5
COLS = 4

TILE_SIZE = 200  # pixels per square
BORDER = 2       # black spacing/border thickness

UPDATE_INTERVAL = 500  # milliseconds
BACKGROUND_COLORS = {
    "orange": (255, 165, 0),
    "gold": (255, 215, 0),
    "blue": (30, 144, 255),
    "purple": (138, 43, 226),
}


def make_rect_gradient(color, size=TILE_SIZE):
    """Create a rectangular gradient: dark in center -> color at edges"""
    base = Image.new("RGB", (size, size), (0, 0, 0))
    overlay = Image.new("RGB", (size, size), color)
    mask = Image.new("L", (size, size))
    pixels = mask.load()

    max_dist = size / 2

    for y in range(size):
        for x in range(size):
            # distance from center (in a square sense, not radial)
            dx = abs(x - size / 2)
            dy = abs(y - size / 2)
            dist = max(dx, dy)  # square distance
            alpha = int(255 * (dist / max_dist))  # 0 at center, 255 at edges
            pixels[x, y] = alpha

    base.paste(overlay, (0, 0), mask)
    return base


class PressYourLuckBoard:
    def __init__(self, root, image_dir):
        self.root = root
        self.image_dir = image_dir

        # Load images
        self.images = [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.lower().endswith(".webp")
        ]
        if not self.images:
            raise ValueError("No WEBP images found!")

        # Canvas with red background
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="red", highlightthickness=0)
        self.canvas.pack()

        # Preload images
        self.raw_images = [Image.open(img_path).convert("RGBA") for img_path in self.images]

        # Precompute gradient backgrounds
        self.gradients = {name: make_rect_gradient(rgb) for name, rgb in BACKGROUND_COLORS.items()}

        # Define border positions (outer loop)
        self.positions = []
        # Top row
        for c in range(4):
            self.positions.append((c, 0))
        # Right side
        for r in range(1, 5):
            self.positions.append((3, r))
        # Bottom row
        for c in range(2, -1, -1):
            self.positions.append((c, 4))
        # Left side
        for r in range(3, 0, -1):
            self.positions.append((0, r))

        self.tile_widgets = {}
        self.cursor_index = 0

        self.draw_board()
        self.update_board()

    def make_tile(self):
        """Create a tile with gradient background + random image"""
        color_name = random.choice(list(BACKGROUND_COLORS.keys()))
        bg = self.gradients[color_name].copy()

        # Pick and resize an image
        img = random.choice(self.raw_images)
        img_resized = ImageOps.contain(img, (TILE_SIZE - 20, TILE_SIZE - 20))  # padding

        # Center the image
        x = (TILE_SIZE - img_resized.width) // 2
        y = (TILE_SIZE - img_resized.height) // 2
        bg.paste(img_resized, (x, y), img_resized)

        # Add black border background
        bordered = Image.new("RGB", (TILE_SIZE + 2 * BORDER, TILE_SIZE + 2 * BORDER), (0, 0, 0))
        bordered.paste(bg, (BORDER, BORDER))

        return ImageTk.PhotoImage(bordered)

    def draw_board(self):
        """Draw initial board"""
        for r in range(5):
            for c in range(4):
                x = c * (TILE_SIZE + 2 * BORDER) + 100
                y = r * (TILE_SIZE + 2 * BORDER) + 100

                # Skip center (logo space)
                if 1 <= c <= 2 and 1 <= r <= 3:
                    continue

                tile_img = self.make_tile()
                tile_id = self.canvas.create_image(x, y, image=tile_img, anchor="nw")
                self.tile_widgets[(c, r)] = (tile_id, tile_img)

    def update_board(self):
        """Update all tiles with new random images + gradients"""
        for pos, (tile_id, _) in self.tile_widgets.items():
            new_tile_img = self.make_tile()
            self.canvas.itemconfig(tile_id, image=new_tile_img)
            self.tile_widgets[pos] = (tile_id, new_tile_img)

        # Move cursor
        self.highlight_cursor()

        # Schedule next refresh
        self.root.after(UPDATE_INTERVAL, self.update_board)

    def highlight_cursor(self):
        """Draw highlight rectangle around active tile"""
        self.canvas.delete("cursor")
        self.cursor_index = random.randrange(len(self.positions))

        c, r = self.positions[self.cursor_index]
        x = c * (TILE_SIZE + 2 * BORDER) + 100
        y = r * (TILE_SIZE + 2 * BORDER) + 100

        self.canvas.create_rectangle(
            x, y, x + TILE_SIZE + 2 * BORDER, y + TILE_SIZE + 2 * BORDER,
            outline="lime", width=8, tags="cursor"
        )

        self.cursor_index = (self.cursor_index + 1) % len(self.positions)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Press Your Luck Board")

    board = PressYourLuckBoard(root, "/mnt/c/Users/abecx/Documents/press-your-luck/tiles")  # put your WEBP files in ./tiles

    root.mainloop()

