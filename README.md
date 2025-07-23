# Scrabble Crossword Generator

A Python tool that generates beautiful Scrabble-style crossword puzzles from a list of names and renders them as high-quality SVG tiles perfect for t-shirt printing.

## Features

- **Smart word placement** - Uses backtracking algorithm to fit all names into a connected crossword
- **Authentic Scrabble tiles** - Realistic letter scoring and modern dark tile design
- **Multiple sizes** - Generates 4 different tile sizes (small, medium, large, xlarge)
- **Print-ready output** - High-quality SVG files perfect for professional printing
- **Customizable spacing** - Clean gaps between tiles for better visual appeal
- **Modern dark design** - Sleek blackish-grey tiles with white text

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup

1. Clone or download this project
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

### 1. Prepare your names

Edit the `data/names.txt` file with your names (one per line):
```
David
Debbie
Beth
Steve
Sam
...
```

### 2. Generate the crossword

Run the generator:
```bash
uv run render_scrabble_tiles.py
```

### 3. Find your output

The script creates a timestamped directory in `output/` containing:
- `scrabble_crossword_small.svg` (80px tiles)
- `scrabble_crossword_medium.svg` (100px tiles) 
- `scrabble_crossword_large.svg` (120px tiles)
- `scrabble_crossword_xlarge.svg` (150px tiles)
- `word_layout.txt` (placement details and grid layout)

## Example Output

```
output/scrabble_tiles_20250723_140957/
├── scrabble_crossword_small.svg
├── scrabble_crossword_medium.svg  
├── scrabble_crossword_large.svg
├── scrabble_crossword_xlarge.svg
└── word_layout.txt
```

## File Structure

```
crossword/
├── data/
│   └── names.txt              # Input names (edit this!)
├── output/                    # Generated SVG files
├── scrabble_crossword.py      # Core crossword generation logic
├── render_scrabble_tiles.py   # SVG renderer (run this!)
├── pyproject.toml            # Dependencies
└── README.md                 # This file
```

## Customization

### Tile Design
Edit `render_scrabble_tiles.py` to customize:
- Colors (search for `#4a4a4a`, `#f5f5f5` etc.)
- Tile spacing (change `self.spacing`)
- Fonts (change `font_family`)
- Tile sizes (modify the `sizes` array)

### Algorithm Settings
Edit `scrabble_crossword.py` to adjust:
- Grid size (default 20x20)
- Timeout (default 30 seconds)
- Word placement strategy

## Troubleshooting

**"Could not place all words"**: Some name combinations are impossible to fit. Try:
- Reducing the number of names
- Using names with more common letters (vowels, common consonants)

**"No module named 'svgwrite'"**: Run `uv sync` to install dependencies

## For T-Shirt Printing

The SVG files are vector-based and scale perfectly. For best results:
- Use the `xlarge` version for large prints
- Convert to PDF if your printer requires it: `inkscape file.svg --export-filename=file.pdf`
- For raster formats: `inkscape file.svg --export-filename=file.png --export-dpi=300`

## License

This project is for personal/educational use. Scrabble is a trademark of Hasbro/Mattel.
