#!/usr/bin/env python3
# /// script
# description = "Generate Scrabble-style crossword layouts where adjacent letters form valid words"
# dependencies = []
# ///

import random
import time
from typing import List, Tuple, Optional, Set


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.all_words = set()
    
    def insert(self, word: str):
        """Insert a word into the trie."""
        word = word.upper()
        self.all_words.add(word)
        
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def contains(self, word: str) -> bool:
        """Check if a word exists in the trie."""
        return word.upper() in self.all_words


class ScrabbleCrossword:
    def __init__(self, word_list: List[str], grid_size: int = 20):
        self.grid_size = grid_size
        self.grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        self.placed_words = []
        self.start_time = None
        self.timeout = 30  # 30 second timeout
        
        # Build dictionary with the names
        self.trie = Trie()
        for word in word_list:
            self.trie.insert(word)
        
        # Sort words by length (longest first for better anchoring)  
        self.words = sorted(word_list, key=len, reverse=True)
        # Add controlled randomization
        self._shuffle_same_length_groups()
        
    def _shuffle_same_length_groups(self):
        """Shuffle words within same length groups for variation."""
        from itertools import groupby
        grouped = []
        for length, group in groupby(self.words, key=len):
            group_list = list(group)
            random.shuffle(group_list)
            grouped.extend(group_list)
        self.words = grouped
        
    def clear_grid(self):
        """Reset the grid to empty state."""
        self.grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.placed_words = []

    def build_perpendicular_word(self, row: int, col: int, main_direction: str) -> str:
        """Build the perpendicular word that would exist at this position."""
        letters = []
        
        if main_direction == 'across':
            # Check vertically (up and down)
            # Go up first
            r = row - 1
            while r >= 0 and self.grid[r][col] != ' ':
                letters.insert(0, self.grid[r][col])
                r -= 1
            
            # Add current position (will be filled)
            letters.append('?')  # Placeholder
            
            # Go down
            r = row + 1
            while r < self.grid_size and self.grid[r][col] != ' ':
                letters.append(self.grid[r][col])
                r += 1
                
        else:  # down
            # Check horizontally (left and right)
            # Go left first
            c = col - 1
            while c >= 0 and self.grid[row][c] != ' ':
                letters.insert(0, self.grid[row][c])
                c -= 1
            
            # Add current position (will be filled)
            letters.append('?')  # Placeholder
            
            # Go right
            c = col + 1
            while c < self.grid_size and self.grid[row][c] != ' ':
                letters.append(self.grid[row][c])
                c += 1
        
        return ''.join(letters)

    def can_place_word_scrabble(self, word: str, row: int, col: int, direction: str) -> bool:
        """Check if word can be placed using Scrabble rules."""
        word = word.upper()
        
        # Check bounds
        if direction == 'across':
            if col + len(word) > self.grid_size:
                return False
        else:  # down
            if row + len(word) > self.grid_size:
                return False
        
        # Check each letter position
        for i, char in enumerate(word):
            if direction == 'across':
                curr_row, curr_col = row, col + i
            else:
                curr_row, curr_col = row + i, col
            
            # Check if position conflicts
            current_char = self.grid[curr_row][curr_col]
            if current_char != ' ' and current_char != char:
                return False
            
            # If placing a new letter, check perpendicular word validity
            if current_char == ' ':
                perp_word = self.build_perpendicular_word(curr_row, curr_col, direction)
                # Replace placeholder with the actual character
                perp_word = perp_word.replace('?', char)
                
                # If perpendicular word has length > 1, it must be valid
                if len(perp_word) > 1 and not self.trie.contains(perp_word):
                    return False
        
        # Check word boundaries (must be isolated)
        if direction == 'across':
            # Check left boundary
            if col > 0 and self.grid[row][col - 1] != ' ':
                return False
            # Check right boundary
            if col + len(word) < self.grid_size and self.grid[row][col + len(word)] != ' ':
                return False
        else:  # down
            # Check top boundary
            if row > 0 and self.grid[row - 1][col] != ' ':
                return False
            # Check bottom boundary
            if row + len(word) < self.grid_size and self.grid[row + len(word)][col] != ' ':
                return False
        
        return True

    def place_word(self, word: str, row: int, col: int, direction: str):
        """Place a word on the grid."""
        word = word.upper()
        
        if direction == 'across':
            for i, char in enumerate(word):
                self.grid[row][col + i] = char
        else:  # down
            for i, char in enumerate(word):
                self.grid[row + i][col] = char
        
        self.placed_words.append((word, row, col, direction))

    def has_connection_to_existing(self, word: str, row: int, col: int, direction: str) -> bool:
        """Check if placing this word would connect to existing words orthogonally."""
        if len(self.placed_words) == 0:
            return True  # First word is always okay
        
        word = word.upper()
        
        # Check if any letter of this word would intersect or be orthogonally adjacent to existing letters
        for i in range(len(word)):
            if direction == 'across':
                curr_row, curr_col = row, col + i
            else:
                curr_row, curr_col = row + i, col
            
            # Check if this position already has the same letter (intersection)
            if self.grid[curr_row][curr_col] == word[i]:
                return True
            
            # Check only orthogonal adjacency (no diagonals!)
            orthogonal_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
            for dr, dc in orthogonal_directions:
                nr, nc = curr_row + dr, curr_col + dc
                if (0 <= nr < self.grid_size and 0 <= nc < self.grid_size and 
                    self.grid[nr][nc] != ' '):
                    return True
        
        return False

    def find_best_placement(self, word: str) -> Optional[Tuple[int, int, str]]:
        """Find the best placement for a word that connects to existing words."""
        word = word.upper()
        connected_placements = []
        
        # Try all positions and directions
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                for direction in ['across', 'down']:
                    if (self.can_place_word_scrabble(word, row, col, direction) and
                        self.has_connection_to_existing(word, row, col, direction)):
                        
                        # Calculate score based on intersections
                        intersections = 0
                        if direction == 'across':
                            for i in range(len(word)):
                                if self.grid[row][col + i] == word[i]:
                                    intersections += 1
                        else:
                            for i in range(len(word)):
                                if self.grid[row + i][col] == word[i]:
                                    intersections += 1
                        
                        # Calculate distance to center for tie-breaking
                        center_row, center_col = self.grid_size // 2, self.grid_size // 2
                        if direction == 'across':
                            word_center_row, word_center_col = row, col + len(word) // 2
                        else:
                            word_center_row, word_center_col = row + len(word) // 2, col
                        
                        distance_to_center = abs(word_center_row - center_row) + abs(word_center_col - center_col)
                        
                        connected_placements.append((row, col, direction, intersections, -distance_to_center))
        
        if not connected_placements:
            return None
        
        # Sort by intersections (more is better), then by distance to center (closer is better)
        connected_placements.sort(key=lambda x: (-x[3], x[4], random.random()))
        return connected_placements[0][:3]

    def generate_puzzle(self) -> bool:
        """Generate a Scrabble-style crossword with backtracking."""
        self.start_time = time.time()
        print(f"Starting backtracking with {len(self.words)} words...")
        result = self._backtrack_solve(0)
        elapsed = time.time() - self.start_time
        print(f"Backtracking completed in {elapsed:.2f} seconds")
        return result
    
    def _backtrack_solve(self, word_index: int) -> bool:
        """Recursive backtracking to place all words."""
        # Check timeout
        if time.time() - self.start_time > self.timeout:
            print(f"⏰ Timeout after {self.timeout}s - stopping backtrack")
            return False
            
        if word_index >= len(self.words):
            return True  # All words placed successfully
        
        word = self.words[word_index]
        print(f"  Trying to place word {word_index + 1}/{len(self.words)}: {word}")
        
        # Get all valid placements for this word
        valid_placements = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                for direction in ['across', 'down']:
                    if (self.can_place_word_scrabble(word, row, col, direction) and
                        self.has_connection_to_existing(word, row, col, direction)):
                        
                        # Calculate intersections for scoring
                        intersections = 0
                        if direction == 'across':
                            for i in range(len(word)):
                                if self.grid[row][col + i] == word[i]:
                                    intersections += 1
                        else:
                            for i in range(len(word)):
                                if self.grid[row + i][col] == word[i]:
                                    intersections += 1
                        
                        valid_placements.append((row, col, direction, intersections))
        
        # Sort by intersections (more is better) for better success rate, add randomization
        valid_placements.sort(key=lambda x: (-x[3], random.random()))
        
        print(f"    Found {len(valid_placements)} valid placements")
        
        # Try each valid placement
        for row, col, direction, _ in valid_placements:
            # Save current state
            old_grid = [row[:] for row in self.grid]
            old_placed_words = self.placed_words[:]
            
            # Place the word
            self.place_word(word, row, col, direction)
            
            # Try to place remaining words
            if self._backtrack_solve(word_index + 1):
                return True  # Success!
            
            # Backtrack: restore previous state
            self.grid = old_grid
            self.placed_words = old_placed_words
        
        print(f"    ❌ Could not place {word} - backtracking")
        
        return False  # No valid placement found

    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get the minimal bounding box containing all words."""
        min_row, max_row = self.grid_size, -1
        min_col, max_col = self.grid_size, -1
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] != ' ':
                    min_row = min(min_row, row)
                    max_row = max(max_row, row)
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)
        
        return min_row, max_row, min_col, max_col

    def display_grid(self):
        """Display the crossword grid."""
        print("\nScrabble-Style Crossword:")
        print("=" * 40)
        
        min_row, max_row, min_col, max_col = self.get_bounding_box()
        
        if max_row == -1:
            print("No words placed")
            return
        
        # Display only the relevant portion
        for row in range(min_row, max_row + 1):
            line = ""
            for col in range(min_col, max_col + 1):
                if self.grid[row][col] == ' ':
                    line += "."
                else:
                    line += self.grid[row][col]
                line += " "
            print(line)

    def display_word_list(self):
        """Display the words placed in the puzzle."""
        print(f"\nPlaced words ({len(self.placed_words)}):")
        print("-" * 30)
        for i, (word, row, col, direction) in enumerate(self.placed_words, 1):
            print(f"{i}. {word} ({direction}) at ({row}, {col})")


def main():
    """Generate a Scrabble-style crossword."""
    names = [
        "David", "Debbie", "Beth", "Steve", "Sam", "Lila", "Wes", 
        "Hannah", "Dave", "Paige", "Natalie", "Ben", "Kate", 
        "Lena", "June", "Abby", "Rich", "William", "Sienna"
    ]
    
    print("Generating Scrabble-style crossword with backtracking...")
    puzzle = ScrabbleCrossword(names, grid_size=25)
    puzzle.clear_grid()  # Start with clean grid
    
    if puzzle.generate_puzzle():
        puzzle.display_grid()
        puzzle.display_word_list()
        print(f"\nSuccessfully placed {len(puzzle.placed_words)} out of {len(names)} words!")
        
        # Check if we got all words
        if len(puzzle.placed_words) == len(names):
            print("🎉 All names successfully placed with proper orthogonal connections!")
        else:
            missing = set(names) - {word for word, _, _, _ in puzzle.placed_words}
            print(f"Missing: {', '.join(missing)}")
    else:
        print("Failed to generate crossword - try increasing grid size or relaxing constraints")


if __name__ == "__main__":
    main()
