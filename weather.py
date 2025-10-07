
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherTool:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str):
        """
        Get current weather for a city
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary with weather information
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"  # Celsius
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant info
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }
            
            return weather_info
            
        except Exception as e:
            raise Exception(f"Failed to fetch weather: {str(e)}")


# Test the weather tool
if __name__ == "__main__":
    weather = WeatherTool()
    
    # Test with a city
    city_name = "Delhi"
    try:
        result = weather.get_weather(city_name)
        print(f"Weather in {result['city']}:")
        print(f"Temperature: {result['temperature']}°C")
        print(f"Feels like: {result['feels_like']}°C")
        print(f"Conditions: {result['description']}")
        print(f"Humidity: {result['humidity']}%")
        print(f"Wind Speed: {result['wind_speed']} m/s")
    except Exception as e:
        print(f"Error: {e}")