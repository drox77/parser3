import asyncio
import os
import logging
import time
import json
import random
import sys
from typing import Optional, List, Dict, Tuple
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
    FSInputFile
)
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 🔑 ТОКЕН БОТА
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "8235636216:AAG0NW9iCOMtL1Di5Uik4zK0hPdB-y24yg0"

BOT_TOKEN = BOT_TOKEN.strip()

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 🔌 ПРОКСИ (можно добавить свои)
PROXIES = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
    # Добавьте реальные прокси здесь
]

# 🎁 NFT GIFTS КОЛЛЕКЦИИ (30 коллекций)
NFT_GIFT_COLLECTIONS = {
    "snoop-dogg": {"name": "🐕 Snoop Dogg", "base_url": "https://t.me/nft/SnoopDogg-", "max_number": 577000},
    "swag-bag": {"name": "🎒 Swag Bag", "base_url": "https://t.me/nft/SwagBag-", "max_number": 230000},
    "snoop-cigar": {"name": "🚬 Snoop Cigar", "base_url": "https://t.me/nft/SnoopCigar-", "max_number": 116000},
    "ice-cream": {"name": "🍦 Ice Cream", "base_url": "https://t.me/nft/IceCream-", "max_number": 319000},
    "easter-egg": {"name": "🥚 Easter Egg", "base_url": "https://t.me/nft/EasterEgg-", "max_number": 160000},
    "spring-basket": {"name": "🌷 Spring Basket", "base_url": "https://t.me/nft/SpringBasket-", "max_number": 158000},
    "jack-in-the-box": {"name": "🎁 Jack In The Box", "base_url": "https://t.me/nft/JackInTheBox-", "max_number": 95000},
    "stellar-rocket": {"name": "🚀 Stellar Rocket", "base_url": "https://t.me/nft/StellarRocket-", "max_number": 132000},
    "jolly-chimp": {"name": "🐵 Jolly Chimp", "base_url": "https://t.me/nft/JollyChimp-", "max_number": 113000},
    "happy-brownie": {"name": "🍫 Happy Brownie", "base_url": "https://t.me/nft/HappyBrownie-", "max_number": 203000},
    "instant-ramen": {"name": "🍜 Instant Ramen", "base_url": "https://t.me/nft/InstantRamen-", "max_number": 349000},
    "faith-amulet": {"name": "📿 Faith Amulet", "base_url": "https://t.me/nft/FaithAmulet-", "max_number": 128000},
    "clover-pin": {"name": "🍀 Clover Pin", "base_url": "https://t.me/nft/CloverPin-", "max_number": 218000},
    "money-pot": {"name": "💰 Money Pot", "base_url": "https://t.me/nft/MoneyPot-", "max_number": 62000},
    "pretty-posy": {"name": "💐 Pretty Posy", "base_url": "https://t.me/nft/PrettyPosy-", "max_number": 95000},
    "bow-tie": {"name": "🎀 Bow Tie", "base_url": "https://t.me/nft/BowTie-", "max_number": 53000},
    "light-sword": {"name": "⚔️ Light Sword", "base_url": "https://t.me/nft/LightSword-", "max_number": 123000},
    "fresh-socks": {"name": "🧦 Fresh Socks", "base_url": "https://t.me/nft/FreshSocks-", "max_number": 152000},
    "input-key": {"name": "🔑 Input Key", "base_url": "https://t.me/nft/InputKey-", "max_number": 122000},
    "lunar-snake": {"name": "🌙🐍 Lunar Snake", "base_url": "https://t.me/nft/LunarSnake-", "max_number": 180000},
    "big-year": {"name": "📅 Big Year", "base_url": "https://t.me/nft/BigYear-", "max_number": 71000},
    "pet-snake": {"name": "🐍 Pet Snake", "base_url": "https://t.me/nft/PetSnake-", "max_number": 160000},
    "snake-box": {"name": "📦🐍 Snake Box", "base_url": "https://t.me/nft/SnakeBox-", "max_number": 156000},
    "winter-wreath": {"name": "🎄 Winter Wreath", "base_url": "https://t.me/nft/WinterWreath-", "max_number": 67000},
    "ginger-cookie": {"name": "🍪 Ginger Cookie", "base_url": "https://t.me/nft/GingerCookie-", "max_number": 135000},
    "snow-globe": {"name": "🔮 Snow Globe", "base_url": "https://t.me/nft/SnowGlobe-", "max_number": 49000},
    "star-notepad": {"name": "📓 Star Notepad", "base_url": "https://t.me/nft/StarNotepad-", "max_number": 66000},
    "jelly-bunny": {"name": "🐰 Jelly Bunny", "base_url": "https://t.me/nft/JellyBunny-", "max_number": 98000},
    "lol-pop": {"name": "🍭 Lol Pop", "base_url": "https://t.me/nft/LolPop-", "max_number": 427000},
    "desk-calendar": {"name": "📅 Desk Calendar", "base_url": "https://t.me/nft/DeskCalendar-", "max_number": 339000},
}

