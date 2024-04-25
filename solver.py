#CS22B2004
#CS22B2008

# WORD SOLVER PROBLEM USING CSP, BACKTRACKING, HEURISTIC, AND LINEAR SEARCH automated problem solving


import tkinter as tk # importing the tkinter library for the gui to generate the boards

import random  # random function which we shall use later in the CSP variable and domain selection 

import enchant # python nltk library to have a custom dictionary

import os

import copy

from tkinter import messagebox

# DEFINITION 
BOARD_SIZE = 5
EMPTY = ""
PLAYER_1_COLOR = "lightblue"
PLAYER_2_COLOR = "lightgreen"
WORDS_FILE = "words_alpha.txt"


english_dict = enchant.Dict("en_US")


class WordGame:
    def __init__(self):
        self.player_boards = {
            1: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            2: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        }
        self.current_player = 1  # Player 1 starts
        self.previous_state = {1: None, 2: None}  # Maintain previous states for backtracking
        self.word_count = {1: 0, 2: 0}  # Track the number of words each player has filled
        self.load_word_list()
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
        matching_words = []
        for word in self.word_list:
            if len(word) != BOARD_SIZE:
                continue

            matches = True
            for i in range(BOARD_SIZE):
                if pattern[i] != EMPTY and pattern[i] != word[i]:
                    matches = False
                    break

            if matches:
                matching_words.append(word)

        if matching_words:
            return random.choice(matching_words)
        return None

    def fill_board_with_word(self, word, orientation, index):
        """Fill a row or column with the given word."""
        if orientation == "row":
            self.player_boards[self.current_player][index] = list(word)
        else:
            for i in range(BOARD_SIZE):
                self.player_boards[self.current_player][i][index] = word[i]

    def revert_to_previous_state(self):
        """Revert to the previous game state."""
        self.player_boards[self.current_player] = copy.deepcopy(self.previous_state[self.current_player])

    def save_previous_state(self):
        """Save the current state for potential backtracking."""
        self.previous_state[self.current_player] = copy.deepcopy(self.player_boards[self.current_player])

    def get_board_for_player(self, player):
        """Get the board for the specified player."""
        return self.player_boards[player]

    def reset_boards(self):
        """Reset both player boards to an empty state."""
        self.player_boards = {
            1: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            2: [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        }
        self.word_count = {1: 0, 2: 0}  # Reset word counts
        self.current_player = 1
        self.previous_state = {1: None, 2: None}  # Reset previous states


class WordGameGUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("2-Player Word Game")
        self.game = game
        self.game.gui = self 
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

        reset_button = tk.Button(
            self, text="Reset Game", command=self.reset_game
        )
        reset_button.grid(row=1, column=1, columnspan=2, pady=10)

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

    def reset_game(self):
        """Reset the game to its initial state."""
        self.game.reset_boards() 
        self.update_entries()  # Clear all entries
        self.turn_label.config(text=f"Player {self.game.current_player}'s turn")
        messagebox.showinfo("Game Reset", "The game has been reset to empty state.")

    def submit_move(self):
        """Submit the player's move and let the AI suggest a word."""
        current_player = self.game.current_player
        entries = self.frames[current_player]

        # Save the current state for potential backtracking
        self.game.save_previous_state()

        # Find the letter that the player filled in and its position
        letter = None
        row_idx = None
        col_idx = None

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell_content = entries[i][j].get().lower()   # ensure scalability by converting all cases to lowercase
                if cell_content != EMPTY and self.game.player_boards[current_player][i][j] == EMPTY:
                    letter = cell_content
                    row_idx = i
                    col_idx = j
                    break

            if letter:
                break

        if not letter:
            messagebox.showerror("Invalid Input", "Please enter a valid letter.")
            return

         # determine the CSP's variable on random basis and the left out one will be the domain
        orientation = random.choice(["row", "column"])

        if orientation == "row":
            pattern = [entries[row_idx][k].get().lower() for k in range(BOARD_SIZE)]
            index = row_idx
        else:
            pattern = [entries[k][col_idx].get().lower() for k in range(BOARD_SIZE)]
            index = col_idx

        suggested_word = self.game.suggest_word(pattern)

        if suggested_word:
            # Fill the appropriate row or column with the suggested word
            if orientation == "row":
                self.game.fill_board_with_word(suggested_word, orientation, row_idx)
            else:
                self.game.fill_board_with_word(suggested_word, orientation, col_idx)

            # Update the GUI to reflect the new board state
            self.update_entries()

            # Check if the board is full
            if self.game.is_board_full(current_player):
                # Determine the winner based on the valid word count
                player_1_count = self.game.word_count[1]
                player_2_count = self.game.word_count[2]

                if player_1_count > player_2_count:
                    winner = 1
                elif player_2_count > player_2_count:
                    winner = 2
                else:
                    winner = None

                if winner:
                    messagebox.showinfo("Game Over", f"Player {winner} wins with more words!")
                else:
                    messagebox.showinfo("Game Over", "It's a draw!")

                self.quit()
            else:
                # Switch to the other player and update the GUI
                self.game.switch_player()
                self.turn_label.config(text=f"Player {self.game.current_player}'s turn")
                self.update_entries()  # Update the board to reflect the new current player

        else:
            # Backtrack to the previous state if a valid word isn't found
            self.game.revert_to_previous_state()
            self.update_entries()  # Update the GUI to reflect the previous state
            messagebox.showerror("Invalid Word", "Could not find a valid word.")

            # If the boards are full and no valid words are found, end the game
            if self.game.is_board_full(1) and self.game.is_board_full(2):
                messagebox.showinfo("Game Over", "No more valid words can be found. The game is over.")

    def update_entries(self):
        """Update the GUI to reflect the current state of the boards."""
        # Ensure the cuurent player board is active # if player 1 is playing then player 2 board should be disabled
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



if __name__=="__main__":  # just a formal definition for initiating the program from here in an order
    
    game = WordGame()  #initialise the object for word solver class
    
    gui = WordGameGUI(game)  # initialising the gui for word solver games using tkinter 
    
    gui.mainloop()  # accessing the class' member function to start the games
