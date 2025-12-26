
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import Admin, Customer
from app.models.product import Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_PRODUCTS = [
    {
        "title": "Avengers Tower",
        "price": 40.99,
        "icon": "🏢",
        "rating": 5,
        "category": "Sets",
        "stock": 10,
        "description": "Epic Avengers Tower playset",
        "detailed_description": "Build your own Avengers Tower with this amazing set featuring multiple floors, detailed interiors, and exclusive minifigures.",
        "images": ["https://via.placeholder.com/400x300?text=Avengers+Tower"]
    },
    {
        "title": "Venomized Groot",
        "price": 35.99,
        "icon": "🪴",
        "rating": 4,
        "category": "Plushies",
        "stock": 5,
        "description": "Cute Venomized Groot plush",
        "detailed_description": "Adorable plush toy combining Groot and Venom! Soft, cuddly, and perfect for Marvel fans.",
        "images": ["https://via.placeholder.com/400x300?text=Venomized+Groot"]
    },
    {
        "title": "Expecto Patronum",
        "price": 69.99,
        "icon": "🦌",
        "rating": 5,
        "category": "Sets",
        "stock": 8,
        "description": "Harry Potter Patronus set",
        "detailed_description": "Cast your own Patronus with this magical set featuring light-up effects and detailed minifigures from Harry Potter.",
        "images": ["https://via.placeholder.com/400x300?text=Expecto+Patronum"]
    },
    {
        "title": "The Child",
        "price": 40.99,
        "icon": "🐸",
        "rating": 5,
        "category": "Plushies",
        "stock": 20,
        "description": "Baby Yoda plush toy",
        "detailed_description": "The cutest Child (Baby Yoda) plush toy from The Mandalorian. Super soft and huggable!",
        "images": ["https://via.placeholder.com/400x300?text=The+Child"]
    },
    {
        "title": "Alpine Lodge",
        "price": 80.99,
        "icon": "🏠",
        "rating": 5,
        "category": "Sets",
        "stock": 3,
        "description": "Cozy Alpine Lodge building set",
        "detailed_description": "Build a beautiful Alpine Lodge complete with detailed interior, ski equipment, and winter scenery.",
        "images": ["https://via.placeholder.com/400x300?text=Alpine+Lodge"]
    },
    {
        "title": "Monkey King",
        "price": 45.59,
        "icon": "🐵",
        "rating": 4,
        "category": "Blocks",
        "stock": 12,
        "description": "Monkey King action figure",
        "detailed_description": "Legendary Monkey King building figure with articulated joints and accessories from Chinese mythology.",
        "images": ["https://via.placeholder.com/400x300?text=Monkey+King"]
    },
    {
        "title": "Tusken Raider",
        "price": 19.99,
        "icon": "👺",
        "rating": 3,
        "category": "Sets",
        "stock": 15,
        "description": "Star Wars Tusken Raider",
        "detailed_description": "Authentic Tusken Raider minifigure set from Star Wars with detailed accessories and weapons.",
        "images": ["https://via.placeholder.com/400x300?text=Tusken+Raider"]
    },
    {
        "title": "Hogwarts Castle",
        "price": 120.99,
        "icon": "🏰",
        "rating": 5,
        "category": "Sets",
        "stock": 2,
        "description": "Massive Hogwarts Castle set",
        "detailed_description": "The ultimate Hogwarts Castle with over 6000 pieces, featuring all the iconic locations from Harry Potter.",
        "images": ["https://via.placeholder.com/400x300?text=Hogwarts+Castle"]
    },
    {
        "title": "Mighty Bowser",
        "price": 59.99,
        "icon": "🐢",
        "rating": 5,
        "category": "Blocks",
        "stock": 7,
        "description": "Super Mario Bowser figure",
        "detailed_description": "Build the mighty Bowser from Super Mario with moving parts, fire-breathing action, and detailed design.",
        "images": ["https://via.placeholder.com/400x300?text=Mighty+Bowser"]
    },
    {
        "title": "Dobby Experience",
        "price": 29.99,
        "icon": "🧦",
        "rating": 4,
        "category": "Plushies",
        "stock": 25,
        "description": "Dobby the House Elf plush",
        "detailed_description": "Adorable Dobby plush complete with removable sock! A must-have for Harry Potter fans.",
        "images": ["https://via.placeholder.com/400x300?text=Dobby"]
    },
    {
        "title": "Orchid Plant",
        "price": 49.99,
        "icon": "🌺",
        "rating": 5,
        "category": "Sets",
        "stock": 18,
        "description": "Beautiful Orchid building set",
        "detailed_description": "Create a stunning orchid plant with this botanical building set featuring realistic details and colors.",
        "images": ["https://via.placeholder.com/400x300?text=Orchid"]
    },
    {
        "title": "London Skyline",
        "price": 39.99,
        "icon": "🎡",
        "rating": 5,
        "category": "Sets",
        "stock": 10,
        "description": "London landmarks building set",
        "detailed_description": "Build iconic London landmarks including Big Ben, London Eye, Tower Bridge and more in this detailed architecture set.",
        "images": ["https://via.placeholder.com/400x300?text=London+Skyline"]
    }
]

