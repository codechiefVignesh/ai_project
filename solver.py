import tkinter as tk
import random
import enchant
from tkinter import messagebox
import os

# Use a dictionary for valid word checking
english_dict = enchant.Dict("en_US")

# Constants
BOARD_SIZE = 5
EMPTY = ""
PLAYER_1_COLOR = "lightblue"
PLAYER_2_COLOR = "lightgreen"
WORDS_FILE = "words_alpha.txt"

# Game State Class
class WordGame:
    def __init__(self):
        # Initialize boards for Player 1 and Player 2
        self.player_boards = {
            1: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            2: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        }
        self.current_player = 1
        self.word_count = {1: 0, 2: 0}  # Track words formed by each player
        self.load_word_list()

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 2 if self.current_player == 1 else 1

    def is_board_full(self, player):
        """Check if a player's board is completely filled."""
        board = self.player_boards[player]
        for row in board:
            if EMPTY in row:
                return False
        return True

    def load_word_list(self):
        """Load the list of valid words from the word file."""
        if not os.path.isfile(WORDS_FILE):
            raise FileNotFoundError(f"The word list file '{WORDS_FILE}' is missing.")
        with open(WORDS_FILE, "r") as word_file:
            self.word_list = word_file.read().splitlines()

    def suggest_word(self, letter, index, orientation):
        """Suggest a word with a given letter at a specific index."""
        possible_words = []

        # Find words with the specified letter at a given position
        for word in self.word_list:
            if len(word) == BOARD_SIZE and word[index] == letter:
                possible_words.append(word)

        if possible_words:
            return random.choice(possible_words)
        else:
            return None

    def fill_board_with_word(self, word, orientation, index):
        """Fill the appropriate row or column with the given word."""
        board = self.player_boards[self.current_player]

        if orientation == "row":
            board[index] = list(word)
        else:
            for i in range(BOARD_SIZE):
                board[i][index] = word[i]

    def validate_word(self, word):
        """Check if a word is valid using the enchant dictionary."""
        return english_dict.check(word)

# GUI Class for the game
class WordGameGUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("2-Player Word Game")
        self.game = game
        self.create_widgets()

    def create_widgets(self):
        """Create separate sections for each player's board."""
        self.frames = {
            1: self.create_player_frame(1, PLAYER_1_COLOR),
            2: self.create_player_frame(2, PLAYER_2_COLOR),
        }
        self.turn_label = tk.Label(
            self, text=f"Player {self.game.current_player}'s turn", font=("Arial", 14)
        )
        self.turn_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Submit button to make a move
        submit_button = tk.Button(
            self, text="Submit Move", command=self.submit_move
        )
        submit_button.grid(row=1, column=0, columnspan=2, pady=10)

    def create_player_frame(self, player, color):
        frame = tk.Frame(self, bg=color, padx=10, pady=10)
        frame.grid(row=0, column=player - 1, padx=20, pady=20)

        entries = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                entry = tk.Entry(
                    frame,
                    width=3,
                    font=("Arial", 16),
                    justify="center",
                    bg="white",
                    state="normal" if self.game.current_player == player else "disabled",
                )
                entry.grid(row=i, column=j, padx=5, pady=5)
                row.append(entry)
            entries.append(row)

        return entries

    def submit_move(self):
        """Submit the player's move and let the AI suggest a word."""
        current_player = self.game.current_player
        entries = self.frames[current_player]

        # Find the letter that the player filled in
        letter = None
        orientation = None
        row_idx = None
        col_idx = None

        # Detect which cell the player filled
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if entries[i][j].get() == "":
                    continue  # Skip empty cells
                letter = entries[i][j].get().upper()
                if len(letter) == 1:
                    row_idx = i
                    col_idx = j
                    break
            if letter:
                break

        if not letter:
            messagebox.showerror("Invalid Input", "Please enter a valid letter.")
            return

        # Suggest a word based on the player's letter and orientation
        orientation = random.choice(["row", "column"])

        if orientation == "row":
            word = self.game.suggest_word(letter, col_idx, "row")
        else:
            word = self.game.suggest_word(letter, row_idx, "column")

        if word and self.game.validate_word(word):
            # Fill the appropriate row or column with the suggested word
            self.game.fill_board_with_word(word, orientation, orientation == "row" and row_idx or col_idx)

            # Update word count for the player
            self.game.word_count[current_player] += 1

            # Update the GUI to reflect the new board state
            self.update_entries()

            # Check if the board is full
            if self.game.is_board_full(current_player):
                messagebox.showinfo(
                    "Game Over", f"Player {current_player} wins with {self.game.word_count[current_player]} words!"
                )
                self.quit()
            else:
                self.game.switch_player()
                self.turn_label.config(
                    text=f"Player {self.game.current_player}'s turn"
                )

        else:
            messagebox.showerror("Invalid Word", "Could not suggest a valid word with this letter.")

    def update_entries(self):
        """Update the GUI to reflect the board's current state."""
        entries = self.frames[self.game.current_player]
        game_board = self.game.player_boards[self.game.current_player]

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, game_board[i][j])

# Main execution
if __name__ == "__main__":
    game = WordGame()
    gui = WordGameGUI(game)
    gui.mainloop()
