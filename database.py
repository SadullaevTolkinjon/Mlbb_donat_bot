import aiosqlite
from config import DB_NAME

async def init_db():
    """Database yaratish"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Users jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                total_orders INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Orders jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                user_id INTEGER,
                diamonds INTEGER,
                price INTEGER,
                player_id TEXT,
                zone_id TEXT,
                screenshot_file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        await db.commit()
    print("✅ Database initialized")

async def add_user(telegram_id: int, username: str, first_name: str):
    """Yangi user qo'shish"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
            (telegram_id, username, first_name)
        )
        await db.commit()

async def create_order(user_id: int, diamonds: int, price: int, player_id: str, zone_id: str):
    """Yangi buyurtma yaratish"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Order number generatsiya
        cursor = await db.execute("SELECT COUNT(*) FROM orders")
        count = (await cursor.fetchone())[0]
        order_number = f"ORD{count + 1:04d}"
        
        await db.execute("""
            INSERT INTO orders (order_number, user_id, diamonds, price, player_id, zone_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order_number, user_id, diamonds, price, player_id, zone_id))
        
        await db.commit()
        return order_number

async def update_screenshot(order_number: str, file_id: str):
    """Screenshot qo'shish"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE orders SET screenshot_file_id = ?, status = 'screenshot_sent' WHERE order_number = ?",
            (file_id, order_number)
        )
        await db.commit()

async def get_order(order_number: str):
    """Buyurtma ma'lumotini olish"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,)
        )
        return await cursor.fetchone()

async def confirm_payment(order_number: str):
    """To'lovni tasdiqlash"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE orders SET status = 'payment_confirmed' WHERE order_number = ?",
            (order_number,)
        )
        await db.commit()

async def complete_order(order_number: str):
    """Buyurtmani bajarish"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE orders SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE order_number = ?",
            (order_number,)
        )
        await db.commit()

async def get_pending_orders():
    """Kutayotgan buyurtmalar"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE status = 'screenshot_sent' ORDER BY created_at DESC"
        )
        return await cursor.fetchall()

async def get_statistics():
    """Statistika"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Bugungi buyurtmalar
        cursor = await db.execute(
            "SELECT COUNT(*), SUM(price) FROM orders WHERE DATE(created_at) = DATE('now') AND status = 'completed'"
        )
        today = await cursor.fetchone()
        
        # Jami
        cursor = await db.execute(
            "SELECT COUNT(*), SUM(price) FROM orders WHERE status = 'completed'"
        )
        total = await cursor.fetchone()
        
        return {
            'today_count': today[0] or 0,
            'today_amount': today[1] or 0,
            'total_count': total[0] or 0,
            'total_amount': total[1] or 0
        }
        
        
        
        
async def get_pending_orders():
    """Kutayotgan buyurtmalar (screenshot yuborilgan)"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE status = 'screenshot_sent' ORDER BY created_at DESC LIMIT 20"
        )
        return await cursor.fetchall()
    
    
async def get_completed_orders():
    """Bajarilgan buyurtmalar"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE status = 'completed' ORDER BY completed_at DESC LIMIT 50"
        )
        return await cursor.fetchall()
    
async def get_all_packages():
    """Barcha paketlarni olish (sozlamalar uchun)"""
    packages = []
    
    from config import REGULAR_PACKAGES, DOUBLE_PACKAGES, WEEKLY_PASS
    
    for pkg in REGULAR_PACKAGES:
        packages.append({
            'type': 'regular',
            'diamonds': pkg['diamonds'],
            'price': pkg['price']
        })
    
    for pkg in DOUBLE_PACKAGES:
        packages.append({
            'type': 'double',
            'diamonds': pkg['total'],
            'price': pkg['price']
        })
    
    for pkg in WEEKLY_PASS:
        packages.append({
            'type': 'weekly',
            'name': pkg['name'],
            'price': pkg['price']
        })
    
    return packages

async def get_payment_info():
    """To'lov ma'lumotini olish"""
    from config import PAYMENT_CARD, PAYMENT_PHONE, PAYMENT_NAME
    return {
        'card': PAYMENT_CARD,
        'phone': PAYMENT_PHONE,
        'name': PAYMENT_NAME
    }
    
async def get_user_orders(user_id: int):
    """User buyurtmalarini olish"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        )
        return await cursor.fetchall()
    
async def get_all_orders():
    """Barcha buyurtmalar (so'ngi 50 ta)"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 50"
        )
        return await cursor.fetchall()
    
async def get_user(user_id: int):
    """User ma'lumotini olish"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (user_id,)
        )
        return await cursor.fetchone()