# История парсинга
parsing_history = []

# Выбранные коллекции для массового парсинга
selected_collections = set()

# 🎨 КНОПКИ
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔍 ПАРСИНГ NFT GIFTS", callback_data="start_parsing")],
        [InlineKeyboardButton(text="📊 ИСТОРИЯ", callback_data="show_history")],
        [InlineKeyboardButton(text="🎁 ВЫБРАТЬ КОЛЛЕКЦИИ", callback_data="select_collections")],
        [InlineKeyboardButton(text="⚡ МАССОВЫЙ ПАРСИНГ", callback_data="mass_parse")],
        [InlineKeyboardButton(text="⚙️ НАСТРОЙКИ", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_collections_keyboard():
    buttons = []
    for coll_id, coll_data in NFT_GIFT_COLLECTIONS.items():
        # Проверяем, выбрана ли коллекция
        selected = "✅ " if coll_id in selected_collections else "⬜ "
        buttons.append([
            InlineKeyboardButton(
                text=f"{selected}{coll_data['name']}",
                callback_data=f"toggle_{coll_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔍 ПАРСИНГ ВЫБРАННЫХ", callback_data="parse_selected"),
        InlineKeyboardButton(text="🗑️ ОЧИСТИТЬ ВЫБОР", callback_data="clear_selection")
    ])
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 🔥 РЕАЛЬНЫЙ ПАРСИНГ С ПРОКСИ
class NFTGiftParser:
    
    @staticmethod
    def get_random_proxy():
        """Получить случайный прокси из списка"""
        if PROXIES:
            return random.choice(PROXIES)
        return None
    
    @staticmethod
    def generate_random_nft_urls(base_url: str, max_number: int, sample_size: int = 50) -> List[str]:
        """Генерируем случайные URL NFT для проверки"""
        urls = []
        numbers = random.sample(range(1, max_number + 1), min(sample_size, max_number))
        for number in numbers:
            url = f"{base_url}{number}"
            urls.append(url)
        return urls
    
    @staticmethod
    async def fetch_with_proxy(session: aiohttp.ClientSession, url: str, proxy: Optional[str] = None):
        """Запрос через прокси"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        try:
            if proxy:
                async with session.get(url, headers=headers, proxy=proxy, timeout=30, ssl=False) as response:
                    return await response.text(), response.status
            else:
                async with session.get(url, headers=headers, timeout=30, ssl=False) as response:
                    return await response.text(), response.status
        except Exception as e:
            logger.error(f"Ошибка при запросе {url}: {e}")
            return None, None
    
    @staticmethod
    def extract_telegram_username(html: str) -> Optional[str]:
        """Извлечь юзернейм Telegram из HTML"""
        try:
            import re
            
            # Паттерны для поиска юзернеймов
            patterns = [
                r'"username":"([^"]+)"',
                r'@([a-zA-Z0-9_]{5,32})',
                r't\.me\/([a-zA-Z0-9_]{5,32})',
                r'data-username="([^"]+)"',
                r'username\s*:\s*[\'"]([^\'"]+)[\'"]',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, str) and 5 <= len(match) <= 32:
                            # Фильтруем системные имена
                            if match.lower() not in ['telegram', 'support', 'durov', 'team', 'admin', 'bot']:
                                if not match.startswith('@'):
                                    return f"@{match}"
                                else:
                                    return match
            
            # Ищем в мета-тегах
            meta_patterns = [
                r'<meta[^>]*property="og:description"[^>]*content="[^>]*@([a-zA-Z0-9_]{5,32})',
                r'<meta[^>]*name="description"[^>]*content="[^>]*@([a-zA-Z0-9_]{5,32})',
            ]
            
            for pattern in meta_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if 5 <= len(match) <= 32:
                            return f"@{match}"
            
        except Exception as e:
            logger.debug(f"Ошибка парсинга HTML: {e}")
        
        return None
    
    @staticmethod
    async def parse_nft_owners(collection_id: str, sample_size: int = 30) -> Tuple[List[Dict], List[str]]:
        """Парсинг реальных владельцев NFT через прокси"""
        collection = NFT_GIFT_COLLECTIONS.get(collection_id)
        if not collection:
            return [], []
        
        urls = NFTGiftParser.generate_random_nft_urls(
            collection["base_url"],
            collection["max_number"],
            sample_size
        )
        
        logger.info(f"Парсинг {len(urls)} NFT из {collection['name']}")
        
        owners = []
        checked_urls = []
        proxy_errors = 0
        
        # Создаем сессию с поддержкой прокси
        connector = aiohttp.TCPConnector(limit=10, ssl=False)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for idx, url in enumerate(urls):
                try:
                    # Получаем прокси для этого запроса
                    proxy = NFTGiftParser.get_random_proxy()
                    
                    logger.info(f"Проверка {idx+1}/{len(urls)}: {url} через прокси: {proxy}")
                    
                    html, status = await NFTGiftParser.fetch_with_proxy(session, url, proxy)
                    
                    if html and status == 200:
                        checked_urls.append(url)
                        
                        # Извлекаем владельца
                        username = NFTGiftParser.extract_telegram_username(html)
                        
                        if username:
                            nft_id = url.split('-')[-1]
                            owner_data = {
                                "username": username,
                                "nft_url": url,
                                "nft_id": nft_id,
                                "collection": collection["name"]
                            }
                            owners.append(owner_data)
                            logger.info(f"Найден владелец: {username} для NFT #{nft_id}")
                        else:
                            logger.debug(f"Владелец не найден для {url}")
                    
                    # Случайная задержка между запросами
                    delay = random.uniform(1.0, 3.0)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Ошибка при парсинге {url}: {e}")
                    proxy_errors += 1
                    
                    # Если много ошибок с прокси, пробуем без прокси
                    if proxy_errors > 5:
                        logger.warning("Слишком много ошибок прокси, пробую без прокси...")
                        try:
                            html, status = await NFTGiftParser.fetch_with_proxy(session, url, None)
                            if html and status == 200:
                                checked_urls.append(url)
                        except:
                            pass
        
        logger.info(f"Парсинг завершен. Найдено {len(owners)} владельцев")
        return owners, checked_urls
    
    @staticmethod
    def generate_realistic_owners(collection_name: str, count: int) -> List[Dict]:
        """Генерируем реалистичных владельцев (запасной вариант)"""
        real_nft_users = [
            {"username": "@crypto_whale", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@nft_collector", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@web3_enthusiast", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@digital_art_lover", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@blockchain_guru", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@metaverse_pioneer", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@hodl_forever", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@crypto_nomad", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@nft_artist", "nft_url": "", "nft_id": "0000", "collection": collection_name},
            {"username": "@web3_builder", "nft_url": "", "nft_id": "0000", "collection": collection_name},
        ]
        
        return random.sample(real_nft_users, min(count, len(real_nft_users)))

# 🤖 ОБРАБОТЧИКИ БОТА
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎁 <b>NFT GIFT PARSER v4.0</b>\n\n"
        "🔍 <b>Парсинг реальных владельцев NFT Gifts</b>\n"
        "🛡️ <b>Использует прокси для обхода ограничений</b>\n"
        "👥 <b>Находит реальные Telegram аккаунты</b>\n\n"
        "<i>Выберите действие:</i>",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "start_parsing")
async def on_start_parsing(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎯 <b>ВЫБЕРИТЕ РЕЖИМ ПАРСИНГА:</b>\n\n"
        "1. <b>Одна коллекция</b> - глубокий парсинг\n"
        "2. <b>Массовый парсинг</b> - несколько коллекций\n"
        "3. <b>Своя ссылка</b> - конкретный NFT\n\n"
        "<i>Парсинг использует прокси для обхода ограничений</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 ОДНА КОЛЛЕКЦИЯ", callback_data="single_collection")],
            [InlineKeyboardButton(text="📊 МАССОВЫЙ ПАРСИНГ", callback_data="mass_parse")],
            [InlineKeyboardButton(text="🔗 СВОЯ ССЫЛКА", callback_data="custom_parse")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")]
        ])
    )

@dp.callback_query(F.data == "select_collections")
async def on_select_collections(callback: CallbackQuery):
    selected_count = len(selected_collections)
    await callback.message.edit_text(
        f"📋 <b>ВЫБОР КОЛЛЕКЦИЙ</b>\n\n"
        f"✅ Выбрано: {selected_count}/30 коллекций\n"
        f"🖱️ Нажмите на коллекцию для выбора/отмены\n\n"
        f"<i>После выбора запустите массовый парсинг</i>",
        reply_markup=get_collections_keyboard()
    )

@dp.callback_query(F.data.startswith("toggle_"))
async def on_toggle_collection(callback: CallbackQuery):
    collection_id = callback.data.replace("toggle_", "")
    
    if collection_id in selected_collections:
        selected_collections.remove(collection_id)
    else:
        selected_collections.add(collection_id)
    
    selected_count = len(selected_collections)
    await callback.message.edit_text(
        f"📋 <b>ВЫБОР КОЛЛЕКЦИЙ</b>\n\n"
        f"✅ Выбрано: {selected_count}/30 коллекций\n"
        f"🖱️ Нажмите на коллекцию для выбора/отмены\n\n"
        f"<i>После выбора запустите массовый парсинг</i>",
        reply_markup=get_collections_keyboard()
    )

@dp.callback_query(F.data == "clear_selection")
async def on_clear_selection(callback: CallbackQuery):
    selected_collections.clear()
    await callback.answer("✅ Выбор очищен")
    await callback.message.edit_text(
        "📋 <b>ВЫБОР КОЛЛЕКЦИЙ</b>\n\n"
        "✅ Выбрано: 0/30 коллекций\n"
        "🖱️ Нажмите на коллекцию для выбора/отмены\n\n"
        "<i>После выбора запустите массовый парсинг</i>",
        reply_markup=get_collections_keyboard()
    )

@dp.callback_query(F.data == "parse_selected")
async def on_parse_selected(callback: CallbackQuery):
    if not selected_collections:
        await callback.answer("❌ Не выбрано ни одной коллекции")
        return
    
    collections_list = "\n".join([f"• {NFT_GIFT_COLLECTIONS[cid]['name']}" for cid in selected_collections])
    
    await callback.message.edit_text(
        f"🚀 <b>МАССОВЫЙ ПАРСИНГ</b>\n\n"
        f"📊 Коллекций: {len(selected_collections)}\n"
        f"🔍 Будет проверено: {len(selected_collections) * 30} NFT\n"
        f"⏳ Время: ~{len(selected_collections) * 2} минут\n\n"
        f"<b>Коллекции:</b>\n{collections_list}\n\n"
        f"<i>Используются прокси для парсинга</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ НАЧАТЬ ПАРСИНГ", callback_data="start_mass_parse")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="select_collections")]
        ])
    )

@dp.callback_query(F.data == "start_mass_parse")
async def on_start_mass_parse(callback: CallbackQuery):
    if not selected_collections:
        await callback.answer("❌ Не выбрано коллекций")
        return
    
    await callback.message.edit_text(
        "🔄 <b>ЗАПУСК МАССОВОГО ПАРСИНГА...</b>\n\n"
        "⏳ Начинаю парсинг выбранных коллекций\n"
        "🛡️ Использую прокси для обхода\n"
        "⏱️ Ожидайте 1-5 минут\n\n"
        "<i>Статус будет обновляться</i>"
    )
    
    all_owners = []
    total_checked = 0
    
    for idx, coll_id in enumerate(selected_collections, 1):
        collection = NFT_GIFT_COLLECTIONS[coll_id]
        
        # Обновляем статус
        status_text = (
            f"📊 <b>ПАРСИНГ {idx}/{len(selected_collections)}</b>\n\n"
            f"🎁 Коллекция: {collection['name']}\n"
            f"🔢 NFT в коллекции: {collection['max_number']:,}\n"
            f"🔄 Проверяю случайные NFT...\n"
            f"🛡️ Использую прокси\n\n"
            f"<i>Ожидайте 30-60 секунд</i>"
        )
        
        try:
            await callback.message.edit_text(status_text)
            
            # Парсим коллекцию
            parser = NFTGiftParser()
            owners, checked_urls = await parser.parse_nft_owners(coll_id, sample_size=30)
            
            total_checked += len(checked_urls)
            all_owners.extend(owners)
            
            # Сохраняем в историю
            parsing_history.append({
                "collection": collection["name"],
                "total_nft": collection["max_number"],
                "checked_count": len(checked_urls),
                "found_owners": len(owners),
                "owners": owners[:10],
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Ошибка парсинга {collection['name']}: {e}")
    
    # Формируем результаты
    unique_owners = []
    seen_usernames = set()
    
    for owner in all_owners:
        if owner["username"] not in seen_usernames:
            seen_usernames.add(owner["username"])
            unique_owners.append(owner)
    
    if unique_owners:
        owners_list = "\n".join([f"{i+1}. {owner['username']} ({owner['collection']})" 
                               for i, owner in enumerate(unique_owners[:25])])
        
        result_text = (
            f"✅ <b>МАССОВЫЙ ПАРСИНГ ЗАВЕРШЁН!</b>\n\n"
            f"📊 Коллекций проверено: {len(selected_collections)}\n"
            f"🔍 NFT проверено: {total_checked}\n"
            f"👥 Уникальных владельцев: {len(unique_owners)}\n"
            f"⏱️ Время: {time.time() - parsing_history[-1]['timestamp'] if parsing_history else 0:.1f}с\n\n"
            f"<b>НАЙДЕННЫЕ ВЛАДЕЛЬЦЫ:</b>\n{owners_list}"
        )
        
        if len(unique_owners) > 25:
            result_text += f"\n\n... и ещё {len(unique_owners) - 25} владельцев"
    else:
        result_text = (
            f"⚠️ <b>ВЛАДЕЛЬЦЫ НЕ НАЙДЕНЫ</b>\n\n"
            f"📊 Коллекций: {len(selected_collections)}\n"
            f"🔍 NFT проверено: {total_checked}\n"
            f"👥 Найдено: 0 владельцев\n\n"
            f"<i>Попробуйте использовать другие прокси или увеличьте количество проверяемых NFT</i>"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 СОХРАНИТЬ РЕЗУЛЬТАТЫ", callback_data="save_results")],
        [InlineKeyboardButton(text="🔄 ПОВТОРИТЬ", callback_data="parse_selected")],
        [InlineKeyboardButton(text="🔙 В МЕНЮ", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(result_text, reply_markup=keyboard)

@dp.callback_query(F.data == "single_collection")
async def on_single_collection(callback: CallbackQuery):
    # Создаем клавиатуру со всеми коллекциями
    buttons = []
    row = []
    for coll_id, coll_data in NFT_GIFT_COLLECTIONS.items():
        row.append(InlineKeyboardButton(
            text=coll_data["name"],
            callback_data=f"parse_{coll_id}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="start_parsing")])
    
    await callback.message.edit_text(
        "🎯 <b>ВЫБЕРИТЕ КОЛЛЕКЦИЮ ДЛЯ ПАРСИНГА:</b>\n\n"
        "<i>Бот проверит случайные NFT из выбранной коллекции\n"
        "Использует прокси для обхода ограничений</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("parse_"))
async def on_parse_single(callback: CallbackQuery):
    collection_id = callback.data.replace("parse_", "")
    collection = NFT_GIFT_COLLECTIONS.get(collection_id)
    
    if not collection:
        await callback.answer("❌ Коллекция не найдена")
        return
    
    await callback.message.edit_text(
        f"🔍 <b>ПАРСИНГ {collection['name']}</b>\n\n"
        f"📊 Всего NFT: {collection['max_number']:,}\n"
        f"🔢 Проверяю случайные NFT...\n"
        f"🛡️ Использую прокси\n"
        f"⏳ Ожидайте 30-60 секунд\n\n"
        f"<i>Ищу реальных владельцев Telegram</i>"
    )
    
    start_time = time.time()
    
    try:
        parser = NFTGiftParser()
        owners, checked_urls = await parser.parse_nft_owners(collection_id, sample_size=50)
        elapsed_time = time.time() - start_time
        
        # Сохраняем в историю
        parsing_history.append({
            "collection": collection["name"],
            "total_nft": collection["max_number"],
            "checked_count": len(checked_urls),
            "found_owners": len(owners),
            "owners": owners[:20],
            "sample_urls": checked_urls[:5],
            "timestamp": time.time()
        })
        
        if owners:
            # Уникальные владельцы
            unique_owners = []
            seen = set()
            for owner in owners:
                if owner["username"] not in seen:
                    seen.add(owner["username"])
                    unique_owners.append(owner)
            
            owners_list = "\n".join([f"{i+1}. {owner['username']}" 
                                   for i, owner in enumerate(unique_owners[:20])])
            
            sample_links = ""
            if checked_urls:
                sample_links = "\n<b>Примеры проверенных NFT:</b>\n"
                for i, url in enumerate(checked_urls[:3], 1):
                    nft_id = url.split('-')[-1]
                    sample_links += f"{i}. <a href='{url}'>NFT #{nft_id}</a>\n"
            
            result_text = (
                f"✅ <b>ПАРСИНГ ЗАВЕРШЁН!</b>\n\n"
                f"🎁 <b>Коллекция:</b> {collection['name']}\n"
                f"🔢 <b>Всего NFT:</b> {collection['max_number']:,}\n"
                f"🔍 <b>Проверено:</b> {len(checked_urls)} NFT\n"
                f"👥 <b>Найдено владельцев:</b> {len(unique_owners)}\n"
                f"⏱️ <b>Время:</b> {elapsed_time:.1f}с\n"
                f"{sample_links}\n"
                f"<b>НАЙДЕННЫЕ ВЛАДЕЛЬЦЫ:</b>\n{owners_list}"
            )
            
            if len(unique_owners) > 20:
                result_text += f"\n\n... и ещё {len(unique_owners) - 20} владельцев"
        else:
            # Если не нашли реальных, показываем примерных
            fake_owners = NFTGiftParser.generate_realistic_owners(collection["name"], 15)
            owners_list = "\n".join([f"{i+1}. {owner['username']}" 
                                   for i, owner in enumerate(fake_owners)])
            
            result_text = (
                f"⚠️ <b>РЕАЛЬНЫЕ ВЛАДЕЛЬЦЫ НЕ НАЙДЕНЫ</b>\n\n"
                f"🎁 {collection['name']}\n"
                f"🔢 Всего NFT: {collection['max_number']:,}\n"
                f"🔍 Проверено: {len(checked_urls)} NFT\n"
                f"⏱️ Время: {elapsed_time:.1f}с\n\n"
                f"<i>Возможные владельцы (пример):</i>\n{owners_list}\n\n"
                f"<b>Совет:</b> Добавьте больше прокси в настройках"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💾 СОХРАНИТЬ РЕЗУЛЬТАТЫ", callback_data=f"save_{collection_id}")],
            [InlineKeyboardButton(text="🔄 ПОВТОРИТЬ", callback_data=f"parse_{collection_id}")],
            [InlineKeyboardButton(text="🔍 ЕЩЁ КОЛЛЕКЦИИ", callback_data="single_collection")]
        ])
        
        await callback.message.edit_text(result_text, reply_markup=keyboard, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")
        await callback.message.edit_text(
            f"❌ <b>ОШИБКА ПАРСИНГА</b>\n\n"
            f"{collection['name']}\n"
            f"Ошибка: {str(e)[:100]}\n\n"
            f"<i>Проверьте настройки прокси</i>",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query(F.data == "save_results")
async def on_save_results(callback: CallbackQuery):
    if not parsing_history:
        await callback.answer("❌ Нет данных для сохранения")
        return
    
    import tempfile
    import os
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("🎁 NFT GIFT PARSER - РЕЗУЛЬТАТЫ\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Дата: {time.ctime()}\n")
            f.write(f"Всего записей в истории: {len(parsing_history)}\n\n")
            
            for i, record in enumerate(reversed(parsing_history[-10:]), 1):
                f.write(f"ЗАПИСЬ #{i}\n")
                f.write(f"Коллекция: {record['collection']}\n")
                f.write(f"Всего NFT: {record['total_nft']:,}\n")
                f.write(f"Проверено: {record.get('checked_count', 0)}\n")
                f.write(f"Найдено: {record.get('found_owners', 0)} владельцев\n")
                f.write(f"Время: {record.get('time', 0):.1f}с\n")
                
                owners = record.get('owners', [])
                if owners:
                    f.write("Владельцы:\n")
                    for owner in owners[:15]:
                        if isinstance(owner, dict):
                            f.write(f"  • {owner.get('username', 'N/A')}\n")
                        else:
                            f.write(f"  • {owner}\n")
                f.write("\n")
            
            filename = f.name
        
        document = FSInputFile(filename)
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=document,
            caption="📁 <b>Результаты парсинга сохранены</b>"
        )
        
        await callback.answer("✅ Файл отправлен")
        os.unlink(filename)
        
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await callback.answer("❌ Ошибка сохранения")

@dp.callback_query(F.data == "show_history")
async def on_show_history(callback: CallbackQuery):
    if not parsing_history:
        await callback.message.edit_text(
            "📭 <b>ИСТОРИЯ ПУСТА</b>\n\n"
            "Начните парсинг NFT Gifts!",
            reply_markup=get_main_keyboard()
        )
        return
    
    history_text = "📊 <b>ИСТОРИЯ ПАРСИНГА NFT GIFTS:</b>\n\n"
    for i, record in enumerate(reversed(parsing_history[-8:]), 1):
        time_str = time.strftime('%H:%M', time.localtime(record.get('timestamp', time.time())))
        history_text += (
            f"{i}. <b>{record['collection']}</b>\n"
            f"   📅 {time_str} | 🔍 {record.get('checked_count', 0)} NFT\n"
            f"   👥 {record.get('found_owners', 0)} владельцев\n"
        )
    
    history_text += f"\n<i>Всего записей: {len(parsing_history)}</i>"
    
    await callback.message.edit_text(
        history_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ ОЧИСТИТЬ ИСТОРИЮ", callback_data="clear_history")],
            [InlineKeyboardButton(text="💾 СОХРАНИТЬ ВСЁ", callback_data="save_results")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")]
        ])
    )

@dp.callback_query(F.data == "clear_history")
async def on_clear_history(callback: CallbackQuery):
    parsing_history.clear()
    await callback.message.edit_text(
        "✅ <b>История очищена!</b>",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "back_to_main")
async def on_back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎁 <b>NFT GIFT PARSER v4.0</b>\n\n"
        "🔍 <b>Парсинг реальных владельцев NFT Gifts</b>\n"
        "🛡️ <b>Использует прокси для обхода ограничений</b>\n"
        "👥 <b>Находит реальные Telegram аккаунты</b>\n\n"
        "<i>Выберите действие:</i>",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "settings")
async def on_settings(callback: CallbackQuery):
    proxy_status = "✅" if PROXIES else "❌"
    
    await callback.message.edit_text(
        f"⚙️ <b>НАСТРОЙКИ ПАРСЕРА</b>\n\n"
        f"🛡️ <b>Прокси:</b> {proxy_status} ({len(PROXIES)} шт)\n"
        f"📊 <b>История записей:</b> {len(parsing_history)}\n"
        f"🎁 <b>Коллекций в базе:</b> {len(NFT_GIFT_COLLECTIONS)}\n"
        f"✅ <b>Выбрано коллекций:</b> {len(selected_collections)}\n\n"
        f"<i>Для добавления прокси отредактируйте код</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 ОБНОВИТЬ ПРОКСИ", callback_data="refresh_proxies")],
            [InlineKeyboardButton(text="🗑️ ОЧИСТИТЬ ВСЁ", callback_data="clear_all")],
            [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")]
        ])
    )

@dp.callback_query(F.data == "mass_parse")
async def on_mass_parse(callback: CallbackQuery):
    await callback.answer("Используйте 'Выбрать коллекции' для массового парсинга")
    await on_select_collections(callback)

@dp.message()
async def handle_unknown(message: Message):
    await message.answer(
        "🎁 <b>NFT GIFT PARSER v4.0</b>\n\n"
        "Используйте кнопки меню или команду /start",
        reply_markup=get_main_keyboard()
    )

# 🚀 ЗАПУСК БОТА
async def main():
    logger.info("=" * 50)
    logger.info("🎁 ЗАПУСК NFT GIFT PARSER v4.0")
    logger.info(f"🤖 Токен: {BOT_TOKEN[:10]}...")
    logger.info(f"🛡️ Прокси: {len(PROXIES)} доступно")
    logger.info(f"📦 Коллекций: {len(NFT_GIFT_COLLECTIONS)}")
    logger.info("=" * 50)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        me = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{me.username}")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ ОШИБКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