def create_admin_user(db: Session) -> None:

    try:

        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()

        if existing_admin:
            logger.info("Admin user already exists")
            return

        admin = Admin(
            username="admin",
            email="admin@toyverse.com",
            password_hash=hash_password("admin123"),
            role="admin",
            full_name="ToyVerse Administrator"
        )

        db.add(admin)
        db.commit()

        logger.info("✓ Admin user created successfully")
        logger.info("  Username: admin")
        logger.info("  Password: admin123")
        logger.info("  Email: admin@toyverse.com")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
        raise

def create_customer_user(db: Session) -> None:

    try:

        existing_customer = db.query(Customer).filter(Customer.username == "customer").first()

        if existing_customer:
            logger.info("Test customer user already exists")
            return

        customer = Customer(
            username="customer",
            email="customer@toyverse.com",
            password_hash=hash_password("customer123"),
            role="customer",
            full_name="Test Customer"
        )

        db.add(customer)
        db.commit()

        logger.info("✓ Test customer user created successfully")
        logger.info("  Username: customer")
        logger.info("  Password: customer123")
        logger.info("  Email: customer@toyverse.com")

    except Exception as e:
        logger.error(f"Error creating customer user: {e}")
        db.rollback()
        raise

def create_products(db: Session) -> None:

    try:

        existing_count = db.query(Product).count()

        if existing_count > 0:
            logger.info(f"Products already exist ({existing_count} products in database)")
            return

        logger.info(f"Creating {len(INITIAL_PRODUCTS)} products...")

        for product_data in INITIAL_PRODUCTS:
            product = Product(
                title=product_data["title"],
                price=product_data["price"],
                category=product_data["category"],
                stock=product_data["stock"],
                rating=product_data["rating"],
                icon=product_data["icon"],
                description=product_data["description"],
                detailed_description=product_data["detailed_description"]
            )

            product.images = product_data["images"]

            db.add(product)

        db.commit()

        logger.info(f"✓ {len(INITIAL_PRODUCTS)} products created successfully")

    except Exception as e:
        logger.error(f"Error creating products: {e}")
        db.rollback()
        raise

def main():

    try:
        logger.info("=" * 60)
        logger.info("ToyVerse Database Seeding")
        logger.info("=" * 60)

        db = SessionLocal()

        try:

            logger.info("\nCreating admin user...")
            create_admin_user(db)

            logger.info("\nCreating test customer user...")
            create_customer_user(db)

            logger.info("\nCreating products...")
            create_products(db)

            logger.info("\n" + "=" * 60)
            logger.info("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("\nYou can now:")
            logger.info("  1. Start the API: python -m app.main")
            logger.info("  2. Login with:")
            logger.info("     - Admin: username=admin, password=admin123")
            logger.info("     - Customer: username=customer, password=customer123")
            logger.info("  3. Access API docs: http://localhost:8000/docs")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error("Database seeding FAILED!")
        logger.error(f"{'=' * 60}")
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
