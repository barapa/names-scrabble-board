#!/usr/bin/env python3
"""
Render crossword puzzles as Scrabble-style tiles in SVG format.
Creates high-quality, print-ready graphics suitable for t-shirts.
"""

import os
import svgwrite
from datetime import datetime
from pathlib import Path
import base64
from typing import List, Tuple, Dict

# Import the crossword generator
from scrabble_crossword import ScrabbleCrossword

# Scrabble letter scores
SCRABBLE_SCORES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8,
    'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1,
    'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
}

class ScrabbleTileRenderer:
    def __init__(self, tile_size=100):
        self.tile_size = tile_size
        self.spacing = int(0.05 * tile_size)  # 5% spacing between tiles
        self.letter_size = int(0.6 * tile_size)
        self.score_size = int(0.25 * tile_size)
        self.corner_radius = int(0.08 * tile_size)
        
    def create_svg_defs(self, dwg):
        """Create SVG definitions for gradients."""
        defs = dwg.defs
        
        # Dark modern gradient for tile background
        grad = dwg.radialGradient(id="darkTile", center=(0.3, 0.3))
        grad.add_stop_color(0, "#4a4a4a")  # Lighter grey at center
        grad.add_stop_color(0.8, "#2d2d2d") # Medium grey
        grad.add_stop_color(1, "#1a1a1a")   # Dark grey at edges
        defs.add(grad)
        
        return defs
    
    def draw_tile(self, dwg, x, y, letter):
        """Draw a single Scrabble tile at the given position."""
        tile_x = x * (self.tile_size + self.spacing)
        tile_y = y * (self.tile_size + self.spacing)
        
        # Create tile group
        tile_group = dwg.g(transform=f"translate({tile_x},{tile_y})")
        
        # Tile background with rounded corners
        tile_rect = dwg.rect(
            insert=(0, 0), 
            size=(self.tile_size, self.tile_size),
            rx=self.corner_radius, 
            ry=self.corner_radius,
            fill="url(#darkTile)",
            stroke="#666666",
            stroke_width=2
        )
        tile_group.add(tile_rect)
        
        # Main letter (centered)
        letter_text = dwg.text(
            letter.upper(),
            insert=(self.tile_size/2, self.tile_size*0.68),  # Optical centering
            text_anchor="middle",
            font_size=f"{self.letter_size}px",
            font_family="Arial, sans-serif",
            font_weight="bold",
            fill="#f5f5f5"  # Light grey/white text
        )
        tile_group.add(letter_text)
        
        # Score (bottom-right corner)
        score = SCRABBLE_SCORES.get(letter.upper(), 0)
        score_text = dwg.text(
            str(score),
            insert=(self.tile_size*0.92, self.tile_size*0.9),
            text_anchor="end",
            font_size=f"{self.score_size}px",
            font_family="Arial, sans-serif",
            font_weight="normal",
            fill="#cccccc"  # Slightly dimmer for score
        )
        tile_group.add(score_text)
        
        return tile_group
    
    def render_crossword(self, grid, word_positions, filename="scrabble_crossword.svg"):
        """Render the complete crossword as Scrabble tiles."""
        if not grid:
            print("No grid to render!")
            return None
            
        # Find grid bounds
        occupied_cells = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] != ' ']
        if not occupied_cells:
            print("No occupied cells found!")
            return None
            
        min_row = min(r for r, c in occupied_cells)
        max_row = max(r for r, c in occupied_cells)
        min_col = min(c for r, c in occupied_cells)
        max_col = max(c for r, c in occupied_cells)
        
        # Calculate SVG dimensions (accounting for spacing)
        grid_width = (max_col - min_col + 1)
        grid_height = (max_row - min_row + 1)
        svg_width = grid_width * (self.tile_size + self.spacing) - self.spacing
        svg_height = grid_height * (self.tile_size + self.spacing) - self.spacing
        
        # Create SVG drawing
        dwg = svgwrite.Drawing(filename, size=(svg_width, svg_height), profile='full')
        dwg.viewbox(0, 0, svg_width, svg_height)
        
        # Add definitions
        self.create_svg_defs(dwg)
        
        # Draw tiles for occupied cells
        for row_idx in range(len(grid)):
            for col_idx in range(len(grid[0])):
                letter = grid[row_idx][col_idx]
                if letter != ' ':
                    # Adjust coordinates relative to the bounding box
                    tile_x = col_idx - min_col
                    tile_y = row_idx - min_row
                    tile = self.draw_tile(dwg, tile_x, tile_y, letter)
                    dwg.add(tile)
        
        # Save the SVG
        dwg.save()
        print(f"Rendered Scrabble tiles to: {filename}")
        return filename

def create_scrabble_outputs():
    """Generate crossword and create multiple Scrabble tile renderings."""
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output") / f"scrabble_tiles_{timestamp}" 
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating Scrabble tile outputs in: {output_dir}")
    
    # Read names from file
    names_file = Path("data/names.txt")
    names = []
    if names_file.exists():
        with open(names_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract just the name part, handle numbered format
                    if ':' in line:
                        name = line.split(':', 1)[1].strip()
                    else:
                        name = line
                    if name:
                        names.append(name.upper())
    else:
        # Fallback names if file doesn't exist
        names = [
            "ALICE", "BOB", "CHARLIE", "DIANA", "EVE", "FRANK", "GRACE", "HENRY",
            "IVY", "JACK", "KATE", "LIAM", "MIA", "NOAH", "OLIVIA", "PAUL",
            "QUINN", "RUBY", "SAM"
        ]
    
    print(f"Using {len(names)} names: {', '.join(names)}")
    
    crossword = ScrabbleCrossword(names)
    success = crossword.generate_puzzle()
    
    if not success:
        print("Failed to generate crossword!")
        return
        
    # Extract grid and word positions from the crossword object
    grid = crossword.grid
    word_positions = {word: (row, col, direction) for word, row, col, direction in crossword.placed_words}
        
    # Create different sized renderings
    sizes = [
        (80, "small"),
        (100, "medium"), 
        (120, "large"),
        (150, "xlarge")
    ]
    
    files_created = []
    
    for tile_size, size_name in sizes:
        renderer = ScrabbleTileRenderer(tile_size=tile_size)
        filename = output_dir / f"scrabble_crossword_{size_name}.svg"
        result = renderer.render_crossword(grid, word_positions, str(filename))
        if result:
            files_created.append(result)
    
    # Save word list and layout info
    layout_file = output_dir / "word_layout.txt"
    with open(layout_file, 'w') as f:
        f.write("SCRABBLE TILE CROSSWORD LAYOUT\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("WORDS PLACED:\n")
        for word, (row, col, direction) in word_positions.items():
            f.write(f"  {word}: Row {row}, Col {col}, {direction}\n")
        
        f.write("\nGRID LAYOUT:\n")
        for row in grid:
            f.write("  " + " ".join(cell if cell != ' ' else '·' for cell in row) + "\n")
            
        f.write(f"\nFILES CREATED:\n")
        for file in files_created:
            f.write(f"  {Path(file).name}\n")
    
    print(f"\nCompleted! Files saved to: {output_dir}")
    print(f"Layout info saved to: {layout_file}")
    
    return files_created

if __name__ == "__main__":
    create_scrabble_outputs()
