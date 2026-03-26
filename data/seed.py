"""Seed script - Generate restaurants: every cuisine in every neighborhood"""
import uuid
import random
from data.models import Restaurant, init_db, get_session

NEIGHBORHOODS = [
    "Koramangala", "Indiranagar", "Whitefield", "HSR Layout",
    "MG Road", "Jayanagar", "JP Nagar", "Malleshwaram"
]

CUISINES = [
    "North Indian", "South Indian", "Chinese", "Italian", "Continental",
    "Japanese", "Thai", "Mexican", "Mediterranean", "Mughlai",
    "Coastal", "Cafe", "Bakery", "Pan-Asian", "BBQ & Grills"
]

PRICE_RANGES = ["₹200-400", "₹400-600", "₹600-800", "₹800-1200", "₹1200+"]

TIME_SLOTS = [
    ["12:00 PM", "1:30 PM", "3:00 PM"],
    ["7:00 PM", "8:30 PM", "10:00 PM"],
    ["12:30 PM", "7:30 PM", "9:00 PM"],
    ["12:00 PM", "7:00 PM", "8:30 PM"],
    ["1:00 PM", "7:30 PM", "9:30 PM"],
]

AMBIANCE_OPTIONS = ["Casual", "Romantic", "Family-friendly", "Fine Dining", "Trendy", "Cozy", "Rooftop", "Garden"]
AMENITY_OPTIONS = ["Wi-Fi", "Parking", "Outdoor Seating", "Live Music", "Private Dining", "Bar", "Buffet", "Valet"]

# Restaurant name patterns per cuisine
NAME_TEMPLATES = {
    "North Indian": ["Tandoor Tales {n}", "Spice Route {n}", "Delhi Darbar {n}", "Curry House {n}", "Punjab Grill {n}"],
    "South Indian": ["Dosa Corner {n}", "Madras Café {n}", "Udupi Grand {n}", "Temple Kitchen {n}", "Coconut Grove {n}"],
    "Chinese": ["Wok Express {n}", "Dragon Palace {n}", "Golden Chopsticks {n}", "Noodle Bar {n}", "Ming Garden {n}"],
    "Italian": ["Pasta La Vista {n}", "Olive Garden {n}", "Trattoria {n}", "Roma Kitchen {n}", "La Piazza {n}"],
    "Continental": ["The Brasserie {n}", "Euro Kitchen {n}", "Savoy Grill {n}", "Ivy House {n}", "The Continental {n}"],
    "Japanese": ["Sakura Sushi {n}", "Tokyo Table {n}", "Ramen House {n}", "Zen Garden {n}", "Wasabi {n}"],
    "Thai": ["Thai Orchid {n}", "Bangkok Bites {n}", "Lemongrass {n}", "Basil Thai {n}", "Siam Kitchen {n}"],
    "Mexican": ["Taco Bell {n}", "El Mexicano {n}", "Burrito Bar {n}", "Cantina {n}", "Salsa House {n}"],
    "Mediterranean": ["Olive & Feta {n}", "Hummus House {n}", "Aegean Kitchen {n}", "Pita Palace {n}", "Mezze Bar {n}"],
    "Mughlai": ["Nawab's Kitchen {n}", "Biryani Blues {n}", "Royal Feast {n}", "Kebab Corner {n}", "Mughal Durbar {n}"],
    "Coastal": ["Fisherman's Wharf {n}", "Sea Shell {n}", "Coastal Curry {n}", "Beach House {n}", "Prawn Star {n}"],
    "Cafe": ["Brew & Bite {n}", "The Coffee Lab {n}", "Artisan Café {n}", "Mocha House {n}", "Bean Counter {n}"],
    "Bakery": ["Flour Power {n}", "Crumbs & Co {n}", "The Bake Shop {n}", "Sugar Rush {n}", "Oven Fresh {n}"],
    "Pan-Asian": ["Asia Kitchen {n}", "Eastern Spice {n}", "Chopstick House {n}", "Fusion Bowl {n}", "Lotus Kitchen {n}"],
    "BBQ & Grills": ["Smoke House {n}", "Grill Master {n}", "Fire & Ice {n}", "Charcoal Pit {n}", "BBQ Nation {n}"],
}

