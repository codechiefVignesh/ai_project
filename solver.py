import tkinter as tk
import random
import enchant
import os
import copy
from tkinter import messagebox

# Constants
BOARD_SIZE = 5
EMPTY = ""
PLAYER_1_COLOR = "lightblue"
PLAYER_2_COLOR = "lightgreen"
WORDS_FILE = "words_alpha.txt"

# Load the English dictionary
english_dict = enchant.Dict("en_US")

# Game State Class
class WordGame:
    def __init__(self):
        self.player_boards = {
            1: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            2: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        }
        self.current_player = 1  # Player 1 starts
        self.previous_state = None
        self.word_count = {1: 0, 2: 0}  # Track the number of words each player has filled
        self.load_word_list()

        # Start with a random word for each player
        self.start_with_random_word(1)
        self.start_with_random_word(2)

    def load_word_list(self):
        """Load a list of valid words from the given word file."""
        if not os.path.isfile(WORDS_FILE):
            raise FileNotFoundError(f"The word list file '{WORDS_FILE}' is missing.")
        with open(WORDS_FILE, "r") as word_file:
            self.word_list = [word.strip().lower() for word in word_file if len(word.strip()) == BOARD_SIZE]

    def start_with_random_word(self, player):
        """Start the game by placing a random word for a specific player."""
        initial_word = random.choice(self.word_list)
        orientation = random.choice(["row", "column"])
        index = random.randint(0, BOARD_SIZE - 1)

        if orientation == "row":
            self.player_boards[player][index] = list(initial_word)
        else:
            for i in range(BOARD_SIZE):
                self.player_boards[player][i][index] = initial_word[i]

        self.word_count[player] += 1  # Track the word count

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 2 if self.current_player == 1 else 1

    def is_board_full(self, player):
        """Check if a player's board is completely filled."""
        board = self.player_boards[player]
        return all(EMPTY not in row for row in board)

    def suggest_word(self, pattern):
        """Suggest a word given a row/column pattern with some known letters."""
        for word in self.word_list:
            if len(word) != BOARD_SIZE:
                continue

            # Check if the word matches the pattern
            matches = True
            for i in range(BOARD_SIZE):
                if pattern[i] != EMPTY and pattern[i] != word[i]:
                    matches = False
                    break

            if matches:
                return word

        return None  # No matching word found

    def fill_board_with_word(self, word, orientation, index):
        """Fill a row or column with the given word."""
        if orientation == "row":
            self.player_boards[self.current_player][index] = list(word)
        else:
            for i in range(BOARD_SIZE):
                self.player_boards[self.current_player][i][index] = word[i]

    def revert_to_previous_state(self):
        """Revert to the previous game state."""
        self.player_boards[self.current_player] = copy.deepcopy(self.previous_state)

    def get_board_for_player(self, player):
        """Get the board for the specified player."""
        return self.player_boards[player]


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
                )
                entry.grid(row=i, column=j, padx=5, pady=5)
                row.append(entry)
            entries.append(row)

        return entries

    def submit_move(self):
        """Submit the player's move and let the AI suggest a word."""
        current_player = self.game.current_player
        entries = self.frames[current_player]

        # Save the current state for potential backtracking
        self.game.previous_state = copy.deepcopy(self.game.get_board_for_player(current_player))

        # Find the new letter and its position
        row_idx = None
        col_idx = None
        orientation = None  # Will be determined based on the player's input

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell_content = entries[i][j].get().lower()  # Ensure case consistency
                if cell_content != EMPTY and self.game.get_board_for_player(current_player)[i][j] == EMPTY:
                    # Found the new letter and its position
                    row_idx = i
                    col_idx = j
                    break

            if row_idx is not None:
                break

        if row_idx is None or col_idx is None:
            messagebox.showerror("Invalid Input", "Please enter a valid letter in an empty cell.")
            return

        # Determine orientation and corresponding pattern
        row_pattern = [entries[row_idx][k].get().lower() for k in range(BOARD_SIZE)]
        column_pattern = [entries[k][col_idx].get().lower() for k in range(BOARD_SIZE)]

        suggested_word = None

        # Try to find a word in both orientations, row first, then column
        suggested_word = self.game.suggest_word(row_pattern)

        if suggested_word:
            orientation = "row"
            self.game.fill_board_with_word(suggested_word, orientation, row_idx)
        else:
            suggested_word = self.game.suggest_word(column_pattern)

            if suggested_word:
                orientation = "column"
                self.game.fill_board_with_word(suggested_word, orientation, col_idx)

        if suggested_word:
            # Update the GUI with the filled word
            self.update_entries()

            if self.game.is_board_full(current_player):
                messagebox.showinfo("Game Over", f"Player {current_player} wins with {self.game.word_count[current_player]} words!")
                self.quit()
            else:
                # Switch player after successful move
                self.game.switch_player()
                self.turn_label.config(text=f"Player {self.game.current_player}'s turn")
                self.update_entries()  # Update the board to reflect the new current player
        else:
            # If no valid word is found, revert to the previous state
            self.game.revert_to_previous_state()
            self.update_entries()  # Update the GUI to reflect the reverted state
            messagebox.showerror("Invalid Word", "Could not find a valid word with given pattern.")

    def update_entries(self):
        """Update the GUI to reflect the current state of the boards."""
        for player in [1, 2]:
            game_board = self.game.get_board_for_player(player)
            entries = self.frames[player]

            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    entries[i][j].delete(0, tk.END)  # Clear existing text
                    entries[i][j].insert(0, game_board[i][j])  # Fill with the current board state
                    # Enable inputs only for the current player
                    state = "normal" if player == self.game.current_player else "disabled"
                    entries[i][j].configure(state=state)


# Main execution
if __name__=="__main__":
    game = WordGame()
    gui = WordGameGUI(game)
    gui.mainloop()
