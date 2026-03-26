"""Orchestrator - The agentic loop that ties everything together"""
import json
import re
from agent.llm_client import LLMClient
from agent.prompts import get_system_prompt
from agent.context_builder import ContextBuilder
from rag.vector_store import VectorStore
from data.models import Restaurant, Reservation, get_session

class Orchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
        self.context_builder = ContextBuilder(self.vector_store)
        self.max_iterations = 5
    
    def _clean_response(self, content: str) -> str:
        """Strip Qwen 3 thinking tags and clean up response"""
        if not content:
            return ""
        # Remove <think>...</think> blocks (Qwen 3 thinking mode)
        cleaned = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        return cleaned.strip()
    
    def process_message(self, user_message: str, conversation_history: list) -> str:
        """Main agentic loop"""
        
        # Build messages — no eager RAG, let the LLM decide when to search
        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        tools = self.llm.get_tool_definitions()
        
        for _ in range(self.max_iterations):
            response = self.llm.chat(messages, tools)
            
            # Check for tool calls
            if response.tool_calls:
                # Clean thinking tags from content before adding to history
                clean_content = self._clean_response(response.content or "")
                messages.append({
                    "role": "assistant",
                    "content": clean_content,
                    "tool_calls": [
                        {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in response.tool_calls
                    ]
                })
                
                # Execute each tool
                for tool_call in response.tool_calls:
                    result = self._execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                continue
            
            # No tool calls = final response — clean thinking tags
            cleaned = self._clean_response(response.content)
            if cleaned:
                return cleaned
            
            # If response was empty after cleaning, retry without tools
            response = self.llm.chat(messages, tools=None)
            cleaned = self._clean_response(response.content)
            return cleaned or "I'm not sure I understood that. Could you rephrase?"
        
        return "I'm having trouble processing your request. Could you try rephrasing?"
    
    def _match_time_slot(self, input_time: str, available_slots: list) -> str | None:
        """Fuzzy match user/LLM time input to available slots.
        Handles '1:30' → '1:30 PM', '7pm' → '7:00 PM', etc."""
        # Exact match first
        if input_time in available_slots:
            return input_time
        
        # Normalize: strip, lowercase for comparison
        normalized = input_time.strip().upper().replace(".", "")
        
        for slot in available_slots:
            slot_upper = slot.strip().upper()
            # Match without AM/PM: "1:30" matches "1:30 PM"
            slot_time_part = slot_upper.replace(" AM", "").replace(" PM", "")
            input_time_part = normalized.replace(" AM", "").replace(" PM", "").replace("AM", "").replace("PM", "")
            
            if input_time_part == slot_time_part:
                return slot
            
            # Match "7" to "7:00 PM"
            if input_time_part == slot_time_part.split(":")[0]:
                return slot
        
        return None
    
    def _execute_tool(self, name: str, args: dict) -> str:
        """Execute a tool and return result"""
        session = get_session()
        
        try:
            if name == "search_restaurants":
                # Use RAG semantic search for better results
                rag_results = self.vector_store.search(
                    query=args.get("query", ""),
                    n_results=10,
                    neighborhood=args.get("neighborhood")
                )
                
                # Get full restaurant details from DB for RAG matches
                all_matched = []
                for result in rag_results:
                    restaurant_name = result.get("metadata", {}).get("name", "")
                    r = session.query(Restaurant).filter(
                        Restaurant.name == restaurant_name
                    ).first()
                    if r:
                        all_matched.append(r)
                
                # Apply price filter if specified
                price_filter = args.get("price_range")
                if price_filter:
                    filtered = [r for r in all_matched if r.price_range == price_filter]
                    if filtered:
                        restaurants = filtered
                    else:
                        # No results at requested price — return all with a note
                        restaurants = all_matched
                        prices_available = sorted(set(r.price_range for r in all_matched))
                        note = f"No results at {price_filter}. Showing results at other prices: {', '.join(prices_available)}"
                        result_list = [{"name": r.name, "neighborhood": r.neighborhood, "cuisines": r.cuisines, "price_range": r.price_range, "rating": r.rating, "available_slots": r.available_slots, "ambiance": r.ambiance} for r in restaurants]
                        return json.dumps({"note": note, "results": result_list}, indent=2)
                else:
                    restaurants = all_matched
                
                return json.dumps([{
                    "name": r.name,
                    "neighborhood": r.neighborhood,
                    "cuisines": r.cuisines,
                    "price_range": r.price_range,
                    "rating": r.rating,
                    "available_slots": r.available_slots,
                    "ambiance": r.ambiance
                } for r in restaurants], indent=2)
            
            elif name == "get_restaurant_details":
                r = session.query(Restaurant).filter(
                    Restaurant.name.ilike(f"%{args['restaurant_name']}%")
                ).first()
                
                if not r:
                    return json.dumps({"error": "Restaurant not found"})
                
                return json.dumps({
                    "name": r.name,
                    "neighborhood": r.neighborhood,
                    "cuisines": r.cuisines,
                    "price_range": r.price_range,
                    "rating": r.rating,
                    "available_slots": r.available_slots,
                    "amenities": r.amenities,
                    "ambiance": r.ambiance,
                    "capacity": r.seating_capacity,
                    "description": r.description
                }, indent=2)
            
            elif name == "check_availability":
                r = session.query(Restaurant).filter(
                    Restaurant.name.ilike(f"%{args['restaurant_name']}%")
                ).first()
                
                if not r:
                    return json.dumps({"available": False, "reason": "Restaurant not found"})
                
                # Guard for missing required fields
                time_input = args.get("time", "")
                date_input = args.get("date", "")
                party_size = args.get("party_size", 2)
                
                if not time_input:
                    return json.dumps({
                        "available": False,
                        "reason": f"No time specified. Available slots for {r.name}: {', '.join(r.available_slots)}"
                    })
                
                if not date_input:
                    return json.dumps({
                        "available": False,
                        "reason": "No date specified. Please ask the customer for a date."
                    })
                
                matched_time = self._match_time_slot(time_input, r.available_slots)
                if not matched_time:
                    return json.dumps({
                        "available": False,
                        "reason": f"'{time_input}' is not available. Options: {', '.join(r.available_slots)}"
                    })
                
                # Sum all confirmed bookings at this slot
                from sqlalchemy import func
                booked_seats = session.query(func.coalesce(func.sum(Reservation.party_size), 0)).filter(
                    Reservation.restaurant_id == r.id,
                    Reservation.date == date_input,
                    Reservation.time == matched_time,
                    Reservation.status == "confirmed"
                ).scalar()
                
                remaining = r.seating_capacity - booked_seats
                requested = party_size
                
                if requested > remaining:
                    # Check other slots for this date
                    slot_info = []
                    for slot in r.available_slots:
                        slot_booked = session.query(func.coalesce(func.sum(Reservation.party_size), 0)).filter(
                            Reservation.restaurant_id == r.id,
                            Reservation.date == date_input,
                            Reservation.time == slot,
                            Reservation.status == "confirmed"
                        ).scalar()
                        slot_remaining = r.seating_capacity - slot_booked
                        if slot_remaining >= requested:
                            slot_info.append(f"{slot} ({slot_remaining} seats left)")
                    
                    reason = f"Only {remaining} seats left at {time_input} (capacity: {r.seating_capacity})."
                    if slot_info:
                        reason += f" Try: {', '.join(slot_info)}"
                    else:
                        reason += " No slots available with enough seats for your party on this date."
                    
                    return json.dumps({"available": False, "reason": reason})
                
                return json.dumps({
                    "available": True,
                    "restaurant": r.name,
                    "neighborhood": r.neighborhood,
                    "date": args["date"],
                    "time": matched_time,
                    "party_size": requested,
                    "seats_remaining": remaining,
                    "total_capacity": r.seating_capacity
                })
            
            elif name == "make_reservation":
                r = session.query(Restaurant).filter(
                    Restaurant.name.ilike(f"%{args['restaurant_name']}%")
                ).first()
                
                if not r:
                    return json.dumps({"success": False, "error": "Restaurant not found"})
                
                # Validate phone number — must be exactly 10 digits
                import re as re_phone
                phone = args.get("customer_phone", "")
                digits_only = re_phone.sub(r'\D', '', phone)
                if len(digits_only) != 10:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid phone number '{phone}'. Must be exactly 10 digits."
                    })
                
                # Fuzzy match the time slot
                time_input = args.get("time", "")
                if not time_input:
                    return json.dumps({
                        "success": False,
                        "error": f"No time specified. Available slots: {', '.join(r.available_slots)}"
                    })
                
                matched_time = self._match_time_slot(time_input, r.available_slots)
                if not matched_time:
                    return json.dumps({
                        "success": False,
                        "error": f"'{time_input}' is not available. Options: {', '.join(r.available_slots)}"
                    })
                
                # Capacity check — sum all confirmed bookings at this slot
                from sqlalchemy import func
                booked_seats = session.query(func.coalesce(func.sum(Reservation.party_size), 0)).filter(
                    Reservation.restaurant_id == r.id,
                    Reservation.date == args["date"],
                    Reservation.time == matched_time,
                    Reservation.status == "confirmed"
                ).scalar()
                
                remaining = r.seating_capacity - booked_seats
                requested = args["party_size"]
                
                if requested > remaining:
                    return json.dumps({
                        "success": False,
                        "error": f"Not enough seats. Only {remaining} of {r.seating_capacity} seats left at {args['time']}. Available times: {', '.join(r.available_slots)}"
                    })
                
                import random, string
                from datetime import datetime
                booking_id = f"DW-{datetime.now().year}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
                
                reservation = Reservation(
                    id=booking_id,
                    restaurant_id=r.id,
                    restaurant_name=r.name,
                    customer_name=args["customer_name"],
                    customer_phone=args["customer_phone"],
                    party_size=args["party_size"],
                    date=args["date"],
                    time=matched_time,
                    special_requests=args.get("special_requests", "")
                )
                session.add(reservation)
                session.commit()
                
                new_remaining = remaining - requested
                
                return json.dumps({
                    "success": True,
                    "booking_id": booking_id,
                    "restaurant": r.name,
                    "neighborhood": r.neighborhood,
                    "date": args["date"],
                    "time": args["time"],
                    "party_size": args["party_size"],
                    "customer_name": args["customer_name"],
                    "customer_phone": args["customer_phone"],
                    "special_requests": args.get("special_requests", "None"),
                    "seats_remaining_after_booking": new_remaining,
                    "total_capacity": r.seating_capacity
                }, indent=2)
            
            elif name == "cancel_reservation":
                reservation = session.query(Reservation).filter(
                    Reservation.id == args["booking_id"]
                ).first()
                
                if not reservation:
                    return json.dumps({"success": False, "error": "Reservation not found"})
                
                reservation.status = "cancelled"
                session.commit()
                return json.dumps({"success": True, "message": f"Reservation {args['booking_id']} cancelled"})
            
            elif name == "get_reservation":
                q = session.query(Reservation)
                if args.get("booking_id"):
                    q = q.filter(Reservation.id == args["booking_id"])
                elif args.get("phone"):
                    q = q.filter(Reservation.customer_phone == args["phone"])
                
                reservation = q.first()
                if not reservation:
                    return json.dumps({"error": "Reservation not found"})
                
                return json.dumps({
                    "booking_id": reservation.id,
                    "restaurant": reservation.restaurant_name,
                    "date": reservation.date,
                    "time": reservation.time,
                    "party_size": reservation.party_size,
                    "customer_name": reservation.customer_name,
                    "status": reservation.status
                }, indent=2)
            
            elif name == "get_recommendations":
                occasion = args.get("occasion", "").lower()
                ambiance_map = {
                    "date": "Romantic", "romantic": "Romantic", "anniversary": "Romantic",
                    "birthday": "Trendy", "celebration": "Trendy",
                    "business": "Fine Dining", "corporate": "Fine Dining",
                    "family": "Family-friendly", "kids": "Family-friendly",
                    "casual": "Casual", "friends": "Casual"
                }
                
                target = next((v for k, v in ambiance_map.items() if k in occasion), None)
                restaurants = session.query(Restaurant).all()
                
                if target:
                    results = [r for r in restaurants if target in r.ambiance][:5]
                else:
                    results = restaurants[:5]
                
                return json.dumps([{
                    "name": r.name,
                    "neighborhood": r.neighborhood,
                    "cuisines": r.cuisines,
                    "price_range": r.price_range,
                    "rating": r.rating,
                    "ambiance": r.ambiance
                } for r in results], indent=2)
            
            return json.dumps({"error": "Unknown tool"})
        
        finally:
            session.close()
