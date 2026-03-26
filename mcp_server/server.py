"""MCP Server with reservation tools"""
import json
import random
import string
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent
from data.models import Restaurant, Reservation, get_session

server = Server("dinewise-reservation")

def generate_booking_id():
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"DW-{datetime.now().year}-{chars}"

# Tool definitions
TOOLS = [
    Tool(
        name="search_restaurants",
        description="Search for restaurants by cuisine, neighborhood, price range, or ambiance. Use this when user wants to find restaurants.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search (e.g., 'romantic Italian dinner')"},
                "neighborhood": {"type": "string", "description": "Optional: Koramangala, Indiranagar, Whitefield, HSR Layout, MG Road, Jayanagar, JP Nagar, Malleshwaram"},
                "price_range": {"type": "string", "description": "Optional: ₹200-400, ₹400-600, ₹600-800, ₹800-1200, ₹1200+"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_restaurant_details",
        description="Get full details of a specific restaurant by name",
        inputSchema={
            "type": "object",
            "properties": {
                "restaurant_name": {"type": "string", "description": "Exact restaurant name"}
            },
            "required": ["restaurant_name"]
        }
    ),
    Tool(
        name="check_availability",
        description="Check if a restaurant has availability for a specific date, time, and party size",
        inputSchema={
            "type": "object",
            "properties": {
                "restaurant_name": {"type": "string"},
                "date": {"type": "string", "description": "Date in format 'February 11, 2026'"},
                "time": {"type": "string", "description": "Time slot like '7:30 PM'"},
                "party_size": {"type": "integer"}
            },
            "required": ["restaurant_name", "date", "time", "party_size"]
        }
    ),
    Tool(
        name="make_reservation",
        description="Create a reservation after confirming all details with the user",
        inputSchema={
            "type": "object",
            "properties": {
                "restaurant_name": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "party_size": {"type": "integer"},
                "customer_name": {"type": "string"},
                "customer_phone": {"type": "string"},
                "special_requests": {"type": "string", "description": "Optional special requests"}
            },
            "required": ["restaurant_name", "date", "time", "party_size", "customer_name", "customer_phone"]
        }
    ),
    Tool(
        name="cancel_reservation",
        description="Cancel an existing reservation by booking reference",
        inputSchema={
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking reference like DW-2024-ABC123"}
            },
            "required": ["booking_id"]
        }
    ),
    Tool(
        name="get_reservation",
        description="Look up a reservation by booking reference or phone number",
        inputSchema={
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "phone": {"type": "string"}
            }
        }
    ),
    Tool(
        name="get_recommendations",
        description="Get personalized restaurant recommendations based on occasion",
        inputSchema={
            "type": "object",
            "properties": {
                "occasion": {"type": "string", "description": "E.g., date night, birthday, business lunch, family dinner"},
                "party_size": {"type": "integer"},
                "budget": {"type": "string", "description": "Optional price range preference"}
            },
            "required": ["occasion"]
        }
    )
]

