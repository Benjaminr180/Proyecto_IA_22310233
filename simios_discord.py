import discord
import asyncio
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use("fivethirtyeight")

token = open("token.txt", "r").read()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

guild_obj = None  # Variable global para guardar el guild


def reporte_comunidad(guild):
    online = 0
    idle = 0
    offline = 0

    if guild is None:
        return online, idle, offline  # Si no hay guild, devolver ceros

    for miembro in guild.members:
        status = str(miembro.status)
        if status == "online":
            online += 1
        elif status == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline


async def tarea_metricas_usuario():
    await client.wait_until_ready()
    global guild_obj
    guild_obj = client.get_guild(1383977531681542245)  # Cambia por tu ID de servidor real

    while not client.is_closed():
        if guild_obj is None:
            print("La variable guild_obj es None, esperando a que se defina...")
            await asyncio.sleep(5)
            continue

        try:
            online, idle, offline = reporte_comunidad(guild_obj)

            # Guardar métricas en CSV
            with open("usermetrics.csv", "a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            # Generar y actualizar el gráfico
            plt.clf()
            df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df['date'] = pd.to_datetime(df['time'], unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", axis=1, inplace=True)
            df.set_index("date", inplace=True)
            df['online'].plot()
            plt.legend()
            plt.savefig("online.png")

            await asyncio.sleep(5)

        except Exception as e:
            print(f"Error en tarea_metricas_usuario: {e}")
            await asyncio.sleep(5)


@client.event
async def on_ready():
    global guild_obj
    guild_obj = client.get_guild(1383977531681542245)  # Cambia por tu ID de servidor real
    if guild_obj is None:
        print("Error: No se encontró el servidor con ese ID.")
    else:
        print(f"Conectado como {client.user} en el servidor {guild_obj.name}")


@client.event
async def on_message(message):
    global guild_obj

    if message.author == client.user:
        return

    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    if guild_obj is None:
        print("Guild no definido aún, ignorando mensaje.")
        return

    contenido = message.content.lower()

    if contenido == "simio.member_count()":
        await message.channel.send(f"```py\n{guild_obj.member_count}```")

    elif contenido == "hola":
        await message.channel.send(f"Hola {message.author.name}, ¿cómo estás?")

    elif contenido == "simio.logout()":
        await client.close()

    elif contenido == "simio.community_report()":
        online, idle, offline = reporte_comunidad(guild_obj)
        await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

        # Enviar la imagen del gráfico
        file = discord.File("online.png", filename="online.png")
        await message.channel.send("online.png", file=file)


async def main():
    asyncio.create_task(tarea_metricas_usuario())
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())