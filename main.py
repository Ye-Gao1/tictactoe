import discord
import random
import asyncio
import os

TOKEN = os.environ['Token']
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DIRECTIONS = {
    '⬅️': (-1, 0),
    '➡️': (1, 0),
    '⬆️': (0, -1),
    '⬇️': (0, 1)
}

GRID_SIZE = 10
SNAKE_ICON = '🟩'
FOOD_ICON = '🍎'
EMPTY_ICON = '⬜'

class SnakeGame:
    def __init__(self):
        self.snake = [(5, 5)]
        self.direction = DIRECTIONS['➡️']
        self.food = self.random_food()
        self.score = 0

    def random_food(self):
        while True:
            food = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if food not in self.snake:
                return food

    def move(self):
        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        if (new_head in self.snake or 
            not (0 <= new_head[0] < GRID_SIZE) or 
            not (0 <= new_head[1] < GRID_SIZE)):
            return False

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.food = self.random_food()
            self.score += 1
        else:
            self.snake.pop()
        return True

    def render(self):
        grid = [[EMPTY_ICON] * GRID_SIZE for _ in range(GRID_SIZE)]
        for x, y in self.snake:
            grid[y][x] = SNAKE_ICON
        grid[self.food[1]][self.food[0]] = FOOD_ICON
        return '\n'.join(''.join(row) for row in grid)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == '!start':
        game = SnakeGame()
        embed = discord.Embed(title="Snake Game", description=game.render())
        embed.add_field(name="Score", value=game.score)
        game_message = await message.channel.send(embed=embed)

        for emoji in DIRECTIONS.keys():
            await game_message.add_reaction(emoji)

        def check(reaction, user):
            return user != client.user and str(reaction.emoji) in DIRECTIONS

        while True:
            try:
                tasks = [
                    asyncio.create_task(client.wait_for('reaction_add', timeout=0.5, check=check)),
                    asyncio.create_task(asyncio.sleep(0.5))
                ]
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                for task in pending:
                    task.cancel()

                if done:
                    result = done.pop().result()
                    if isinstance(result, tuple):
                        reaction, user = result
                        game.direction = DIRECTIONS[str(reaction.emoji)]
                        await game_message.remove_reaction(reaction.emoji, user)

                if not game.move():
                    await message.channel.send(f"Game over! Final score: {game.score}")
                    break

                embed = discord.Embed(title="Snake Game", description=game.render())
                embed.add_field(name="Score", value=game.score)
                await game_message.edit(embed=embed)

            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        await message.channel.send("Type `!start` to play again!")

client.run(TOKEN)