DESCRIPTIONS = {
    "North Indian": "Authentic North Indian flavors with rich curries, tandoori dishes, and freshly baked naan. A true culinary journey through the heartland of India.",
    "South Indian": "Traditional South Indian cuisine featuring crispy dosas, fluffy idlis, and aromatic sambar. A taste of Southern comfort.",
    "Chinese": "Flavorful Indo-Chinese and authentic Chinese dishes with woks fired up to perfection. From dim sum to sizzlers.",
    "Italian": "Handcrafted pasta, wood-fired pizzas, and classic Italian preparations with the finest imported ingredients.",
    "Continental": "Classic European cuisine with a modern twist. Steaks, grills, and sophisticated preparations.",
    "Japanese": "Authentic Japanese cuisine featuring fresh sushi, ramen, and traditional preparations with attention to detail.",
    "Thai": "Fragrant Thai curries, stir-fries, and soups with the perfect balance of sweet, sour, salty, and spicy.",
    "Mexican": "Bold Mexican flavors with handmade tortillas, fresh guacamole, and zesty salsas.",
    "Mediterranean": "Healthy Mediterranean cuisine with fresh salads, grilled meats, and dips from the sun-kissed coast.",
    "Mughlai": "Royal Mughlai cuisine with slow-cooked biryanis, succulent kebabs, and rich gravies fit for royalty.",
    "Coastal": "Fresh seafood preparations from India's coastline. Prawns, fish, crab, and more cooked to perfection.",
    "Cafe": "Artisanal coffees, light bites, sandwiches, and a cozy atmosphere perfect for work or catch-ups.",
    "Bakery": "Freshly baked breads, pastries, cakes, and desserts. A paradise for those with a sweet tooth.",
    "Pan-Asian": "A culinary tour across Asia featuring dishes from Thailand, Japan, Korea, and Vietnam under one roof.",
    "BBQ & Grills": "Smoky grilled meats, flame-kissed vegetables, and signature BBQ sauces. A carnivore's paradise.",
}


def generate_restaurants():
    """Generate one restaurant per cuisine per neighborhood = 120 restaurants"""
    init_db()
    session = get_session()
    
    # Clear existing
    session.query(Restaurant).delete()
    session.commit()
    
    restaurants = []
    counter = 0
    
    for neighborhood in NEIGHBORHOODS:
        for cuisine in CUISINES:
            counter += 1
            
            # Pick a unique name (strip to avoid trailing spaces from short neighborhood codes)
            template = random.choice(NAME_TEMPLATES[cuisine])
            name = template.format(n=neighborhood[:3]).strip()
            
            # Random but realistic details
            price = random.choice(PRICE_RANGES)
            slots = random.choice(TIME_SLOTS)
            rating = round(random.uniform(3.5, 5.0), 1)
            ambiance = random.sample(AMBIANCE_OPTIONS, k=random.randint(2, 3))
            amenities = random.sample(AMENITY_OPTIONS, k=random.randint(2, 4))
            
            restaurant = Restaurant(
                id=str(uuid.uuid4()),
                name=name,
                neighborhood=neighborhood,
                city="Bangalore",
                cuisines=[cuisine],
                price_range=price,
                seating_capacity=random.randint(30, 120),
                available_slots=slots,
                rating=rating,
                amenities=amenities,
                ambiance=ambiance,
                description=DESCRIPTIONS[cuisine]
            )
            restaurants.append(restaurant)
            session.add(restaurant)
    
    session.commit()
    print(f"✅ Seeded {len(restaurants)} restaurants ({len(NEIGHBORHOODS)} neighborhoods × {len(CUISINES)} cuisines)")
    session.close()


if __name__ == "__main__":
    generate_restaurants()
