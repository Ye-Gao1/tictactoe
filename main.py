import discord
import requests
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
Token = os.environ['Token']
client = discord.Client(intents=intents)

game_in_progress = False
word_to_guess = ""
guessed_letters = set()
attempts_left = 6

def get_random_word():
    response = requests.get("https://random-word-api.herokuapp.com/word?number=1&length=5")
    if response.status_code == 200:
        return response.json()[0]
    else:
        return "apple"

def display_word():
    return ' '.join(letter if letter in guessed_letters else '_' for letter in word_to_guess)

def display_hangman():
    stages = [
        "  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
        "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n========="
    ]
    return stages[6 - attempts_left]

def format_game_state():
    hangman = display_hangman()
    word = display_word()
    guesses = ", ".join(sorted(guessed_letters)) or "None"
    return f"```\n{hangman}\n\nWord: {word}\nGuessed letters: {guesses}\nAttempts left: {attempts_left}\n```"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global game_in_progress, word_to_guess, guessed_letters, attempts_left

    if message.author == client.user:
        return

    if message.content.startswith('!hangman'):
        if game_in_progress:
            await message.channel.send("A game is already in progress!")
        else:
            game_in_progress = True
            word_to_guess = get_random_word()
            guessed_letters = set()
            attempts_left = 6
            await message.channel.send("Hangman game started! Guess the 5-letter word.")
            await message.channel.send(format_game_state())

    elif game_in_progress and len(message.content) == 1:
        guess = message.content.lower()
        if guess in guessed_letters:
            await message.channel.send("You already guessed that letter!")
        elif guess in word_to_guess:
            guessed_letters.add(guess)
            await message.channel.send("Correct guess!")
        else:
            guessed_letters.add(guess)
            attempts_left -= 1
            await message.channel.send("Wrong guess!")

        await message.channel.send(format_game_state())

        if set(word_to_guess) <= guessed_letters:
            await message.channel.send(f"Congratulations! You guessed the word: {word_to_guess}")
            game_in_progress = False
        elif attempts_left == 0:
            await message.channel.send(f"Game over! The word was: {word_to_guess}")
            game_in_progress = False

client.run(Token)