@server.list_tools()
async def list_tools():
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    session = get_session()
    
    try:
        if name == "search_restaurants":
            query = arguments.get("query", "")
            neighborhood = arguments.get("neighborhood")
            price = arguments.get("price_range")
            
            q = session.query(Restaurant)
            if neighborhood:
                q = q.filter(Restaurant.neighborhood == neighborhood)
            if price:
                q = q.filter(Restaurant.price_range == price)
            
            restaurants = q.limit(5).all()
            results = [{"name": r.name, "neighborhood": r.neighborhood, "cuisines": r.cuisines,
                       "price_range": r.price_range, "rating": r.rating, "slots": r.available_slots} 
                      for r in restaurants]
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        elif name == "get_restaurant_details":
            r = session.query(Restaurant).filter(Restaurant.name.ilike(f"%{arguments['restaurant_name']}%")).first()
            if not r:
                return [TextContent(type="text", text="Restaurant not found")]
            return [TextContent(type="text", text=json.dumps({
                "name": r.name, "neighborhood": r.neighborhood, "cuisines": r.cuisines,
                "price_range": r.price_range, "rating": r.rating, "slots": r.available_slots,
                "amenities": r.amenities, "ambiance": r.ambiance, "capacity": r.seating_capacity
            }, indent=2))]
        
        elif name == "check_availability":
            r = session.query(Restaurant).filter(Restaurant.name.ilike(f"%{arguments['restaurant_name']}%")).first()
            if not r:
                return [TextContent(type="text", text="Restaurant not found")]
            
            if arguments["time"] not in r.available_slots:
                return [TextContent(type="text", text=f"Time slot {arguments['time']} not available. Available: {', '.join(r.available_slots)}")]
            
            if arguments["party_size"] > r.seating_capacity:
                return [TextContent(type="text", text=f"Party too large. Max capacity: {r.seating_capacity}")]
            
            return [TextContent(type="text", text=json.dumps({
                "available": True,
                "restaurant": r.name,
                "date": arguments["date"],
                "time": arguments["time"],
                "party_size": arguments["party_size"]
            }))]
        
        elif name == "make_reservation":
            r = session.query(Restaurant).filter(Restaurant.name.ilike(f"%{arguments['restaurant_name']}%")).first()
            if not r:
                return [TextContent(type="text", text="Restaurant not found")]
            
            booking = Reservation(
                id=generate_booking_id(),
                restaurant_id=r.id,
                restaurant_name=r.name,
                customer_name=arguments["customer_name"],
                customer_phone=arguments["customer_phone"],
                party_size=arguments["party_size"],
                date=arguments["date"],
                time=arguments["time"],
                special_requests=arguments.get("special_requests", "")
            )
            session.add(booking)
            session.commit()
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "booking_id": booking.id,
                "restaurant": booking.restaurant_name,
                "neighborhood": r.neighborhood,
                "date": booking.date,
                "time": booking.time,
                "party_size": booking.party_size,
                "customer_name": booking.customer_name,
                "customer_phone": booking.customer_phone,
                "special_requests": booking.special_requests
            }, indent=2))]
        
        elif name == "cancel_reservation":
            booking = session.query(Reservation).filter(Reservation.id == arguments["booking_id"]).first()
            if not booking:
                return [TextContent(type="text", text="Booking not found")]
            
            booking.status = "cancelled"
            session.commit()
            return [TextContent(type="text", text=f"Reservation {booking.id} cancelled successfully")]
        
        elif name == "get_reservation":
            q = session.query(Reservation)
            if arguments.get("booking_id"):
                q = q.filter(Reservation.id == arguments["booking_id"])
            elif arguments.get("phone"):
                q = q.filter(Reservation.customer_phone == arguments["phone"])
            
            booking = q.first()
            if not booking:
                return [TextContent(type="text", text="No reservation found")]
            
            return [TextContent(type="text", text=json.dumps({
                "booking_id": booking.id,
                "restaurant": booking.restaurant_name,
                "date": booking.date,
                "time": booking.time,
                "party_size": booking.party_size,
                "status": booking.status
            }, indent=2))]
        
        elif name == "get_recommendations":
            occasion = arguments.get("occasion", "").lower()
            ambiance_map = {
                "date": "Romantic", "romantic": "Romantic", "anniversary": "Romantic",
                "birthday": "Trendy", "celebration": "Trendy",
                "business": "Fine Dining", "meeting": "Fine Dining",
                "family": "Family-friendly", "kids": "Family-friendly",
                "casual": "Casual", "friends": "Casual"
            }
            target_ambiance = next((v for k, v in ambiance_map.items() if k in occasion), None)
            
            restaurants = session.query(Restaurant).all()
            results = [r for r in restaurants if target_ambiance in r.ambiance][:5] if target_ambiance else restaurants[:5]
            
            return [TextContent(type="text", text=json.dumps([
                {"name": r.name, "neighborhood": r.neighborhood, "cuisines": r.cuisines,
                 "price_range": r.price_range, "rating": r.rating, "ambiance": r.ambiance}
                for r in results
            ], indent=2))]
        
        return [TextContent(type="text", text="Unknown tool")]
    
    finally:
        session.close()
