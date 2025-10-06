"""
Unit tests for WeatherTool
Tests weather API handling without making real API calls
"""

import pytest
from unittest.mock import Mock, patch
from weather import WeatherTool


class TestWeatherTool:
    """Test suite for WeatherTool class"""
    
    @pytest.fixture
    def weather_tool(self):
        """Create a WeatherTool instance for testing"""
        return WeatherTool()
    
    @patch('weather.requests.get')
    def test_get_weather_success(self, mock_get, weather_tool):
        """Test successful weather data retrieval"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 15.5,
                "feels_like": 14.2,
                "humidity": 72
            },
            "weather": [{"description": "cloudy"}],
            "wind": {"speed": 5.5}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test
        result = weather_tool.get_weather("London")
        
        # Assertions
        assert result["city"] == "London"
        assert result["country"] == "GB"
        assert result["temperature"] == 15.5
        assert result["feels_like"] == 14.2
        assert result["humidity"] == 72
        assert result["description"] == "cloudy"
        assert result["wind_speed"] == 5.5
    
    @patch('weather.requests.get')
    def test_get_weather_invalid_city(self, mock_get, weather_tool):
        """Test handling of invalid city name"""
        # Mock 404 response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 City not found")
        mock_get.return_value = mock_response
        
        # Test
        with pytest.raises(Exception) as exc_info:
            weather_tool.get_weather("InvalidCityXYZ123")
        
        assert "Failed to fetch weather" in str(exc_info.value)
    
    @patch('weather.requests.get')
    def test_get_weather_api_timeout(self, mock_get, weather_tool):
        """Test handling of API timeout"""
        # Mock timeout
        mock_get.side_effect = Exception("Timeout")
        
        # Test
        with pytest.raises(Exception) as exc_info:
            weather_tool.get_weather("London")
        
        assert "Failed to fetch weather" in str(exc_info.value)
    
    @patch('weather.requests.get')
    def test_get_weather_api_key_used(self, mock_get, weather_tool):
        """Test that API key is included in request"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Paris",
            "sys": {"country": "FR"},
            "main": {"temp": 18, "feels_like": 17, "humidity": 65},
            "weather": [{"description": "sunny"}],
            "wind": {"speed": 3.2}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        weather_tool.get_weather("Paris")
        
        # Verify API call was made with correct parameters
        call_args = mock_get.call_args
        assert call_args[1]['params']['q'] == "Paris"
        assert 'appid' in call_args[1]['params']
        assert call_args[1]['params']['units'] == "metric"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])