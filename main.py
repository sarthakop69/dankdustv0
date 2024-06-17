import discord
import random
import requests
from discord.ext import commands
import os
import asyncio
import time
import mimetypes
import urllib.request
import json
import os.path
import io
import collections
import codecs
import base64
from collections import defaultdict, Counter
from io import BytesIO
import re
from urllib.parse import quote
import datetime
import aiohttp
import locale
import sqlite3
import subprocess
import sys
import mysql.connector
import aiosqlite
from discord.ui import Button, View
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='pls ', intents=intents, help_command=None)
active_races = {}
mines_cooldowns = {}
ongoing_fights = {}
fetch_cooldowns = {}
stake_cooldowns = {}
fight_requests = {}
active_searches = {}
noleave_users = []
ongoing_payments = defaultdict(bool)
ongoing_transactions = defaultdict(bool)
auto_reply_dm_users = []
wmc_ongoing_games = defaultdict(bool)
default_cooldown_minutes = 0
search_cooldowns = {}
ongoing_fights = {}
pending_fight_requests = {}
ongoing_fight_requests = set()
kick_cooldowns = {}
JSON_FILE = 'non_anonymous_users.json'
balances = {}
owners = ['sid', 'sunny', 'robert', 'nicx', 'deep', 'mohamed', 'weltan', 'xily']
weltan_enabled = False
user_messages = []
watch_channel_id = 1206873111333703690
watched_keywords = {}
locale.setlocale(locale.LC_ALL, '')
doggy_react_users = {}
ongoing_games = {}
fish_cooldowns = {}
hunt_cooldowns = {}
start_time = time.time()
shop_items = {
    'beard': {'name': ':man_beard: Mohamed ki beard', 'price': 10000, 'id': 'beard'},
    'sarthak': {'name': ':troll: Sarthak', 'price': 100000, 'id': 'sarthak'},
    'dog': {'name': '🐶 Doggy', 'price': 300000, 'id': 'dog'},
    'sun': {'name': '🌞 Sunny', 'price': 500000, 'id': 'sun'},
    'skull': {'name': '<:SKULL_SKELETON:1247908834861777017> SKULL SKELETON', 'price': 1000000, 'id': 'skull'},
    'banana': {'name': '🍌 Xily ka banana', 'price': 10000000, 'id': 'banana'},
    'bone': {'name': ':bone: Bone', 'price': 5000, 'id': 'bone', 'buyable': False},
    'leash': {'name': ":service_dog: Robert's Leash", 'price': 25000, 'id': 'leash', 'buyable': False},
    'dogfood': {'name': ':canned_food: Dog Food', 'price': 100000, 'id': 'dogfood', 'buyable': False},
    'rarelootbox': {'name': ':gift: Rare Loot Box', 'price': 5000, 'id': 'rarelootbox', 'buyable': False},
    'legendarylootbox': {'name': ':gift: Legendary Loot Box', 'price': 100000, 'id': 'legendarylootbox', 'buyable': False},
    'bestlootbox': {'name': ':gift: Best Loot Box', 'price': 4000000, 'id': 'bestlootbox', 'buyable': False},
    'bolb': {'name': ':red_circle: bolb', 'price': 50000000, 'id': 'bolb', 'buyable': False},
    'dupe': {'name': ':man_technologist: Dupe Hunter', 'price': 2500000, 'id': 'dupe', 'buyable': False},
    'kuppy': {'name': ':dog2: Kuppy', 'price': 50000, 'id': 'kuppy', 'buyable': False},
    'grass': {'name': ':island: Grass', 'price': 200000, 'id': 'grass', 'buyable': False},
    'pyramid': {'name': '<:pyramid:1247931115763925082> Mohameds Pyramid', 'price': 911000, 'id': 'pyramid', 'buyable': True},
    'nicx': {'name': '<a:nicxcrown:1247935115900751933> Nicx Crown', 'price': 1000000, 'id': 'nicx', 'buyable': False},
    'enicx': {'name': '<a:enicxcrown:1247935144489386094> Enchanted Nicx Crown', 'price': 75000000, 'id': 'enicx', 'buyable': False},
    'deepsegirl': {'name': ":girl: Deep's Egirl", 'price': 10, 'id': 'deepsegirl', 'buyable': False},
    'godbox': {'name': '<:godbox:1247980941310427157> God Box', 'price': 40000000, 'id': 'godbox', 'buyable': True, 'sellable': True},
    'stock': {'name': ':scroll: Stock', 'price': None, 'id': 'stock', 'buyable': True, 'sellable': True},
    'duck': {'name': ':swan: wise duck', 'price': 25000, 'id': 'duck', 'sellable': True, 'buyable': False},
    'cat': {'name': "<a:weltan:1249106180677308466> weltan's cat", 'price': 25000000, 'id': 'cat', 'sellable': True, 'buyable': False},
    'temple': {'name': ":hindu_temple: sid's temple", 'price': 300000, 'id': 'temple', 'sellable': True, 'buyable': False},
    'tren': {'name': "<:tren:1249596585961324545> sunny's tren", 'price': 100000000, 'id': 'tren', 'sellable': True, 'buyable': False}
}
SEARCH_TIMEOUT = 10
PREFIXES = [',']
dice_cooldowns = {}

def load_non_anonymous_users():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as file:
        return json.load(file)

def save_non_anonymous_users(users):
    with open(JSON_FILE, 'w') as file:
        json.dump(users, file)

