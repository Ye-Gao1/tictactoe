import discord, os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

board = [':white_large_square:'] * 9
current_player = 'X'
game_in_progress = False
game_message = None

NUMBER_EMOJIS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='tictactoe', help='Starts a new Tic Tac Toe game')
async def tictactoe(ctx):
    global board, current_player, game_in_progress, game_message
    board = [':white_large_square:'] * 9
    current_player = 'X'
    game_in_progress = True
    game_message = await ctx.send("Starting a new game of Tic Tac Toe!")
    await display_board()
    for emoji in NUMBER_EMOJIS:
        await game_message.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    global board, current_player, game_in_progress, game_message
    if user == bot.user or not game_in_progress or reaction.message.id != game_message.id:
        return

    if str(reaction.emoji) in NUMBER_EMOJIS:
        position = NUMBER_EMOJIS.index(str(reaction.emoji))
        if board[position] == ':white_large_square:':
            board[position] = ':regional_indicator_x:' if current_player == 'X' else ':o2:'
            await display_board()

            if check_winner():
                await reaction.message.channel.send(f"Player {current_player} wins!")
                game_in_progress = False
            elif ':white_large_square:' not in board:
                await reaction.message.channel.send("It's a tie!")
                game_in_progress = False
            else:
                current_player = 'O' if current_player == 'X' else 'X'
                await reaction.message.channel.send(f"It's player {current_player}'s turn!")
        else:
            await reaction.message.channel.send("That position is already taken. Choose another.")

    await reaction.remove(user)

async def display_board():
    global game_message
    board_display = '\n'.join([' '.join(board[i:i+3]) for i in range(0, 9, 3)])
    await game_message.edit(content=f"Current board:\n{board_display}")

def check_winner():
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ':white_large_square:':
            return True
    return False

bot.run(os.environ['Token'])