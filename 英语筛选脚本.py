import json
import re
import sys
import tkinter as tk

from tqdm import tqdm


class FlashcardApp:
    def __init__(self, root, cards):
        self.root = root
        self.cards = cards
        if self.cards is None:
            raise ValueError("No cards data provided")
        if not isinstance(self.cards, list):
            raise ValueError("Cards data should be a list")
        self.current_index = 0
        self.is_flipped = False

        self.root.title("Flashcard Viewer")

        # Create frame for card
        self.card_frame = tk.Frame(root)
        self.card_frame.pack(fill=tk.BOTH, expand=True)

        # Create front and back labels
        self.front_label = tk.Label(self.card_frame, text="", font=("Arial", 16), bg="white", anchor="center",
                                    wraplength=380)
        self.back_label = tk.Label(self.card_frame, text="", font=("Arial", 16), bg="lightgray", anchor="center",
                                   wraplength=380)

        # Display front side by default
        self.front_label.pack(fill=tk.BOTH, expand=True)
        self.back_label.pack_forget()

        # Create flip button
        self.flip_button = tk.Button(root, text="Flip Card", command=self.flip_card)
        self.flip_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

        # Create next and previous buttons
        self.next_button = tk.Button(root, text="Next", command=self.next_card)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.X, expand=True)

        self.prev_button = tk.Button(root, text="Previous", command=self.prev_card)
        self.prev_button.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.X, expand=True)

        # Update layout when window is resized
        self.root.bind("<Configure>", self.on_resize)

        # Show the first card
        self.show_card()

    def show_card(self):
        card = self.cards[self.current_index]
        self.front_label.config(text=self.format_front_text(card))
        self.back_label.config(text=self.format_back_text(card))
        self.is_flipped = False
        self.front_label.pack(fill=tk.BOTH, expand=True)
        self.back_label.pack_forget()

    def flip_card(self):
        if self.is_flipped:
            self.front_label.pack(fill=tk.BOTH, expand=True)
            self.back_label.pack_forget()
        else:
            self.front_label.pack_forget()
            self.back_label.pack(fill=tk.BOTH, expand=True)
        self.is_flipped = not self.is_flipped

    def next_card(self):
        self.current_index = (self.current_index + 1) % len(self.cards)
        self.show_card()

    def prev_card(self):
        self.current_index = (self.current_index - 1) % len(self.cards)
        self.show_card()

    def format_front_text(self, card):
        return f"Word: {card['word']}"

    def format_back_text(self, card):
        translations = "\n".join([f"- {t['translation']} ({t['type']})" for t in card.get('translations', [])])
        phrases = "\n".join(
            [f"- {p['phrase']}: {p['translation']}" for p in card.get('phrases', [])]) or "No phrases available"
        return f"Translations:\n{translations}\nPhrases:\n{phrases}"

    def on_resize(self, event):
        # Adjust wraplength based on window width
        new_width = self.card_frame.winfo_width() - 20  # Subtract padding
        self.front_label.config(wraplength=new_width)
        self.back_label.config(wraplength=new_width)


def load_data(filepath):
    """ Load JSON data into a dictionary with words as keys """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("JSON data should be a list of cards")

        # Create a dictionary with words as keys
        word_dict = {entry['word']: entry for entry in data}
        return word_dict
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading JSON data: {e}")
        return {}


def find_word(word, word_dict):
    """ Find a word in the dictionary """
    return word_dict.get(word)


def main():
    CET_path = './4-CET6-顺序.json'
    word_dict = load_data(CET_path)

    print("按Enter后请输入文本(按Ctrl+D退出):")
    input_text = sys.stdin.read()
    word_list = input_text.split()
    word_list = [re.sub(r'[^a-zA-Z]', '', word) for word in word_list]

    merge = []

    # Initialize progress bar with tqdm
    with tqdm(total=len(word_list), desc="Processing") as pbar:
        for letter in word_list:
            data = find_word(letter, word_dict)

            if data is not None:
                merge.append(data)

            # Update progress bar
            pbar.update(1)

    # Do something with merge data
    print(f"Processed {len(merge)} cards.")
    root = tk.Tk()
    app = FlashcardApp(root, merge)
    root.mainloop()


if __name__ == "__main__":
    main()