async def send_message_with_retry(channel, content, retries=3):
    for attempt in range(retries):
        try:
            await channel.send(content)
            break
        except discord.Forbidden:
            if attempt < retries - 1:
                await asyncio.sleep(1)  
            else:
                print(f"Failed to send message in {channel.name} after {retries} attempts due to missing permissions.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
            
async def setup_database():
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await conn.execute('''CREATE TABLE IF NOT EXISTS levels
                               (user_id INTEGER PRIMARY KEY,
                                level INTEGER,
                                experience INTEGER,
                                rebirth_level INTEGER DEFAULT 0)''')
            await conn.commit()
            
            await conn.execute('''CREATE TABLE IF NOT EXISTS balances
                               (user_id INTEGER PRIMARY KEY,
                                wallet INTEGER DEFAULT 0,
                                bank INTEGER DEFAULT 0,
                                inventory INTEGER DEFAULT 0,
                                net_worth INTEGER DEFAULT 0)''')
            await conn.commit()
            await conn.execute('''CREATE TABLE IF NOT EXISTS badges
                            (user_id INTEGER,
                                badge_name TEXT,
                                PRIMARY KEY (user_id, badge_name))''')
            await conn.commit()
            await conn.execute('''CREATE TABLE IF NOT EXISTS cooldowns
                               (user_id INTEGER PRIMARY KEY,
                                beg_cooldown REAL DEFAULT 0)''')
            await conn.commit()
            
            await conn.execute('''CREATE TABLE IF NOT EXISTS inventory
                               (user_id INTEGER,
                                item_id TEXT,
                                quantity INTEGER,
                                PRIMARY KEY (user_id, item_id))''')
            await conn.commit()
            
            await conn.execute('''CREATE TABLE IF NOT EXISTS shop_items
                               (id TEXT PRIMARY KEY,
                                name TEXT,
                                price INTEGER)''')
            await conn.commit()
            
            await conn.execute('''CREATE TABLE IF NOT EXISTS currencylog
                               (user_id INTEGER,
                                action TEXT,
                                amount INTEGER,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            await conn.commit()
            await conn.execute('''CREATE TABLE IF NOT EXISTS stock_price
                            (item_id TEXT PRIMARY KEY,
                                price INTEGER)''')
            await conn.commit()
            await conn.execute("INSERT OR IGNORE INTO stock_price (item_id, price) VALUES (?, ?)", ('stock', 100000))
            await conn.commit()

            await conn.execute('''CREATE TABLE IF NOT EXISTS boosts
                               (user_id INTEGER PRIMARY KEY,
                                boost_factor INTEGER,
                                expiration_time INTEGER)''')
            await conn.commit()

            for item_id, item_data in shop_items.items():
                await conn.execute("INSERT OR REPLACE INTO shop_items (id, name, price) VALUES (?, ?, ?)", 
                                (item_id, item_data['name'], item_data['price']))
            await conn.commit()

def load_non_anonymous_users():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as file:
        return json.load(file)


def save_non_anonymous_users(users):
    with open(JSON_FILE, 'w') as file:
        json.dump(users, file)

non_anonymous_users = load_non_anonymous_users()
LOTTERY_CHANNEL_ID = 56555
try:
    with open('lottery.json', 'r') as f:
        lottery_data = json.load(f)
except FileNotFoundError:
    lottery_data = {
        'tickets': {},
        'pool': 100000,
        'end_time': None,
    }
else:
    
    lottery_data.setdefault('tickets', {})
    lottery_data.setdefault('pool', 100000)
    lottery_data.setdefault('end_time', None)

async def lottery_command(message):
    if lottery_data['end_time'] is None:
        if is_command(message, 'lottery buy'):
            await buy_lottery_tickets(message)
        else:
            await message.channel.send("No lottery is running right now.\nUse .lottery buy 1 to start one.")
    else:
        time_left = lottery_data['end_time'] - time.time()
        if time_left <= 0:
            await end_lottery(message)
        else:
            total_tickets = sum(lottery_data['tickets'].values())
            user_id = message.author.id
            user_tickets = lottery_data['tickets'].get(user_id, 0)
            if is_command(message, 'lottery buy'):
                await buy_lottery_tickets(message)
            else:
                lottery_info = f"**Lottery**\nTotal tickets: {total_tickets:,}\nCurrent pool: {lottery_data['pool']:,}\nTime before lottery ends: {time_left:.0f} seconds\nYour tickets: {user_tickets:,}"
                await message.channel.send(lottery_info)

async def end_lottery(message):
    total_tickets = sum(lottery_data['tickets'].values())
    winner_ticket = random.randint(1, total_tickets)
    current_total = 0
    winner_id = None

    for user_id, tickets in lottery_data['tickets'].items():
        current_total += tickets
        if current_total >= winner_ticket:
            winner_id = user_id
            break

    winner = bot.get_user(winner_id) if winner_id else None
    winnings = lottery_data['pool']

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            if winner is not None:
                await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (winnings, winner_id))
            else:
                
                lottery_data['pool'] += winnings
            await conn.commit()

    if winner is not None:
        end_message = f"**Lottery ended**\nWinner: {winner.mention}\nAmount they won: {winnings:,}\nTotal tickets: {total_tickets:,}"
    else:
        end_message = f"**Lottery ended**\nWinner not found (user left the server or account was deleted).\nAmount added to the next lottery pool: {winnings:,}\nTotal tickets: {total_tickets:,}"

    await bot.get_channel(LOTTERY_CHANNEL_ID).send(end_message)

    lottery_data['end_time'] = None
    lottery_data['tickets'] = {}
    lottery_data['pool'] = 100000

    with open('lottery.json', 'w') as f:
        json.dump(lottery_data, f)

async def buy_lottery_tickets(message):
    try:
        amount = int(message.content.split()[2])
    except (IndexError, ValueError):
        await message.channel.send("Please provide a valid number of tickets to buy.")
        return

    user_id = message.author.id
    price = amount * 10000

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,))
            wallet = (await c.fetchone())[0]

    if wallet < price:
        await message.channel.send(f"You don't have enough coins to buy {amount} lottery tickets. You have {wallet:,} coins.")
        return

    await message.channel.send(f"Are you sure you would like to purchase {amount} lottery tickets for {price:,} coins? 'yes' to accept, 'no' to cancel")

    def check(m):
        return m.author == message.author and m.channel == message.channel and m.content.lower() in ['yes', 'no']

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await message.channel.send("Transaction timed out.")
        return

    if confirmation.content.lower() == 'no':
        await message.channel.send("Transaction canceled.")
        return

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (price, user_id))
            await conn.commit()

    if lottery_data['end_time'] is None:
        lottery_data['end_time'] = time.time() + 3600  
        lottery_data['tickets'] = {user_id: amount}
        lottery_data['pool'] += price
    else:
        lottery_data['tickets'][user_id] = lottery_data['tickets'].get(user_id, 0) + amount
        lottery_data['pool'] += price

    with open('lottery.json', 'w') as f:
        json.dump(lottery_data, f)

    await message.channel.send(f"You have purchased {amount} lottery tickets.")

@bot.event
async def on_ready():
    print(f'bots online')
    asyncio.create_task(setup_database())
    asyncio.create_task(update_stock_price())
    await start_cooldown_task()
    # ok mysql soon ts terrible

async def start_cooldown_task():
    global cooldown_task
    cooldown_task = asyncio.create_task(clear_search_cooldowns())

async def stop_cooldown_task():
    global cooldown_task
    if cooldown_task is not None:
        cooldown_task.cancel()
        try:
            await cooldown_task
        except asyncio.CancelledError:
            pass
        cooldown_task = None
   
def is_command(message, command_name):
    for prefix in PREFIXES:
        if message.content.startswith(prefix + command_name):
            return True
    return False

@bot.event
async def on_message(message):
    if message.guild is None or message.guild.id != 1247588506797084733:
        return

    if message.author.bot:
        return

    content = message.content.lower()
    if message.author == bot.user:
        return

    channel_id = message.channel.id 
    user_id = message.author.id
    if any(message.content.startswith(prefix) for prefix in PREFIXES):
        await update_experience(user_id, channel_id)

    if is_command(message, "adminleaderboard") and message.author.id in admin_user_ids:
        await adminleaderboard_command(message)

    elif is_command(message, "showdupers") and message.author.id in admin_user_ids:
        await showdupers_command(message)

    elif is_command(message, "bj ") or is_command(message, "blackjack "):
        await wmc_blackjack_command(message, bot)

    elif is_command(message, "bet"):
        await dice_command(message)

    elif is_command(message, "stake"):
        await stake_command(message)

    elif is_command(message, "lottery"):
        await lottery_command(message)

    elif is_command(message, "fish"):
        await fish_command(message)

    elif is_command(message, "hunt"):
        await hunt_command(message)

    elif is_command(message, "use"):
        await use_command(message)

    elif is_command(message, "profile"):
        await profile_command(message, user_id)

    elif is_command(message, "progress"):
        await progress_command(message)

    elif is_command(message, "currencylog"):
        await currencylog_command(message)

    elif is_command(message, "remove") and message.author.id in admin_user_ids:
        await remove_command(message)

    elif is_command(message, "setlevel") and message.author.id in admin_user_ids:
        await setlevel_command(message)

    elif is_command(message, "antisun") and message.author.id in admin_user_ids:
        await antisun_command(message)

    elif is_command(message, "wipe") and message.author.id in admin_user_ids:
        await wipe_command(message)

    elif is_command(message, "add ") and message.author.id in admin_user_ids:
        await add_command(message)

    elif is_command(message, "restart") and message.author.id in admin_user_ids:
        await restart_command(message)

    elif is_command(message, "fight"):
        await fight_command(message)

    elif is_command(message, "item "):
        await item_command(message)

    elif is_command(message, "roll "):
        await roll_command(message)

    elif is_command(message, "beg"):
        await beg_command(message)

    elif is_command(message, "bal"):
        await bal_command(message)

    elif is_command(message, "pay") or is_command(message, "give"):
        await pay_command(message)

    elif is_command(message, "shop"):
        await shop_command(message)

    elif is_command(message, "buy"):
        await buy_command(message)

    elif is_command(message, "sell"):
        await sell_command(message)

    elif is_command(message, "inv") or is_command(message, "inventory"):
        await inventory_command(message)

    elif is_command(message, "fetch"):
        await fetch_command(message)

    elif is_command(message, "search"):
        await search_command(message)

    elif is_command(message, "leaderboard") or is_command(message, "lb"):
        await leaderboard_command(message)

    elif is_command(message, "itemleaderboard") or is_command(message, "itemlb"):
        await itemleaderboard_command(message)
        
    elif is_command(message, "help"):
        await help_command(message)

    elif is_command(message, "loottable"):
        await loottable_command(message)


async def restart_command(message):
    try:
        script_path = os.path.abspath(__file__)
        subprocess.Popen(["python3", script_path])
        await message.channel.send("Restarting the script...")
        os._exit(0)
    except Exception as e:
        await message.channel.send(f"Error restarting the script: {str(e)}")
        
async def update_experience(user_id, channel_id):
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("SELECT level, experience FROM levels WHERE user_id = ?", (user_id,))
            result = await c.fetchone()

            if result is None:
                await c.execute("INSERT INTO levels (user_id, level, experience, rebirth_level) VALUES (?, ?, ?, ?)", (user_id, 1, 1, 0))
                level = 1
                experience = 1
            else:
                level, experience = result

                
                await c.execute("SELECT boost_factor FROM boosts WHERE user_id = ?", (user_id,))
                boost_result = await c.fetchone()

                if boost_result is not None:
                    boost_factor = boost_result[0]
                    experience += boost_factor
                else:
                    experience += 1

            
            next_level_experience = level * level * 10 + level * 10 + 10

            if experience >= next_level_experience:
                level += 1
                experience = experience - next_level_experience
                await level_up_rewards(user_id, level, channel_id)

            await c.execute("UPDATE levels SET level = ?, experience = ? WHERE user_id = ?", (level, experience, user_id))
            await conn.commit()

async def setlevel_command(message):
    
    if len(message.content.split()) != 3:
        await message.channel.send("Invalid command format. Use `setlevel <userid> <level>`.")
        return

    
    _, user_id, new_level = message.content.split()
    
    try:
        user_id = int(user_id)
        new_level = int(new_level)
    except ValueError:
        await message.channel.send("User ID and level must be integers.")
        return

    
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE levels SET level = ? WHERE user_id = ?", (new_level, user_id))
            await conn.commit()

    await message.channel.send(f"Set level of user {user_id} to {new_level}.")
    
async def profile_command(message, user_id=None):
    if user_id is None:
        user_id = message.author.id
    username = message.author.name if user_id == message.author.id else (await bot.fetch_user(user_id)).name

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            
            await c.execute("SELECT level, experience, rebirth_level FROM levels WHERE user_id = ?", (user_id,))
            result = await c.fetchone()

            if result is None:
                
                await c.execute("INSERT INTO levels (user_id, level, experience, rebirth_level) VALUES (?, ?, ?, ?)", (user_id, 0, 0, 0))
                await conn.commit()
                level = 0
                experience = 0
                rebirth_level = 0
            else:
                level, experience, rebirth_level = result

            
            next_level_experience = level * level * 10 + level * 10 + 10

            
            await c.execute("SELECT badge_name FROM badges WHERE user_id = ?", (user_id,))
            badges = [row[0] for row in await c.fetchall()]

            
            await c.execute("""
                SELECT
                    wallet,
                    COALESCE(
                        (SELECT SUM(CASE WHEN inventory.item_id = 'stock' THEN (SELECT price FROM stock_price WHERE item_id = 'stock') * quantity ELSE price * quantity END)
                         FROM inventory
                         JOIN shop_items ON inventory.item_id = shop_items.id
                         WHERE inventory.user_id = ?),
                        0
                    ) AS inventory_worth
                FROM balances
                WHERE user_id = ?
            """, (user_id, user_id))
            result = await c.fetchone()

            if result is None:
                wallet = 0
                inventory_worth = 0
            else:
                wallet, inventory_worth = result

            net_worth = wallet + inventory_worth

            
            if net_worth >= 1000000000:
                if 'Platinum Godzilla' not in badges:
                    await c.execute("INSERT INTO badges (user_id, badge_name) VALUES (?, ?)", (user_id, 'Platinum Godzilla'))
                    await conn.commit()
                    badges.append('Platinum Godzilla')
            elif net_worth >= 250000000:
                if 'Godzilla' not in badges:
                    await c.execute("INSERT INTO badges (user_id, badge_name) VALUES (?, ?)", (user_id, 'Godzilla'))
                    await conn.commit()
                    badges.append('Godzilla')
            else:
                if 'Platinum Godzilla' in badges:
                    await c.execute("DELETE FROM badges WHERE user_id = ? AND badge_name = ?", (user_id, 'Platinum Godzilla'))
                    await conn.commit()
                    badges.remove('Platinum Godzilla')
                if 'Godzilla' in badges:
                    await c.execute("DELETE FROM badges WHERE user_id = ? AND badge_name = ?", (user_id, 'Godzilla'))
                    await conn.commit()
                    badges.remove('Godzilla')

            
            await c.execute("SELECT boost_factor, expiration_time FROM boosts WHERE user_id = ?", (user_id,))
            boost_result = await c.fetchone()

            if boost_result is not None:
                boost_factor, expiration_time = boost_result
                remaining_time = expiration_time - int(time.time())

                if remaining_time > 0:
                    hours, remainder = divmod(remaining_time, 3600)
                    minutes, _ = divmod(remainder, 60)
                    boost_status = f"Active Boost: {boost_factor}x level boost ({hours}h {minutes}m remaining)\n"
                else:
                    boost_status = ""
                    await c.execute("DELETE FROM boosts WHERE user_id = ?", (user_id,))
                    await conn.commit()
            else:
                boost_status = ""

            profile_message = f"**{username}**\n"
            profile_message += f"*Level:* `{level}`\n"
            profile_message += f"**Experience:** `{experience}/{next_level_experience}`\n"
            profile_message += f"**Rebirth Level:** `{rebirth_level}`\n"
            profile_message += boost_status + "\n"
            profile_message += "**Badges:**\n"
            for badge in badges:
                if badge == 'Godzilla':
                    profile_message += ":trophy: Godzilla\n"
                elif badge == 'Platinum Godzilla':
                    profile_message += "<:platinum:1249101423912685693> Platinum Godzilla\n"

            await send_message_with_retry(message.channel, profile_message)
            
async def level_up_rewards(user_id, new_level, channel_id):
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            if new_level == 1:
                await c.execute("UPDATE balances SET wallet = wallet + 50000 WHERE user_id = ?", (user_id,))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 50,000 coins!")
                return
            elif new_level == 3:
                await c.execute("UPDATE balances SET wallet = wallet + 100000 WHERE user_id = ?", (user_id,))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 100,000 coins!")
                return
            elif new_level == 5:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'grass', user_id, 'grass'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received a 🌱 Grass!")
                return
            elif new_level == 8:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'nicx', user_id, 'nicx'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received a 🤖 Nicx!")
                return
            elif new_level == 10:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 2)", (user_id, 'bestlootbox', user_id, 'bestlootbox'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 2x 🎁 Best Loot Box!")
                return
            elif new_level == 12:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 10)", (user_id, 'kuppy', user_id, 'kuppy'))
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 2)", (user_id, 'bestlootbox', user_id, 'bestlootbox'))
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'nicx', user_id, 'nicx'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 10x 🐨 Kuppy, 2x 🎁 Best Loot Box, and 1x 🤖 Nicx!")
                return
            elif new_level == 14:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'banana', user_id, 'banana'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received a 🍌 Banana!")
                return
            elif new_level == 15:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'godbox', user_id, 'godbox'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 1x 🎁 God Box!")
                return
            elif new_level == 17:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bolb', user_id, 'bolb'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received a 🔴 Bolb!")
                return
            elif new_level == 18:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 2)", (user_id, 'godbox', user_id, 'godbox'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received a 2x Godbox!")
                return
            elif new_level == 19:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'enicx', user_id, 'enicx'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received an 🤖 Enicx!")
                return
            elif new_level == 20:
                await c.execute("UPDATE balances SET wallet = wallet + 50000000 WHERE user_id = ?", (user_id,))
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bolb', user_id, 'bolb'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 50,000,000 coins and a 🔴 Bolb!")
                return
            elif new_level == 21:
                await c.execute("UPDATE balances SET wallet = wallet + 25000000 WHERE user_id = ?", (user_id,))
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bolb', user_id, 'bolb'))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received 25,000,000 coins and a :tren: Sunny's tren!")
                return
            elif new_level >= 22:
                reward_amount = int(150000000 * (1.2 ** (new_level - 21)))
                await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (reward_amount, user_id))
                await conn.commit()
                await send_message_with_retry(bot.get_channel(channel_id), f"<@{user_id}> has leveled up to level {new_level} and received {reward_amount:,} coins!")
                return
        
async def help_command(message):
    help_text = "**Economy**\n"
    help_text += "\n"
    help_text += "**Grinding**\n"
    help_text += "`beg` - Beg for money\n"
    help_text += "`search` - Search for money\n"
    help_text += "`fetch` - Fetch for money\n"
    help_text += "`stake` - Gamble for money\n"
    help_text += "`hunt` - Hunt for money\n"
    help_text += "`fish` - Fish for money\n"
    help_text += "**Gambling**\n"
    help_text += "`blackjack` or `bj` - Play Blackjack for money\n"
    help_text += "`bet` - gamble quickly for money\n"
    help_text += "`fight` - Wager someone your money\n"
    help_text += "**Utility**\n"
    help_text += "`pay` or `give` - Send someone your money\n"
    help_text += "`bal` - View your balance\n"
    help_text += "`item` - View an item\n"
    help_text += "`use` - Use an item\n"
    help_text += "`leaderboard` or `lb` - View the richest users\n"
    help_text += "`itemleaderboard` - View who has the most of an item\n"
    help_text += "`inventory` or `inv` - View your inventory\n"
    help_text += "`shop` - Check the shop\n"
    help_text += "`buy` - Buy an item\n"
    help_text += "`sell` - Sell an item\n"
    help_text += "`lottery (buy)` - Check/enter lottery\n"
    help_text += "`loottable` - View chances of getting items\n"
    help_text += "**Levelling**\n"
    help_text += "`progress` - View level progress\n"

    await send_message_with_retry(message.channel, help_text)

async def itemleaderboard_command(message):
    args = message.content.split()
    if len(args) < 2:
        await send_message_with_retry(message.channel, "Please provide an item ID.")
        return

    item_id = args[1].lower()  

    if item_id not in shop_items:
        await send_message_with_retry(message.channel, "Invalid item ID.")
        return

    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("""
            SELECT user_id, quantity
            FROM inventory
            WHERE item_id = ?
            ORDER BY quantity DESC
            LIMIT 5
        """, (item_id,)) as cursor:
            result = await cursor.fetchall()

    if len(result) == 0:
        await send_message_with_retry(message.channel, f"No users found holding the item '{shop_items[item_id]['name']}'.")
        return

    item_name = shop_items[item_id]['name']
    leaderboard_message = f"**Item Leaderboard (Top 5 Holders of {item_name})**\n"
    for i, (user_id, quantity) in enumerate(result, start=1):
        user = bot.get_user(user_id)
        if user is None:
            user_name = "Anonymous"
        else:
            user_name = user.name
        leaderboard_message += f"{i}. {user_name} - Quantity: {quantity}\n"

    await send_message_with_retry(message.channel, leaderboard_message)
    
async def loottable_command(message):
    if len(message.content.split()) < 2:
        await send_message_with_retry(message.channel, "Please provide a command. Use `loottable` followed by `search`, `fetch`, `stake`, or `fish`.")
        return

    command_name = message.content.split()[1].lower()

    if command_name == "search":
        loottable_message = "**Search Loot Table**\n"
        loottable_message += "`🌞 Sunny`: 5% chance from searching 'outside'\n"
        loottable_message += "`🧔 Mohamed ki beard`: 20% chance from searching 'mohamedhouse'\n"
        loottable_message += "`🎁 Legendary Loot Box`: 5% chance from searching 'mohamedhouse'\n"
        loottable_message += "`🎁 Rare Loot Box`: 20% chance from searching 'mountain'\n"
        loottable_message += "`🎁 Best Loot Box`: 1% chance from searching 'dog'\n"
        loottable_message += "`🐶 Kuppy`: 5% chance from searching 'dog'\n"
        loottable_message += "`🏝️ Grass`: 2% chance from searching 'grass'\n"
        loottable_message += "`🏰 Mohamed's Pyramid`: 2% chance from searching 'pyramid'\n"
        loottable_message += "`🃏 Nicx Crown`: 2% chance from searching 'pyramid'\n"
        loottable_message += "`🌞 Sunny`: 1% chance from searching 'gbroad'\n"
        loottable_message += "`🎁 Best Loot Box`: 1% chance from searching 'gbroad'\n"
        loottable_message += "`🃏 Nicx Crown`: 1% chance from searching 'gbroad'\n"
        loottable_message += "`💀 Death (lose half coins)`: 10% chance from searching 'delhi'\n"
        loottable_message += "`🌞 Sunny`: 10% chance from searching 'delhi'\n"
        loottable_message += "`👧 Deep's Egirl`: 30% chance from searching 'fighthub'\n"
        loottable_message += "`🧔 Mohamed ki beard`: 10% chance from searching 'fighthub'\n"
        loottable_message += "`🎁 Any Loot Box`: 1% chance from searching 'fighthub'\n"
    elif command_name == "fetch":
        loottable_message = "**Fetch Loot Table**\n"
        loottable_message += "`🦴 Bone`: 30% chance\n"
        loottable_message += "`🦺 Robert's Leash`: 15% chance\n"
        loottable_message += "`🥫 Dog Food`: 5% chance\n"
    elif command_name == "stake":
        loottable_message = "**Stake Loot Table**\n"
        loottable_message += "`🎁 Best Loot Box`: 1% chance\n"
        loottable_message += "`🎁 Legendary Loot Box`: 4% chance\n"
        loottable_message += "`🎁 Rare Loot Box`: 15% chance\n"
    elif command_name == "fish":
        loottable_message = "**Fish Loot Table**\n"
        loottable_message += "`🐠 Clownfish`: 30% chance\n"
        loottable_message += "`🐡 Pufferfish`: 25% chance\n"
        loottable_message += "`🐟 Trout`: 20% chance\n"
        loottable_message += "`🐢 Sea Turtle`: 10% chance\n"
        loottable_message += "`🐠 Sailfish`: 7% chance\n"
        loottable_message += "`🦈 Shark`: 5% chance\n"
        loottable_message += "`🐬 Dolphin`: 2.5% chance\n"
        loottable_message += "`🐋 Blue Whale`: 0.25% chance\n"
    else:
        await send_message_with_retry(message.channel, "Invalid command. Use `loottable` followed by `search`, `fetch`, `stake`, or `fish`.")
        return

    await send_message_with_retry(message.channel, loottable_message)

async def item_command(message):
    if len(message.content.split()) < 2:
        await send_message_with_retry(message.channel, "Please provide an item ID.")
        return

    item_id = message.content.split()[1]
    if item_id not in shop_items:
        await send_message_with_retry(message.channel, "Invalid item ID.")
        return

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            
            user_id = message.author.id

            await c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            row = await c.fetchone()
            quantity = row[0] if row else 0

            await update_shop_items()
            item = shop_items[item_id]
            total_worth = quantity * item['price']
            item_message = f"**Item**\n{item['name']} `{item['id']}`\nPrice: **`⏣ {item['price']:,}`**\nSellable? `{'yes' if item.get('sellable', True) else 'no'}`\nBuyable? `{'yes' if item.get('buyable', True) else 'no'}`\nYou own: `{quantity}`\nWorth: `⏣ {total_worth:,}`"

            if item_id == 'rarelootbox':
                item_message += "\n\n**When used:**\n- 50% Chance of nothing\n- 30% Chance of Mohamed ki beard\n- 15% Chance of Sarthak\n- 5% Chance of Doggy"
            elif item_id == 'legendarylootbox':
                item_message += "\n\n**When used:**\n- 50% Chance of Sarthak\n- 30% Chance of Nothing\n- 15% Chance of Sunny\n- 5% Chance of SKULL SKELETON"
            elif item_id == 'bestlootbox':
                item_message += "\n\n**When used:**\n- 30% Chance of SKULL SKELETON\n- 20% Chance of nothing\n- 20% Chance of x2 bestlootbox\n- 10% Chance of Xily ka banana\n- 9% Chance of Mohamed ki beard\n- 1% Chance of bolb"
            elif item_id == 'banana':
                item_message += "\n\n**When used:**\n- Notifies xily u ate his bana (Item not consumed on use)"
            elif item_id == 'leash':
                item_message += "\n\n**When used:**\n- Times out Robert for 5 minutes. Item consumed on use"
            elif item_id == 'kuppy':
                item_message += "\n\n**When used:**\n- Mention a user to timeout them for 5 minutes. Item consumed on use"
            elif item_id == 'stock':
                item_message += "\n\n**When used:**\n- Price changes every 2-5 minutes, maximum is +- 30k. if it goes to 0 all stocks get deleted."
            elif item_id == 'nicx':
                item_message += "\n\n**When used:**\n- 1% Chance of transforming into an Enchanted Nicx Crown. 99% Chance of being consumed without transforming."

            await send_message_with_retry(message.channel, item_message)
            
async def wipe_command(message):


    if len(message.content.split()) < 2:
        await send_message_with_retry(message.channel, "Please provide a user ID.")
        return

    try:
        user_id = int(message.content.split()[1])
    except ValueError:
        await send_message_with_retry(message.channel, "Invalid user ID. Please provide a valid integer.")
        return

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
            await c.execute("UPDATE balances SET wallet = 0, bank = 0, inventory = 0, net_worth = 0 WHERE user_id = ?", (user_id,))
            await conn.commit()

    await send_message_with_retry(message.channel, f"Wiped user with ID {user_id}.")

async def adminleaderboard_command(message):
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("""
                SELECT user_id, wallet + COALESCE((
                    SELECT SUM(price * quantity) 
                    FROM inventory 
                    JOIN shop_items ON inventory.item_id = shop_items.id 
                    WHERE inventory.user_id = balances.user_id), 0) AS net_worth 
                FROM balances 
                ORDER BY net_worth DESC 
                LIMIT 10
            """)
            result = await c.fetchall()

            if len(result) == 0:
                await send_message_with_retry(message.channel, "No users found on the leaderboard.")
                return

            leaderboard_message = "**Admin Leaderboard (Top 10 Richest Users)**\n"
            for i, (user_id, net_worth) in enumerate(result, start=1):
                user = bot.get_user(user_id)
                if user:
                    leaderboard_message += f"{i}. {user.name} - Net Worth: ⏣ {net_worth:,}\n"
                else:
                    leaderboard_message += f"{i}. Unknown User - Net Worth: ⏣ {net_worth:,}\n"

            await send_message_with_retry(message.channel, leaderboard_message)

async def beg_command(message):
    author = message.author
    current_time = asyncio.get_event_loop().time()

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            
            await c.execute("SELECT beg_cooldown FROM cooldowns WHERE user_id = ?", (author.id,))
            result = await c.fetchone()

            if result is not None:
                beg_cooldown = result[0]
                if current_time < beg_cooldown:
                    remaining_time = int(beg_cooldown - current_time)
                    await message.channel.send(f"{author.mention}, you can use this command again in {remaining_time} seconds.")
                    return

            
            await c.execute("INSERT OR REPLACE INTO cooldowns (user_id, beg_cooldown) VALUES (?, ?)", (author.id, current_time + 60))
            await conn.commit()

            
            await c.execute("SELECT * FROM balances WHERE user_id = ?", (author.id,))
            result = await c.fetchone()

            if result is None:
                
                await c.execute("INSERT INTO balances (user_id) VALUES (?)", (author.id,))
                await conn.commit()

            if random.random() < 0.75:
                amount = random.randint(1000, 10000)
                owner = random.choice(owners)
                await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (amount, author.id))
                await conn.commit()
                await message.channel.send(f"{author.mention}, you begged so hard and your owner {owner} gave you {amount} coins!")
            else:
                await message.channel.send(f"{author.mention}, your begging attempt was unsuccessful. Better luck next time!")

async def progress_command(message):
    user_id = message.author.id
    username = message.author.name
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("SELECT level, experience FROM levels WHERE user_id = ?", (user_id,))
            result = await c.fetchone()

            if result is None:
                await c.execute("INSERT INTO levels (user_id, level, experience) VALUES (?, ?, ?)", (user_id, 1, 0))
                await conn.commit()
                level = 1
                experience = 0
            else:
                level, experience = result

            
            next_level_experience = level * level * 10 + level * 10 + 10

            progress_message = f"**{username}'s Progress**\n"
            progress_message += f"*Level:* `{level}`\n"
            progress_message += f"**Experience:** `{experience}/{next_level_experience}`\n\n"
            progress_message += "**Level Rewards:**\n"
            progress_message += "- Level 1: 50,000 coins\n"
            progress_message += "- Level 3: 100,000 coins\n"
            progress_message += "- Level 5: :island: Grass\n"
            progress_message += "- Level 8: <a:nicxcrown:1247935115900751933> nicx crown\n"
            progress_message += "- Level 10: 2x 🎁 Best Loot Box\n"
            progress_message += "- Level 12: 10x :dog2: Kuppy, 2x 🎁 Best Loot Box, 1x <a:nicxcrown:1247935115900751933> nicx crown\n"
            progress_message += "- Level 14: 🍌 Banana\n"
            progress_message += "- Level 15: <:godbox:1247980941310427157> God Box\n"
            progress_message += "- Level 17: 🔴 Bolb\n"
            progress_message += "- Level 18: 2x <:godbox:1247980941310427157> God Box\n"
            progress_message += "- Level 19: <a:enicxcrown:1247935144489386094> eNicx\n"
            progress_message += "- Level 20: 50,000,000 coins, 🔴 Bolb\n"
            progress_message += "- Level 21: 25,000,000 coins, <:tren:1249596585961324545> Sunny's tren\n"
            progress_message += "- Level 22+: Increasing coins (starting from 150,000,000 and increasing by 1.2x each level)\n"

            await send_message_with_retry(message.channel, progress_message)            
async def bal_command(message):
    if len(message.mentions) > 0:
        
        user = message.mentions[0]
    else:
        
        user = message.author

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            
            await c.execute("""
                SELECT 
                    wallet, 
                    COALESCE(
                        (SELECT SUM(CASE WHEN inventory.item_id = 'stock' THEN (SELECT price FROM stock_price WHERE item_id = 'stock') * quantity ELSE price * quantity END)
                         FROM inventory 
                         JOIN shop_items ON inventory.item_id = shop_items.id
                         WHERE inventory.user_id = ?),
                        0
                    ) AS inventory_worth
                FROM balances
                WHERE user_id = ?
            """, (user.id, user.id))
            result = await c.fetchone()

            if result is None:
                
                await c.execute("INSERT INTO balances (user_id) VALUES (?)", (user.id,))
                await conn.commit()
                wallet, inventory_worth = 0, 0
            else:
                wallet, inventory_worth = result

            net_worth = wallet + inventory_worth

            await message.channel.send(f"**{user.name}'s balance**\n"
                                       f"**Wallet**: ⏣ {wallet:,}\n"
                                       f"**Bank**: ⏣ 0\n"
                                       f"**Inventory**: ⏣ {inventory_worth:,}\n"
                                       f"**Net Worth**: ⏣ {net_worth:,}")

async def shop_command(message):
    await update_shop_items()
    shop_message = "**Weltanschauungen ki shop**\n"
    for item in shop_items.values():
        if item.get('buyable', True):
            shop_message += f"{item['name']} | ⏣ {item['price']:,} | `{item['id']}`\n"
    await send_message_with_retry(message.channel, shop_message)

async def fish_command(message):
    user_id = message.author.id
    current_time = time.time()

    
    if user_id in fish_cooldowns:
        time_since_last_command = current_time - fish_cooldowns[user_id]
        if time_since_last_command < 60:
            remaining_time = 60 - time_since_last_command
            await send_message_with_retry(message.channel, f"You need to wait {remaining_time:.0f} seconds before using this command again.")
            return

    
    fish_cooldowns[user_id] = current_time

    fish_types = [
        ('🐠 Clownfish', 2, 4, 0.3),
        ('🐡 Pufferfish', 4, 8, 0.25),
        ('🐟 Trout', 20, 30, 0.2),
        ('🐢 Sea Turtle', 24, 48, 0.1),
        ('🐠 Sailfish', 60, 84, 0.07),
        ('🦈 Shark', 72, 240, 0.05),
        ('🐬 Dolphin', 72, 144, 0.025),
        ('🐋 Blue Whale', 840, 1080, 0.0025)
    ]

    base_price = 100
    growth_factor = 1.0073

    cumulative_probabilities = [sum(fish[3] for fish in fish_types[:i+1]) for i in range(len(fish_types))]
    random_value = random.random()

    for i, cumulative_probability in enumerate(cumulative_probabilities):
        if random_value <= cumulative_probability:
            fish_type, min_size, max_size, _ = fish_types[i]
            fish_size = random.randint(min_size, max_size)
            fish_value = round(base_price * (growth_factor ** (fish_size - 1)))
            break
    else:
        fish_message = "You didn't catch anything. Better luck next time!"
        await send_message_with_retry(message.channel, fish_message)
        return

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (fish_value, user_id))
            await conn.commit()

            fish_message = f"You caught a {fish_type} ({fish_size} inches) and earned {fish_value:,} coins!"

    await send_message_with_retry(message.channel, fish_message)

async def hunt_command(message):
    user_id = message.author.id
    current_time = time.time()

    
    if user_id in hunt_cooldowns:
        time_since_last_command = current_time - hunt_cooldowns[user_id]
        if time_since_last_command < 60:
            remaining_time = 60 - time_since_last_command
            await send_message_with_retry(message.channel, f"You need to wait {remaining_time:.0f} seconds before using this command again.")
            return

    
    hunt_cooldowns[user_id] = current_time

    coins_gained = random.randint(500, 5000)

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (coins_gained, user_id))
            await conn.commit()

            hunt_message = f"You went hunting and earned {coins_gained:,} coins!"

            loot_random = random.randint(1, 300)
            if 1 <= loot_random <= 20:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'duck', user_id, 'duck'))
                await conn.commit()
                hunt_message += "\nYou also found a :swan: wise duck!"
            elif loot_random == 21:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'cat', user_id, 'cat'))
                await conn.commit()
                hunt_message += "\nYou also found a <a:weltan:1249106180677308466> weltan's cat!"
            elif 22 <= loot_random <= 30:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'temple', user_id, 'temple'))
                await conn.commit()
                hunt_message += "\nYou also found a :hindu_temple: sid's temple!"
            elif 31 <= loot_random <= 40:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'legendarylootbox', user_id, 'legendarylootbox'))
                await conn.commit()
                hunt_message += "\nYou also found a :gift: Legendary loot box!"

    await send_message_with_retry(message.channel, hunt_message)
    
async def stake_command(message):
    user_id = message.author.id
    current_time = time.time()

    
    if user_id in stake_cooldowns:
        time_since_last_command = current_time - stake_cooldowns[user_id]
        if time_since_last_command < 150:
            remaining_time = 150 - time_since_last_command
            await send_message_with_retry(message.channel, f"You need to wait {remaining_time:.0f} seconds before using this command again.")
            return

    
    stake_cooldowns[user_id] = current_time

    coins_gained = random.randint(500, 5000)

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (coins_gained, user_id))
            await conn.commit()

            stake_message = f"You gambled on stake.com all night and made {coins_gained:,} coins!"

            loot_random = random.random()
            if loot_random < 0.01:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bestlootbox', user_id, 'bestlootbox'))
                await conn.commit()
                stake_message += "\nYou also found a :gift: Best loot box!"
            elif loot_random < 0.05:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'legendarylootbox', user_id, 'legendarylootbox'))
                await conn.commit()
                stake_message += "\nYou also found a :gift: Legendary loot box!"
            elif loot_random < 0.2:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'rarelootbox', user_id, 'rarelootbox'))
                await conn.commit()
                stake_message += "\nYou also found a :gift: Rare loot box!"

    await send_message_with_retry(message.channel, stake_message)

async def use_command(message):
    user_id = message.author.id

    if len(message.content.split()) < 2:
        await send_message_with_retry(message.channel, "Please provide an item to use.")
        return

    item_id = message.content.split()[1]
    if len(message.content.split()) > 2:
        try:
            quantity = int(message.content.split()[2])
        except ValueError:
            await send_message_with_retry(message.channel, "Invalid quantity.")
            return
    else:
        quantity = 1

    if item_id not in shop_items:
        await send_message_with_retry(message.channel, f"The item `{item_id}` does not exist in the shop.")
        return

    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id)) as cursor:
            result = await cursor.fetchone()

        if result is None or result[0] < quantity:
            await send_message_with_retry(message.channel, f"You don't have enough of the item `{item_id}` in your inventory.")
            return

        if item_id in ['rarelootbox', 'legendarylootbox', 'bestlootbox']:
            
            found_items = {}
            for _ in range(quantity):
                if item_id == 'rarelootbox':
                    chance = random.random()
                    if chance < 0.5:
                        pass
                    elif chance < 0.8:
                        found_items['beard'] = found_items.get('beard', 0) + 1
                    elif chance < 0.95:
                        found_items['sarthak'] = found_items.get('sarthak', 0) + 1
                    else:
                        found_items['dog'] = found_items.get('dog', 0) + 1
                elif item_id == 'legendarylootbox':
                    chance = random.random()
                    if chance < 0.5:
                        found_items['sarthak'] = found_items.get('sarthak', 0) + 1
                    elif chance < 0.8:
                        pass
                    elif chance < 0.95:
                        found_items['sun'] = found_items.get('sun', 0) + 1
                    else:
                        found_items['skull'] = found_items.get('skull', 0) + 1
                elif item_id == 'bestlootbox':
                    chance = random.random()
                    if chance < 0.3:
                        found_items['skull'] = found_items.get('skull', 0) + 1
                    elif chance < 0.5:
                        pass
                    elif chance < 0.7:
                        found_items['bestlootbox'] = found_items.get('bestlootbox', 0) + 2
                    elif chance < 0.8:
                        found_items['banana'] = found_items.get('banana', 0) + 1
                    elif chance < 0.89:
                        found_items['beard'] = found_items.get('beard', 0) + 1
                    else:
                        found_items['bolb'] = found_items.get('bolb', 0) + 1

            message_text = f"You opened {quantity}x {item_id} and found:\n"
            for item, count in found_items.items():
                message_text += f"{count}x {item}\n"
                await db.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (user_id, item, user_id, item, count))
            if not found_items:
                message_text += "Nothing\n"
            await send_message_with_retry(message.channel, message_text)
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        elif item_id == 'tren':
            boost_duration = 48 * 60 * 60
            expiration_time = int(time.time()) + boost_duration

            async with db.execute("SELECT * FROM boosts WHERE user_id = ?", (user_id,)) as cursor:
                existing_boost = await cursor.fetchone()

            if existing_boost is None:
                await db.execute("INSERT INTO boosts (user_id, boost_factor, expiration_time) VALUES (?, ?, ?)", (user_id, 2, expiration_time))
            else:
                await db.execute("UPDATE boosts SET boost_factor = ?, expiration_time = ? WHERE user_id = ?", (2, expiration_time, user_id))

            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

            remaining_time = expiration_time - int(time.time())
            hours, remainder = divmod(remaining_time, 3600)
            minutes, _ = divmod(remainder, 60)

            await send_message_with_retry(message.channel, f"You used {quantity}x {item_id} and received a 2x level boost for {hours} hours and {minutes} minutes")

        elif item_id == 'godbox':
            
            found_items = {}
            for _ in range(quantity):
                chance = random.random()
                if chance < 0.5:
                    pass
                else:
                    found_items['enicx'] = found_items.get('enicx', 0) + 1

            message_text = f"You opened {quantity}x {item_id} and found:\n"
            for item, count in found_items.items():
                message_text += f"{count}x {item}\n"
                await db.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (user_id, item, user_id, item, count))
            if not found_items:
                message_text += "Nothing LOOOOL @everyone look at this dog\n"
            await send_message_with_retry(message.channel, message_text)
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        elif item_id == 'banana':
            
            target_user_id = 884830854289973288
            target_user = bot.get_user(target_user_id)
            await target_user.send(f"ate yo banana {quantity} times")
            await send_message_with_retry(message.channel, f"You used {quantity} banana(s) and {target_user.mention} now knows")
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        elif item_id == 'leash':
            
            target_user_id = 841667029165015081
            target_user = bot.get_user(target_user_id)
            guild = message.guild
            member = guild.get_member(target_user_id)
            await member.timeout(datetime.timedelta(minutes=5 * quantity), reason="Leashed by user")
            await send_message_with_retry(message.channel, f"You leashed {target_user.mention} {quantity} time(s) and they are now muted for {5 * quantity} minutes")
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        elif item_id == 'kuppy':
            
            if len(message.mentions) == 0:
                await send_message_with_retry(message.channel, "ping someone to kuppy")
                return

            target_user = message.mentions[0]
            guild = message.guild
            member = guild.get_member(target_user.id)
            await member.timeout(datetime.timedelta(minutes=5 * quantity), reason="Bitten by Kuppy")
            await send_message_with_retry(message.channel, f"{target_user.mention} was bitten by kuppy {quantity} time(s) and now needs surgery for {5 * quantity} minutes.")
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        elif item_id == 'nicx':
            
            found_items = {}
            for _ in range(quantity):
                number = random.randint(1, 100)
                if number == 1 or number == 100:
                    found_items['enicx'] = found_items.get('enicx', 0) + 1
                else:
                    pass

            message_text = f"You used {quantity}x {item_id}:\n"
            for item, count in found_items.items():
                message_text += f"{count}x {item} (wtf ur badass nicx crown is now enchanted)\n"
                await db.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (user_id, item, user_id, item, count))
            if not found_items:
                message_text += f"{quantity}x {item_id} (gg lost nicx crown)\n"
            await send_message_with_retry(message.channel, message_text)
            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
            await db.commit()

        else:
            await send_message_with_retry(message.channel, "This item has no use.")

async def buy_command(message):
    user_id = message.author.id

    if user_id in ongoing_transactions:
        await send_message_with_retry(message.channel, f"{message.author.mention}, you have an ongoing transaction. Please wait until it is completed.")
        return

    ongoing_transactions[user_id] = True

    try:
        if user_id in fight_requests:
            await send_message_with_retry(message.channel, "You cannot buy items while in a fight.")
            return

        args = message.content.split()
        if len(args) < 3:
            await send_message_with_retry(message.channel, "Please provide an item ID and amount to buy.")
            return

        item_id = args[1]
        try:
            amount = int(args[2])
        except ValueError:
            await send_message_with_retry(message.channel, "Please provide a valid number for the amount.")
            return

        if amount <= 0:
            await send_message_with_retry(message.channel, "Amount must be greater than zero.")
            return

        if item_id not in shop_items:
            await send_message_with_retry(message.channel, "Invalid item ID.")
            return

        await update_shop_items()
        item = shop_items[item_id]

        
        if not item.get('buyable', True):
            await send_message_with_retry(message.channel, f"{message.author.mention}, the item {item['name']} is not buyable.")
            return

        
        if item_id == 'stock' and item['price'] < 10000:
            await send_message_with_retry(message.channel, f"{message.author.mention}, you can't buy stocks when they're this low.")
            return

        total_price = item['price'] * amount

        async with aiosqlite.connect('economy.db') as conn:
            async with conn.cursor() as c:
                
                await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,))
                result = await c.fetchone()
                if result is None or result[0] < total_price:
                    await send_message_with_retry(message.channel, f"{message.author.mention}, you don't have enough coins to buy {amount} {item['name']}(s)!")
                    return

                await send_message_with_retry(message.channel, f"{message.author.mention}, are you sure you want to buy {amount} {item['name']}(s) for ⏣ {total_price:,}? Type 'yes' to confirm or 'no' to cancel.")

                def check(msg):
                    return msg.author == message.author and msg.content.lower() in ['yes', 'no']

                try:
                    confirmation = await bot.wait_for('message', check=check, timeout=30)
                    if confirmation.content.lower() == 'no':
                        await send_message_with_retry(message.channel, f"{message.author.mention}, purchase cancelled.")
                        return
                except asyncio.TimeoutError:
                    await send_message_with_retry(message.channel, f"{message.author.mention}, purchase confirmation timed out.")
                    return

                
                await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,))
                result = await c.fetchone()
                if result is None or result[0] < total_price:
                    await send_message_with_retry(message.channel, f"{message.author.mention}, you don't have enough coins to buy {amount} {item['name']}(s)!")
                    return

                
                await c.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (total_price, user_id))

                
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (user_id, item_id, user_id, item_id, amount))
                await conn.commit()

                await send_message_with_retry(message.channel, f"{message.author.mention}, you have successfully purchased {amount} {item['name']}(s)!")
    finally:
        
        ongoing_transactions.pop(user_id, None)

async def sell_command(message):
    user_id = message.author.id

    if user_id in ongoing_transactions:
        await send_message_with_retry(message.channel, f"{message.author.mention}, you have an ongoing transaction. Please wait until it is completed.")
        return

    ongoing_transactions[user_id] = True

    try:
        args = message.content.split()
        if len(args) < 3:
            await send_message_with_retry(message.channel, "Please provide an item ID and amount to sell.")
            return

        item_id = args[1].lower()
        try:
            quantity = int(args[2])
        except ValueError:
            await send_message_with_retry(message.channel, "Please provide a valid number for the quantity.")
            return

        if quantity <= 0:
            await send_message_with_retry(message.channel, "Quantity must be greater than zero.")
            return

        async with aiosqlite.connect('economy.db') as conn:
            async with conn.cursor() as c:
                
                await c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
                result = await c.fetchone()

                if result is None or result[0] < quantity:
                    await send_message_with_retry(message.channel, "You don't have enough quantity of that item to sell.")
                    return

                await update_shop_items()
                item_price = shop_items[item_id]['price']
                total_price = item_price * quantity

                await send_message_with_retry(message.channel, f"Are you sure you want to sell {quantity} {shop_items[item_id]['name']} for {total_price:,} coins? Type 'yes' to confirm or 'no' to cancel.")

                def check(msg):
                    return msg.author == message.author and msg.content.lower() in ['yes', 'no']

                try:
                    confirmation = await bot.wait_for('message', check=check, timeout=30)
                    if confirmation.content.lower() == 'no':
                        await send_message_with_retry(message.channel, "Sale canceled.")
                        return
                except asyncio.TimeoutError:
                    await send_message_with_retry(message.channel, "Sale confirmation timed out.")
                    return

                
                await c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
                result = await c.fetchone()

                if result is None or result[0] < quantity:
                    await send_message_with_retry(message.channel, "You no longer have enough quantity of that item to sell. The sale has been canceled.")
                    return

                
                await c.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_id))
                await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (total_price, user_id))
                await conn.commit()

                await send_message_with_retry(message.channel, f"Successfully sold {quantity} {shop_items[item_id]['name']} for {total_price:,} coins!")
    finally:
        
        ongoing_transactions.pop(user_id, None)
        
async def update_stock_price():
    while True:
        try:
            async with aiosqlite.connect('economy.db') as conn:
                async with conn.cursor() as c:
                    await c.execute("SELECT price FROM stock_price WHERE item_id = ?", ('stock',))
                    current_price = await c.fetchone()
                    current_price = current_price[0] if current_price else 100000

                    price_change = random.randint(-30000, 30000)

                    new_price = current_price + price_change
                    new_price = max(new_price, 0)

                    print(f"Updating stock price: Current price: {current_price}, New price: {new_price}")  

                    await c.execute("UPDATE stock_price SET price = ? WHERE item_id = ?", (new_price, 'stock'))

                    if new_price == 0:
                        print("Stock price reached 0. Removing all stocks from inventories.")
                        await c.execute("DELETE FROM inventory WHERE item_id = ?", ('stock',))

                    await conn.commit()

                    
                    await c.execute("SELECT SUM(quantity) FROM inventory WHERE item_id = ?", ('stock',))
                    total_stocks = await c.fetchone()
                    total_stocks = total_stocks[0] if total_stocks[0] else 0
                    total_value = total_stocks * new_price

                    
                    webhook_url = "https://discord.com/api/webhooks/1249068086791901185/AdQ_9EfII8MCQtIyymPXUmAQEj17H5JyakTTFYFENvCDCeFjIS9GtJHuSXcP3MVFFb3L"
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "content": f"Stock updated: `{new_price:,}`\nStock amount: `{total_stocks:,}`\nStock value: `{total_value:,}`"
                        }
                        async with session.post(webhook_url, json=payload) as response:
                            if response.status != 204:
                                print(f"Failed to send message to webhook. Status code: {response.status}")

            await update_shop_items()
            sleep_duration = random.randint(60, 300)
            print(f"Sleeping for {sleep_duration} seconds before the next update.")
            await asyncio.sleep(sleep_duration)
        except Exception as e:
            print(f"An error occurred in update_stock_price: {str(e)}")

async def update_shop_items():
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("SELECT price FROM stock_price WHERE item_id = ?", ('stock',))
            stock_price = await c.fetchone()
            stock_price = stock_price[0] if stock_price else 100000
            shop_items['stock']['price'] = stock_price

async def fetch_command(message):
    user_id = message.author.id
    current_time = asyncio.get_event_loop().time()

    if user_id in fetch_cooldowns and current_time < fetch_cooldowns[user_id]:
        remaining_time = int(fetch_cooldowns[user_id] - current_time)
        minutes, seconds = divmod(remaining_time, 60)
        await send_message_with_retry(message.channel, f"{message.author.mention}, you can use the fetch command again in {minutes} minutes and {seconds} seconds.")
        return

    fetch_cooldowns[user_id] = current_time + 75  

    coins_found = random.randint(1000, 10000)

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (coins_found, user_id))
            await conn.commit()

            fetch_message = f"{message.author.mention}, you fetched like a good doggy and found ⏣ {coins_found:,}!"

            if random.random() < 0.3:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bone', user_id, 'bone'))
                await conn.commit()
                fetch_message += "\nYou also found a :bone: Bone!"
            elif random.random() < 0.15:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'leash', user_id, 'leash'))
                await conn.commit()
                fetch_message += "\nYou also found a :service_dog: Robert's Leash!"
            elif random.random() < 0.05:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'dogfood', user_id, 'dogfood'))
                await conn.commit()
                fetch_message += "\nYou also found a :canned_food: Dog Food!"

            await send_message_with_retry(message.channel, fetch_message)

async def inventory_command(message):
    if len(message.mentions) > 0:
        user = message.mentions[0]
    else:
        user = message.author

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("SELECT item_id, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (user.id,))
            inventory = await c.fetchall()

            if len(inventory) == 0:
                await send_message_with_retry(message.channel, f"{user.mention}'s inventory is empty.")
                return

            inventory_items = []
            total_value = 0
            for item_id, quantity in inventory:
                await update_shop_items()
                item = shop_items[item_id]
                item_value = item['price'] * quantity
                inventory_items.append((item['name'], quantity, item_value))
                total_value += item_value

            
            inventory_items.sort(key=lambda x: x[2], reverse=True)

            inventory_message = f"**{user.name}'s inventory**\n"
            for item_name, quantity, item_value in inventory_items:
                inventory_message += f"{item_name} | `{quantity}` | ⏣ {item_value:,}\n"
            inventory_message += f"\nTotal Value: ⏣ {total_value:,}"

            await send_message_with_retry(message.channel, inventory_message)

async def search_command(message):
    user_id = message.author.id
    current_time = asyncio.get_event_loop().time()
    if user_id in active_searches and active_searches[user_id]:
        await send_message_with_retry(message.channel, f"{message.author.mention}, you already have an ongoing search.")
        return
    if user_id in search_cooldowns and current_time < search_cooldowns[user_id]:
        remaining_time = int(search_cooldowns[user_id] - current_time)
        await send_message_with_retry(message.channel, f"{message.author.mention}, you can search again in {remaining_time} seconds.")
        return
    active_searches[user_id] = True
    search_locations = random.sample(['outside', 'mohamedhouse', 'mountain', 'street', 'dog', 'grass', 'pyramid', 'gbroad', 'delhi', 'fighthub'], 2)
    await send_message_with_retry(message.channel, "Where do you want to search?\n" + "\n".join([f"`{location}`" for location in search_locations]))
    def check(msg):
        return msg.author == message.author and msg.content.lower() in search_locations
    try:
        response = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await send_message_with_retry(message.channel, f"{message.author.mention}, search location selection timed out.")
        active_searches[user_id] = False
        return
    location = response.content.lower()
    search_cooldowns[user_id] = current_time + 60
    coins_found = random.randint(500, 5000)

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (coins_found, user_id))
            await conn.commit()

            search_message = f"{message.author.mention}, you searched {location} and found ⏣ {coins_found:,}!"

            if location == 'outside' and random.random() < 0.05:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'sun', user_id, 'sun'))
                await conn.commit()
                search_message += "\nYou also found a :sunny: Sunny!"
            elif location == 'mohamedhouse':
                if random.random() < 0.2:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'beard', user_id, 'beard'))
                    await conn.commit()
                    search_message += "\nYou also found a :man_beard: Mohamed ki beard!"
                elif random.random() < 0.05:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'legendarylootbox', user_id, 'legendarylootbox'))
                    await conn.commit()
                    search_message += "\nYou also found a :gift: Legendary Loot Box!"
                elif random.random() < 0.04:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'pyramid', user_id, 'pyramid'))
                    await conn.commit()
                    search_message += "\nYou also found mohameds pyramid!"
            elif location == 'mountain' and random.random() < 0.2:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'rarelootbox', user_id, 'rarelootbox'))
                await conn.commit()
                search_message += "\nYou also found a :gift: Rare Loot Box!"
            elif location == 'dog':
                if random.random() < 0.01:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bestlootbox', user_id, 'bestlootbox'))
                    await conn.commit()
                    search_message += "\nYou also found a :gift: Best Loot Box!"
                elif random.random() < 0.05:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'kuppy', user_id, 'kuppy'))
                    await conn.commit()
                    search_message += "\nYou also found a :dog2: Kuppy!"
            elif location == 'grass' and random.random() < 0.02:
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'grass', user_id, 'grass'))
                await conn.commit()
                search_message += "\nYou also found an :island: Grass!"
            elif location == 'pyramid':
                if random.random() < 0.02:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'pyramid', user_id, 'pyramid'))
                    await conn.commit()
                    search_message += "\nYou also found <:pyramid:1247931115763925082> Mohamed's Pyramid!"
                elif random.random() < 0.02:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'nicx', user_id, 'nicx'))
                    await conn.commit()
                    search_message += "\nYou also found a <a:nicxcrown:1247935115900751933> Nicx Crown!"
            elif location == 'gbroad':
                if random.random() < 0.01:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'sun', user_id, 'sun'))
                    await conn.commit()
                    search_message += "\nYou also found a :sunny: Sunny!"
                elif random.random() < 0.01:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'bestlootbox', user_id, 'bestlootbox'))
                    await conn.commit()
                    search_message += "\nYou also found a :gift: Best Loot Box!"
                elif random.random() < 0.01:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'nicx', user_id, 'nicx'))
                    await conn.commit()
                    search_message += "\nYou also found a <a:nicxcrown:1247935115900751933> Nicx Crown!"
            elif location == 'delhi':
                if random.random() < 0.1:
                    await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,))
                    wallet = (await c.fetchone())[0]
                    coins_lost = wallet // 2
                    await c.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (coins_lost, user_id))
                    await conn.commit()
                    search_message += f"\nYou got raped and died in delhi and lost ⏣ {coins_lost:,}"
                elif random.random() < 0.1:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'sun', user_id, 'sun'))
                    await conn.commit()
                    search_message += "\nYou also found a :sunny: Sunny!"
            elif location == 'fighthub':
                if random.random() < 0.3:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'deepsegirl', user_id, 'deepsegirl'))
                    await conn.commit()
                    search_message += "\nYou also found :girl: Deep's eGirl!"
                elif random.random() < 0.1:
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, 'beard', user_id, 'beard'))
                    await conn.commit()
                    search_message += "\nYou also found a :man_beard: Mohamed ki beard!"
                elif random.random() < 0.01:
                    loot_box = random.choice(['rarelootbox', 'legendarylootbox', 'bestlootbox'])
                    await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + 1)", (user_id, loot_box, user_id, loot_box))
                    await conn.commit()
                    search_message += f"\nYou also found a {shop_items[loot_box]['name']}!"

    await send_message_with_retry(message.channel, search_message)
    active_searches[user_id] = False

async def clear_search_cooldowns():
    while True:
        await asyncio.sleep(600)  
        search_cooldowns.clear()
        print("Search cooldowns cleared")

async def leaderboard_command(message):
    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("""
            SELECT user_id, wallet + COALESCE((
                SELECT SUM(price * quantity) 
                FROM inventory 
                JOIN shop_items ON inventory.item_id = shop_items.id 
                WHERE inventory.user_id = balances.user_id), 0) AS net_worth 
            FROM balances
            WHERE user_id NOT IN (SELECT user_id FROM balances WHERE user_id = 0 OR user_id = 1)  -- exclude anonymous users
            ORDER BY net_worth DESC 
            LIMIT 5
        """) as cursor:
            result = await cursor.fetchall()

    if len(result) == 0:
        await send_message_with_retry(message.channel, "No users found on the leaderboard.")
        return

    leaderboard_message = "**Leaderboard (Top 5 Richest Users)**\n"
    for i, (user_id, net_worth) in enumerate(result, start=1):
        user = bot.get_user(user_id)
        leaderboard_message += f"{i}. {user.name} - Net Worth: ⏣ {net_worth:,}\n"

    await send_message_with_retry(message.channel, leaderboard_message)
  
async def dehide_command(message):
    content = message.content.split()
    if len(content) != 2:
        await send_message_with_retry(message.channel, "Usage: !dehide <userid>")
        return

    try:
        user_id = int(content[1])
    except ValueError:
        await send_message_with_retry(message.channel, "Invalid user ID.")
        return

    if user_id not in non_anonymous_users:
        non_anonymous_users.append(user_id)
        save_non_anonymous_users(non_anonymous_users)
        await send_message_with_retry(message.channel, f"User ID {user_id} is no longer anonymous.")
    else:
        await send_message_with_retry(message.channel, f"User ID {user_id} is already not anonymous.")
  
async def fight_command(message):
    author = message.author
    if len(message.mentions) == 0:
        try:
            await message.channel.send("Please mention a user to fight.")
        except Exception as e:
            print(f"Error sending message: {e}")
        return

    opponent = message.mentions[0]
    if opponent == author:
        try:
            await message.channel.send("You cannot fight yourself!")
        except Exception as e:
            print(f"Error sending message: {e}")
        return

    if author.id in ongoing_fights or opponent.id in ongoing_fights:
        try:
            await message.channel.send("One of the users is already in a fight.")
        except Exception as e:
            print(f"Error sending message: {e}")
        return

    wager_amount = 0
    wager_item = None
    wager_quantity = 1

    if len(message.content.split()) > 2:
        try:
            wager_amount = int(message.content.split()[2])
            if wager_amount <= 0:
                await message.channel.send("Invalid wager amount. Please enter a positive integer.")
                return
        except ValueError:
            wager_item = message.content.split()[2]
            if wager_item not in shop_items:
                await message.channel.send("Invalid item ID for wager.")
                return

            if len(message.content.split()) > 3:
                try:
                    wager_quantity = int(message.content.split()[3])
                    if wager_quantity <= 0:
                        await message.channel.send("Invalid wager quantity. Please enter a positive integer.")
                        return
                except ValueError:
                    await message.channel.send("Invalid wager quantity. Please enter a valid integer.")
                    return

    
    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            if wager_item:
                await c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (author.id, wager_item))
                author_item_quantity = await c.fetchone()
                await c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (opponent.id, wager_item))
                opponent_item_quantity = await c.fetchone()

                if author_item_quantity is None or author_item_quantity[0] < wager_quantity:
                    await message.channel.send(f"{author.mention}, you don't have enough of the wagered item in your inventory!")
                    return

                if opponent_item_quantity is None or opponent_item_quantity[0] < wager_quantity:
                    await message.channel.send(f"{opponent.mention} doesn't have enough of the wagered item in their inventory!")
                    return

                
                await c.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (wager_quantity, author.id, wager_item))
                await c.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (wager_quantity, opponent.id, wager_item))
                await conn.commit()
            else:
                await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (author.id,))
                author_wallet = await c.fetchone()
                await c.execute("SELECT wallet FROM balances WHERE user_id = ?", (opponent.id,))
                opponent_wallet = await c.fetchone()

                if author_wallet is None or author_wallet[0] < wager_amount:
                    await message.channel.send(f"{author.mention}, you don't have enough coins for the wager!")
                    return

                if opponent_wallet is None or opponent_wallet[0] < wager_amount:
                    await message.channel.send(f"{opponent.mention} doesn't have enough coins for the wager!")
                    return

                
                await c.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (wager_amount, author.id))
                await c.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (wager_amount, opponent.id))
                await conn.commit()

    
    wager_pot = wager_amount * 2
    item_pot = wager_quantity * 2 if wager_item else 0

    try:
        fight_message = await message.channel.send(f"{author.mention} wants to fight you {opponent.mention}! Type 'accept' to accept the fight or 'decline' to decline{' with a wager of {:,} coins'.format(wager_amount) if wager_amount > 0 else ''}{' with a wager of {} {}'.format(wager_quantity, shop_items[wager_item]['name']) if wager_item else ''}.")
    except Exception as e:
        print(f"Error sending fight message: {e}")
        return

    fight_requests[author.id] = (opponent.id, wager_pot, wager_item, item_pot)
    fight_requests[opponent.id] = (author.id, wager_pot, wager_item, item_pot)

    def check(msg):
        return msg.author == opponent and msg.content.lower() in ['accept', 'decline']

    try:
        response = await bot.wait_for('message', check=check, timeout=30)
        if response.content.lower() == 'decline':
            try:
                await fight_message.edit(content=f"{opponent.mention} declined the fight.")
            except Exception as e:
                print(f"Error editing fight message: {e}")
            
            async with aiosqlite.connect('economy.db') as conn:
                async with conn.cursor() as c:
                    if wager_amount > 0:
                        await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_amount, author.id))
                        await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_amount, opponent.id))
                        await conn.commit()
                    if wager_item:
                        await c.execute("UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?", (wager_quantity, author.id, wager_item))
                        await c.execute("UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?", (wager_quantity, opponent.id, wager_item))
                        await conn.commit()
            del fight_requests[author.id]
            del fight_requests[opponent.id]
            return
    except asyncio.TimeoutError:
        try:
            await fight_message.edit(content=f"{opponent.mention} did not respond. Fight canceled.")
        except Exception as e:
            print(f"Error editing fight message: {e}")
        
        async with aiosqlite.connect('economy.db') as conn:
            async with conn.cursor() as c:
                if wager_amount > 0:
                    await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_amount, author.id))
                    await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_amount, opponent.id))
                    await conn.commit()
                if wager_item:
                    await c.execute("UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?", (wager_quantity, author.id, wager_item))
                    await c.execute("UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?", (wager_quantity, opponent.id, wager_item))
                    await conn.commit()
        del fight_requests[author.id]
        del fight_requests[opponent.id]
        return

    ongoing_fights[author.id] = opponent.id
    ongoing_fights[opponent.id] = author.id

    author_hp = 100
    opponent_hp = 100

    try:
        await fight_message.edit(content=f"**{author.mention}**'s hp: `{author_hp:,}`\n**{opponent.mention}**'s hp: `{opponent_hp:,}`\n**{author.mention}**, what do you want to do? `punch`, `kick`, `run`?\nType your choice out in chat as it's displayed.")
    except Exception as e:
        print(f"Error editing fight message: {e}")
        del ongoing_fights[author.id]
        del ongoing_fights[opponent.id]
        return

    turn = random.choice([author, opponent])

    while author_hp > 0 and opponent_hp > 0:
        def turn_check(msg):
            return msg.author == turn and msg.content.lower() in ['punch', 'kick', 'run']

        try:
            move = await bot.wait_for('message', check=turn_check, timeout=30)
        except asyncio.TimeoutError:
            try:
                await fight_message.edit(content=f"**{turn.mention}** took too long to make a move. **{turn.mention}** ran from the fight!")
            except Exception as e:
                print(f"Error editing fight message: {e}")
            winner = author if turn == opponent else opponent
            loser = opponent if winner == author else author
            async with aiosqlite.connect('economy.db') as conn:
                async with conn.cursor() as c:
                    if wager_pot > 0:
                        await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_pot, winner.id))
                        await conn.commit()
                        try:
                            await message.channel.send(f"{winner.mention} won the wager of {wager_pot:,} coins by default!")
                        except Exception as e:
                            print(f"Error sending message: {e}")
                    if item_pot > 0:
                        await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (winner.id, wager_item, winner.id, wager_item, item_pot))
                        await conn.commit()
                        try:
                            await message.channel.send(f"{winner.mention} won {item_pot} {shop_items[wager_item]['name']} by default!")
                        except Exception as e:
                            print(f"Error sending message: {e}")
            del ongoing_fights[author.id]
            del ongoing_fights[opponent.id]
            return

        attack_message = ""
        if move.content.lower() == 'punch':
            damage = random.randint(1, 15)
            if turn == author:
                opponent_hp -= damage
                attack_message = f"**{turn.mention}** punched **{opponent.mention}** for `{damage:,}` hp!\n**{opponent.mention}** is now at `{opponent_hp:,}` hp!"
            else:
                author_hp -= damage
                attack_message = f"**{turn.mention}** punched **{author.mention}** for `{damage:,}` hp!\n**{author.mention}** is now at `{author_hp:,}` hp!"
        elif move.content.lower() == 'kick':
            if random.random() < 0.6:
                damage = random.randint(5, 32)
                if turn == author:
                    opponent_hp -= damage
                    attack_message = f"**{turn.mention}** kicked **{opponent.mention}** for `{damage:,}` hp!\n**{opponent.mention}** is now at `{opponent_hp:,}` hp!"
                else:
                    author_hp -= damage
                    attack_message = f"**{turn.mention}** kicked **{author.mention}** for `{damage:,}` hp!\n**{author.mention}** is now at `{author_hp:,}` hp!"
            else:
                damage = random.randint(5, 15)
                if turn == author:
                    author_hp -= damage
                    attack_message = f"**{turn.mention}** fell and took `{damage:,}` damage!\n**{turn.mention}** is now at `{author_hp:,}` hp!"
                else:
                    opponent_hp -= damage
                    attack_message = f"**{turn.mention}** fell and took `{damage:,}` damage!\n**{turn.mention}** is now at `{opponent_hp:,}` hp!"
        elif move.content.lower() == 'run':
            try:
                await fight_message.edit(content=f"{turn.mention} has surrendered the fight. {turn.mention} is a coward!")
            except Exception as e:
                print(f"Error editing fight message: {e}")
            winner = author if turn == opponent else opponent
            loser = opponent if winner == author else author
            async with aiosqlite.connect('economy.db') as conn:
                async with conn.cursor() as c:
                    if wager_pot > 0:
                        await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_pot, winner.id))
                        await conn.commit()
                        try:
                            await message.channel.send(f"{winner.mention} won the wager of {wager_pot:,} coins!")
                        except Exception as e:
                            print(f"Error sending message: {e}")
                    if item_pot > 0:
                        await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (winner.id, wager_item, winner.id, wager_item, item_pot))
                        await conn.commit()
                        try:
                            await message.channel.send(f"{winner.mention} won {item_pot} {shop_items[wager_item]['name']}!")
                        except Exception as e:
                            print(f"Error sending message: {e}")
            del ongoing_fights[author.id]
            del ongoing_fights[opponent.id]
            return

        try:
            await fight_message.edit(content=f"{attack_message}\n**{opponent.mention if turn == author else author.mention}**, what do you want to do? `punch`, `kick`, `run`?\nType your choice out in chat as it's displayed.")
            await asyncio.sleep(1.5)  
        except Exception as e:
            print(f"Error editing fight message: {e}")
            del ongoing_fights[author.id]
            del ongoing_fights[opponent.id]
            return

        turn = opponent if turn == author else author

    winner = author if opponent_hp <= 0 else opponent
    loser = opponent if winner == author else author

    try:
        await message.channel.send(f"Holy heck! {winner.mention} just totally bamboozled {loser.mention}, winning with just `{author_hp:,}` hp left!" if winner == author else f"Holy heck! {winner.mention} just totally bamboozled {loser.mention}, winning with just `{opponent_hp:,}` hp left!")
    except Exception as e:
        print(f"Error sending message: {e}")

    async with aiosqlite.connect('economy.db') as conn:
        async with conn.cursor() as c:
            if wager_pot > 0:
                
                await c.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wager_pot, winner.id))
                await conn.commit()
                try:
                    await message.channel.send(f"{winner.mention} won the wager of {wager_pot:,} coins!")
                except Exception as e:
                    print(f"Error sending message: {e}")

            if item_pot > 0:
                
                await c.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (winner.id, wager_item, winner.id, wager_item, item_pot))
                await conn.commit()
                try:
                    await message.channel.send(f"{winner.mention} won {item_pot} {shop_items[wager_item]['name']}!")
                except Exception as e:
                    print(f"Error sending message: {e}")

    del ongoing_fights[opponent.id]
    del ongoing_fights[author.id]

async def roll_command(message):
    try:
        number_str = message.content[len(PREFIX) + len("roll "):]
        number = int(number_str)
        if number > 0:
            roll_result = random.randint(1, number)
            await message.channel.send(f"I roll a {roll_result}")
        else:
            await message.channel.send("Please provide a number greater than 0.")
    except ValueError:
        await message.channel.send("Please provide a valid number.")

async def pay_command(message):
    author = message.author

    if author.id in ongoing_fights:
        await send_message_with_retry(message.channel, "You cannot pay anyone while in a fight.")
        return

    if len(message.mentions) == 0:
        await send_message_with_retry(message.channel, "Please mention a user to pay.")
        return

    recipient = message.mentions[0]
    if recipient == author:
        await send_message_with_retry(message.channel, "You cannot pay yourself.")
        return

    try:
        amount = int(message.content.split()[-1])
        if amount <= 0:
            await send_message_with_retry(message.channel, "Invalid amount.")
            return
    except ValueError:
        await send_message_with_retry(message.channel, "Invalid amount.")
        return

    item_id = None
    item_name = None
    item_parts = message.content.split()
    if len(item_parts) > 3:
        potential_item_id = item_parts[-2].lower()
        if potential_item_id in shop_items:
            item_id = potential_item_id
            item_name = shop_items[item_id]['name']

    if ongoing_payments.get(author.id):
        await send_message_with_retry(message.channel, f"{author.mention}, you have an ongoing payment. Wait until it's completed.")
        return

    ongoing_payments[author.id] = True

    try:
        async with aiosqlite.connect('economy.db') as db:
            async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (author.id,)) as cursor:
                author_wallet = await cursor.fetchone()

            if item_id is None:
                
                if author_wallet is None or author_wallet[0] < amount:
                    await send_message_with_retry(message.channel, f"{author.mention}, you don't have enough coins.")
                    return

                await send_message_with_retry(message.channel, f"{author.mention}, are you sure you want to pay {recipient.mention} {amount:,} coins? Type 'yes' to confirm or 'no' to cancel.")
            else:
                
                async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (author.id, item_id)) as cursor:
                    author_item_quantity = await cursor.fetchone()

                if author_item_quantity is None or author_item_quantity[0] < amount:
                    await send_message_with_retry(message.channel, f"{author.mention}, you don't have enough {item_name} to pay.")
                    return

                await send_message_with_retry(message.channel, f"{author.mention}, are you sure you want to pay {recipient.mention} {amount:,} {item_name}? Type 'yes' to confirm or 'no' to cancel.")

            def check(msg):
                return msg.author == author and msg.content.lower() in ['yes', 'no']

            try:
                confirmation = await bot.wait_for('message', check=check, timeout=30)
                if confirmation.content.lower() == 'no':
                    await send_message_with_retry(message.channel, f"{author.mention}, payment cancelled.")
                    return
            except asyncio.TimeoutError:
                await send_message_with_retry(message.channel, f"{author.mention}, payment confirmation timed out.")
                return

            if item_id is None:
                
                async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (author.id,)) as cursor:
                    author_wallet = await cursor.fetchone()

                if author_wallet is None or author_wallet[0] < amount:
                    await send_message_with_retry(message.channel, f"{author.mention}, you don't have enough coins.")
                    return

                
                await db.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (amount, author.id))
                await db.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (amount, recipient.id))
                await db.commit()

                await send_message_with_retry(message.channel, f"{author.mention} paid {recipient.mention} {amount:,} coins")
            else:
                
                async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (author.id, item_id)) as cursor:
                    author_item_quantity = await cursor.fetchone()

                if author_item_quantity is None or author_item_quantity[0] < amount:
                    await send_message_with_retry(message.channel, f"{author.mention}, you don't have enough {item_name} to pay.")
                    return

                
                await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (amount, author.id, item_id))
                await db.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (recipient.id, item_id, recipient.id, item_id, amount))
                await db.commit()

                await send_message_with_retry(message.channel, f"{author.mention} paid {recipient.mention} {amount:,} {item_name}")
    finally:
        ongoing_payments[author.id] = False

async def add_command(message):
    if len(message.content.split()) < 4:
        await send_message_with_retry(message.channel, "Invalid command usage. Please use the format: `>add (userid) (amount) [item]`.")
        return

    _, user_id, amount, *item_id = message.content.split()

    try:
        user_id = int(user_id)
        amount = int(amount)
    except ValueError:
        await send_message_with_retry(message.channel, "Invalid user ID or amount. Please provide valid integers.")
        return

    async with aiosqlite.connect('economy.db') as db:
        if item_id:
            item_id = item_id[0]
            if item_id not in shop_items:
                await send_message_with_retry(message.channel, "Invalid item ID.")
                return

            if amount <= 0:
                await send_message_with_retry(message.channel, "Amount must be a positive integer.")
                return

            await db.execute("INSERT OR REPLACE INTO inventory (user_id, item_id, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?), 0) + ?)", (user_id, item_id, user_id, item_id, amount))
            await db.commit()
            await send_message_with_retry(message.channel, f"Added {amount} {shop_items[item_id]['name']} to the user's inventory.")
        else:
            if amount <= 0:
                await send_message_with_retry(message.channel, "Amount must be a positive integer.")
                return

            await db.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (amount, user_id))
            await db.commit()
            await send_message_with_retry(message.channel, f"Added {amount} coins to the user's balance.")

async def remove_command(message):

    if len(message.content.split()) < 4:
        await send_message_with_retry(message.channel, "Invalid command usage. Please use the format: `>remove (userid) (amount) [item]`.")
        return

    _, user_id, amount, *item_id = message.content.split()

    try:
        user_id = int(user_id)
        amount = int(amount)
    except ValueError:
        await send_message_with_retry(message.channel, "Invalid user ID or amount. Please provide valid integers.")
        return

    async with aiosqlite.connect('economy.db') as db:
        if item_id:
            item_id = item_id[0]
            if item_id not in shop_items:
                await send_message_with_retry(message.channel, "Invalid item ID.")
                return

            if amount <= 0:
                await send_message_with_retry(message.channel, "Amount must be a positive integer.")
                return

            async with db.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id)) as cursor:
                result = await cursor.fetchone()

            if result is None or result[0] < amount:
                await send_message_with_retry(message.channel, f"The user does not have enough {shop_items[item_id]['name']} to remove.")
                return

            await db.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (amount, user_id, item_id))
            await db.commit()
            await send_message_with_retry(message.channel, f"Removed {amount} {shop_items[item_id]['name']} from the user's inventory.")
        else:
            if amount <= 0:
                await send_message_with_retry(message.channel, "Amount must be a positive integer.")
                return

            async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()

            if result is None or result[0] < amount:
                await send_message_with_retry(message.channel, "The user does not have enough coins to remove.")
                return

            await db.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id))
            await db.commit()
            await send_message_with_retry(message.channel, f"Removed {amount} coins from the user's balance.")

async def wmc_blackjack_command(message, bot):
    wmc_user_id = message.author.id

    if wmc_ongoing_games[wmc_user_id]:
        await send_message_with_retry(message.channel, "You already have an ongoing game.")
        return
    
    try:
        wmc_bet_amount = int(message.content.split()[1])
    except (IndexError, ValueError):
        await send_message_with_retry(message.channel, "Please provide a valid bet amount.")
        return

    if wmc_bet_amount < 1 or wmc_bet_amount > 100000000:
        await send_message_with_retry(message.channel, "Bet amount must be between 1 and 100,000,000. (why the fuck are you going higher anyways)")
        return

    
    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (wmc_user_id,)) as cursor:
            wmc_result = await cursor.fetchone()
        if wmc_result is None or wmc_result[0] < wmc_bet_amount:
            await send_message_with_retry(message.channel, "You don't have enough money to make this bet.")
            return

        
        await db.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (wmc_bet_amount, wmc_user_id))
        await db.commit()

    wmc_ongoing_games[wmc_user_id] = True

    def wmc_draw_card():
        wmc_card = random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])
        return wmc_card

    def wmc_calculate_hand_value(wmc_hand):
        wmc_value = 0
        wmc_aces = 0
        for wmc_card in wmc_hand:
            if wmc_card in ['J', 'Q', 'K']:
                wmc_value += 10
            elif wmc_card == 'A':
                wmc_value += 11
                wmc_aces += 1
            else:
                wmc_value += int(wmc_card)
        while wmc_value > 21 and wmc_aces:
            wmc_value -= 10
            wmc_aces -= 1
        return wmc_value

    
    wmc_player_hand = [wmc_draw_card(), wmc_draw_card()]
    wmc_dealer_hand = [wmc_draw_card(), wmc_draw_card()]

    def wmc_hand_message(wmc_hand, wmc_name):
        return f"{wmc_name}'s hand: {', '.join(wmc_hand)} (value: {wmc_calculate_hand_value(wmc_hand)})"

    
    await send_message_with_retry(message.channel, f"{wmc_hand_message(wmc_player_hand, 'Your')}\nDealer's hand: {wmc_dealer_hand[0]}, ?")

    
    while wmc_calculate_hand_value(wmc_player_hand) < 21:
        await send_message_with_retry(message.channel, "Type 'hit' to draw another card or 'stand' to hold your current hand.")
        wmc_msg = await bot.wait_for('message', check=lambda m: m.author == message.author and m.channel == message.channel and m.content.lower() in ['hit', 'stand'])

        if wmc_msg.content.lower() == 'stand':
            break
        elif wmc_msg.content.lower() == 'hit':
            wmc_player_hand.append(wmc_draw_card())
            await send_message_with_retry(message.channel, f"{wmc_hand_message(wmc_player_hand, 'Your')}\nDealer's hand: {wmc_dealer_hand[0]}, ?")

    wmc_player_value = wmc_calculate_hand_value(wmc_player_hand)

    if wmc_player_value > 21:
        async with aiosqlite.connect('economy.db') as db:
            async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (wmc_user_id,)) as cursor:
                wmc_result = await cursor.fetchone()
            wmc_balance = wmc_result[0] if wmc_result else 0
        await send_message_with_retry(message.channel, f"Bust! Your hand value is {wmc_player_value}. You lost **`⏣ {wmc_bet_amount:,}`**.\nNew balance: `⏣{wmc_balance:,}`")
    else:
        
        while wmc_calculate_hand_value(wmc_dealer_hand) < 17:
            wmc_dealer_hand.append(wmc_draw_card())

        wmc_dealer_value = wmc_calculate_hand_value(wmc_dealer_hand)

        await send_message_with_retry(message.channel, f"{wmc_hand_message(wmc_player_hand, 'Your')}\n{wmc_hand_message(wmc_dealer_hand, 'Dealer''s')}")

        if wmc_dealer_value > 21 or wmc_player_value > wmc_dealer_value:
            wmc_winnings = wmc_bet_amount * 2
            async with aiosqlite.connect('economy.db') as db:
                await db.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wmc_winnings, wmc_user_id))
                await db.commit()
                async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (wmc_user_id,)) as cursor:
                    wmc_result = await cursor.fetchone()
                wmc_balance = wmc_result[0] if wmc_result else 0
            await send_message_with_retry(message.channel, f"You win! You won **`⏣ {wmc_winnings:,}`**.\nNew balance: `⏣{wmc_balance:,}`")
        elif wmc_player_value < wmc_dealer_value:
            async with aiosqlite.connect('economy.db') as db:
                async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (wmc_user_id,)) as cursor:
                    wmc_result = await cursor.fetchone()
                wmc_balance = wmc_result[0] if wmc_result else 0
            await send_message_with_retry(message.channel, f"You lost **`⏣ {wmc_bet_amount:,}`**.\nNew balance: `⏣{wmc_balance:,}`")
        else:
            
            async with aiosqlite.connect('economy.db') as db:
                await db.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (wmc_bet_amount, wmc_user_id))
                await db.commit()
                async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (wmc_user_id,)) as cursor:
                    wmc_result = await cursor.fetchone()
                wmc_balance = wmc_result[0] if wmc_result else 0
            await send_message_with_retry(message.channel, f"It's a tie! Your bet **`⏣ {wmc_bet_amount:,}`** has been returned.\nYour balance: `⏣{wmc_balance:,}`")

    wmc_ongoing_games[wmc_user_id] = False

async def dice_command(message):
    user_id = message.author.id
    current_time = time.time()

    if user_id in dice_cooldowns and current_time < dice_cooldowns[user_id]:
        return

    bet_args = message.content.split()[1:]

    if not bet_args:
        await send_message_with_retry(message.channel, "Please provide a valid bet amount or 'max'.")
        return

    bet_max = False
    if bet_args[0].lower() == 'max':
        bet_max = True
    else:
        try:
            bet_amount = int(bet_args[0])
        except ValueError:
            await send_message_with_retry(message.channel, "Please provide a valid bet amount or 'max'.")
            return

    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("SELECT wallet FROM balances WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
        if result is None or result[0] == 0:
            await send_message_with_retry(message.channel, "You don't have any coins to bet.")
            return

        user_balance = result[0]
        if bet_max:
            bet_amount = min(user_balance, 500000000000)
        else:
            if bet_amount > user_balance or bet_amount > 500000000000: #um change this to a reasonable amount maybe soon
                await send_message_with_retry(message.channel, "Your bet amount cannot exceed your balance or 50,000,000,000 coins") #jk went w it anyways :fire
                return

        user_roll = random.randint(1, 6) + random.randint(1, 6)
        bot_roll = random.randint(1, 6) + random.randint(1, 6)

        if user_roll > bot_roll:
            winnings = bet_amount
            await db.execute("UPDATE balances SET wallet = wallet + ? WHERE user_id = ?", (winnings, user_id))
            await db.commit()
            new_balance = user_balance + winnings
            result_message = f"You won `⏣{winnings:,}`\nNew balance: `⏣{new_balance:,}`\nYou rolled a: {user_roll}\nBot rolled a: {bot_roll}"
        elif user_roll < bot_roll:
            await db.execute("UPDATE balances SET wallet = wallet - ? WHERE user_id = ?", (bet_amount, user_id))
            await db.commit()
            new_balance = user_balance - bet_amount
            result_message = f"You lost `⏣{bet_amount:,}`\nNew balance: `⏣{new_balance:,}`\nYou rolled a: {user_roll}\nBot rolled a: {bot_roll}"
        else:
            result_message = f"It's a tie!\nYour balance remains: `⏣{user_balance:,}`\nYou rolled a: {user_roll}\nBot rolled a: {bot_roll}"

    await send_message_with_retry(message.channel, result_message)

    dice_cooldowns[user_id] = current_time + 2

async def showdupers_command(message):
    async with aiosqlite.connect('economy.db') as db:
        async with db.execute("""
            SELECT user_id 
            FROM balances 
            WHERE wallet < 0 OR bank < 0 OR EXISTS (
                SELECT 1 FROM inventory WHERE inventory.user_id = balances.user_id AND quantity < 0
            ) OR wallet + COALESCE((
                SELECT SUM(price * quantity) 
                FROM inventory 
                JOIN shop_items ON inventory.item_id = shop_items.id 
                WHERE inventory.user_id = balances.user_id), 0) < 0
        """) as cursor:
            result = await cursor.fetchall()

    if not result:
        await send_message_with_retry(message.channel, "No users found with negative balance, inventory, or net worth.")
        return

    dupers = [str(user_id[0]) for user_id in result]
    await send_message_with_retry(message.channel, f"Users with negative balance, inventory, or net worth: {', '.join(dupers)}")
        
bot.run('MTI0NzkyNjgwODQwMjIwMjY5NQ.GNzUp-.gsEA412lIZoi08wY52A8sQ-G5DCV9xR8gG0Wv4')
