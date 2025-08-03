
def weather(location):
        # Mock weather data
        weather_data = {
            "New York": {"temperature": 72, "condition": "Sunny"},
            "London": {"temperature": 62, "condition": "Cloudy"},
            "Tokyo": {"temperature": 80, "condition": "Partly cloudy"},
            "Paris": {"temperature": 65, "condition": "Rainy"},
            "Sydney": {"temperature": 85, "condition": "Clear"},
            "Berlin": {"temperature": 60, "condition": "Foggy"},
        }
        
        return weather_data.get(location, {"error": f"No weather data available for {location}"})
    
def news(topic):
    # Mock news data
    news_data = {
        "technology": [
            "New AI breakthrough announced by research lab",
            "Tech company releases latest smartphone model",
            "Quantum computing reaches milestone achievement"
        ],
        "sports": [
            "Local team wins championship game",
            "Star player signs record-breaking contract",
            "Olympic committee announces host city for 2036"
        ],
        "weather": [
            "Storm system developing in the Atlantic",
            "Record temperatures recorded across Europe",
            "Climate scientists release new research findings"
        ]
    }
    
    return {"headlines": news_data.get(topic.lower(), ["No news available for this topic"])}
