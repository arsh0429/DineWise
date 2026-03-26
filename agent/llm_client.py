"""LLM client for Ollama (local)"""
import os
import json
from openai import OpenAI

class LLMClient:
    def __init__(self, base_url="http://localhost:11434/v1", model="qwen3:8b"):
        self.client = OpenAI(base_url=base_url, api_key="ollama")  # Ollama doesn't need a real key
        self.model = model
    
    def chat(self, messages: list, tools: list = None) -> dict:
        """Send chat completion request with optional tools"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
    
    def get_tool_definitions(self):
        """Tool definitions for OpenAI-compatible format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_restaurants",
                    "description": "Search for restaurants by cuisine, neighborhood, price range, or ambiance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Natural language search query"},
                            "neighborhood": {"type": "string", "description": "Optional neighborhood filter"},
                            "price_range": {"type": "string", "description": "Optional price filter"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_restaurant_details",
                    "description": "Get full details of a specific restaurant",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "restaurant_name": {"type": "string"}
                        },
                        "required": ["restaurant_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Check availability for a restaurant",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "restaurant_name": {"type": "string"},
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "party_size": {"type": "integer"}
                        },
                        "required": ["restaurant_name", "date", "time", "party_size"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "make_reservation",
                    "description": "Create a reservation after collecting all required information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "restaurant_name": {"type": "string"},
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "party_size": {"type": "integer"},
                            "customer_name": {"type": "string"},
                            "customer_phone": {"type": "string"},
                            "special_requests": {"type": "string"}
                        },
                        "required": ["restaurant_name", "date", "time", "party_size", "customer_name", "customer_phone"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_reservation",
                    "description": "Cancel an existing reservation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_id": {"type": "string"}
                        },
                        "required": ["booking_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_reservation",
                    "description": "Look up a reservation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_id": {"type": "string"},
                            "phone": {"type": "string"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations",
                    "description": "Get personalized recommendations based on occasion",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "occasion": {"type": "string"},
                            "party_size": {"type": "integer"},
                            "budget": {"type": "string"}
                        },
                        "required": ["occasion"]
                    }
                }
            }
        ]
