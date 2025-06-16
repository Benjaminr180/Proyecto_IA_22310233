import discord

# Definir intents básicos
intents = discord.Intents.default()
intents.message_content = True  # Necesario para poder leer el contenido de los mensajes

# Crear cliente con intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Conectado como {client.user}')

@client.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == client.user:
        return

    print(f'Mensaje recibido en {message.channel}: {message.author}: {message.content}')

# Leer token desde archivo token.txt (coloca solo el token en ese archivo)
with open("token.txt", "r") as f:
    token = f.read().strip()

client.run(token)
