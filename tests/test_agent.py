# """
# Unit tests for AgentPipeline
# Tests intent classification, routing, and end-to-end flows
# """

# import pytest
# from unittest.mock import Mock, patch, MagicMock
# from agent import AgentPipeline, AgentState


# class TestAgentPipeline:
#     """Test suite for AgentPipeline class"""
    
#     @pytest.fixture
#     def agent(self):
#         """Create AgentPipeline instance with mocked dependencies"""
#         with patch('agent.ChatOpenAI'), \
#              patch('agent.WeatherTool'), \
#              patch('agent.RAGTool'), \
#              patch('agent.ChatDatabase'):
#             return AgentPipeline()
    
#     def test_classify_intent_weather(self, agent):
#         """Test intent classification for weather queries"""
#         # Mock LLM response
#         # mock_chain = Mock()
#         # mock_chain.invoke.return_value = "weather"
#         # mock_prompt.from_template.return_value.__or__ = Mock(return_value=mock_chain)
        
#         state = {
#             "query": "What's the weather in London?",
#             "chat_history": [],
#             "intent": "",
#             "city": "",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         with patch.object(agent.llm, 'invoke', return_value="weather"):
#             result = agent._classify_intent(state)
#             assert result["intent"] == "weather"
        
#         # assert result["intent"] == "weather"
    
#     @patch('agent.StrOutputParser')
#     @patch('agent.ChatPromptTemplate')
#     def test_classify_intent_document(self, mock_prompt, mock_parser, agent):
#         """Test intent classification for document queries"""
#         mock_chain = Mock()
#         mock_chain.invoke.return_value = "document"
#         mock_prompt.from_template.return_value.__or__ = Mock(return_value=mock_chain)
        
#         state = {
#             "query": "What does the PDF say about transformers?",
#             "chat_history": [],
#             "intent": "",
#             "city": "",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         result = agent._classify_intent(state)
        
#         assert result["intent"] == "document"
    
#     def test_extract_city(self,agent):
#         """Test city extraction from query"""
#         # mock_chain = Mock()
#         # mock_chain.invoke.return_value = "Paris"
#         # mock_prompt.from_template.return_value.__or__ = Mock(return_value=mock_chain)
        
#         state = {
#             "query": "How's the weather in Paris?",
#             "chat_history": [],
#             "intent": "weather",
#             "city": "",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         with patch.object(agent.llm, 'invoke', return_value="Paris"):
#             result = agent._extract_city(state)
#             assert result["city"] == "Paris"
    
#     def test_fetch_weather_success(self, agent):
#         """Test successful weather fetching"""
#         agent.weather_tool.get_weather = Mock(return_value={
#             "city": "Tokyo",
#             "temperature": 22,
#             "description": "clear sky",
#             "humidity": 60,
#             "wind_speed": 3.5,
#             "country": "JP"
#         })
        
#         state = {
#             "query": "Weather in Tokyo?",
#             "chat_history": [],
#             "intent": "weather",
#             "city": "Tokyo",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         result = agent._fetch_weather(state)
        
#         assert result["weather_data"]["city"] == "Tokyo"
#         assert result["weather_data"]["temperature"] == 22
#         assert result["error"] == ""
    
#     def test_fetch_weather_failure(self, agent):
#         """Test weather fetching with API error"""
#         agent.weather_tool.get_weather = Mock(side_effect=Exception("API Error"))
        
#         state = {
#             "query": "Weather in InvalidCity?",
#             "chat_history": [],
#             "intent": "weather",
#             "city": "InvalidCity",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         result = agent._fetch_weather(state)
        
#         assert "Weather fetch failed" in result["error"]
#         assert result["weather_data"] == {}
    
#     def test_query_documents(self, agent):
#         """Test document querying"""
#         agent.rag_tool.query = Mock(return_value={
#             "answer": "The transformer is a neural network architecture.",
#             "sources": [{"content": "...", "metadata": {}}]
#         })
        
#         state = {
#             "query": "What is a transformer?",
#             "chat_history": [],
#             "intent": "document",
#             "city": "",
#             "weather_data": {},
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         result = agent._query_documents(state)
        
#         assert "transformer" in result["rag_response"]["answer"].lower()
#         assert len(result["rag_response"]["sources"]) > 0
    
#     def test_route_intent_weather(self, agent):
#         """Test routing for weather intent"""
#         state = {"intent": "weather"}
        
#         result = agent._route_intent(state)
        
#         assert result == "weather"
    
#     def test_route_intent_document(self, agent):
#         """Test routing for document intent"""
#         state = {"intent": "document"}
        
#         result = agent._route_intent(state)
        
#         assert result == "document"
    
#     def test_generate_response_weather(self, agent):
#         """Test response generation for weather"""
#         # mock_chain = Mock()
#         # mock_chain.invoke.return_value = "It's 22°C and sunny in Tokyo."
#         # mock_prompt.from_template.return_value.__or__ = Mock(return_value=mock_chain)
        
#         state = {
#             "query": "Weather in Tokyo?",
#             "chat_history": [],
#             "intent": "weather",
#             "city": "Tokyo",
#             "weather_data": {
#                 "city": "Tokyo",
#                 "country": "JP",
#                 "temperature": 22,
#                 "description": "clear sky",
#                 "humidity": 60,
#                 "wind_speed": 3.5
#             },
#             "rag_response": {},
#             "final_answer": "",
#             "error": ""
#         }
        
#         # result = agent._generate_response(state)
        
#         # assert "Tokyo" in result["final_answer"]
#         with patch.object(agent.llm, 'invoke', return_value="It's 22°C and sunny in Tokyo."):
#             result = agent._generate_response(state)
#             assert "Tokyo" in result["final_answer"]
    
#     def test_generate_response_document(self, agent):
#         """Test response generation for documents"""
#         state = {
#             "query": "What is a transformer?",
#             "chat_history": [],
#             "intent": "document",
#             "city": "",
#             "weather_data": {},
#             "rag_response": {
#                 "answer": "A transformer is a neural network architecture.",
#                 "sources": []
#             },
#             "final_answer": "",
#             "error": ""
#         }
        
#         result = agent._generate_response(state)
        
#         assert result["final_answer"] == "A transformer is a neural network architecture."


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])

"""
Unit tests for AgentPipeline
Tests intent classification, routing, and end-to-end flows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agent import AgentPipeline, AgentState


class TestAgentPipeline:
    """Test suite for AgentPipeline class"""
    
    @pytest.fixture
    def agent(self):
        """Create AgentPipeline instance with mocked dependencies"""
        with patch('agent.ChatOpenAI'), \
             patch('agent.WeatherTool'), \
             patch('agent.RAGTool'), \
             patch('agent.ChatDatabase'):
            return AgentPipeline()

    # FIXED TEST 1
    @patch('agent.StrOutputParser')
    @patch('agent.ChatPromptTemplate')
    def test_classify_intent_weather(self, mock_prompt, mock_parser, agent):
        """Test intent classification for weather queries"""
        # Mock the entire chain to return "weather"
        mock_chain = Mock()
        mock_chain.invoke.return_value = "weather"
        mock_prompt.from_template.return_value.__or__.return_value.__or__.return_value = mock_chain
        
        state = {
            "query": "What's the weather in London?",
            "chat_history": [], "intent": "", "city": "", "weather_data": {},
            "rag_response": {}, "final_answer": "", "error": ""
        }
        
        result = agent._classify_intent(state)
        assert result["intent"] == "weather"
    
    @patch('agent.StrOutputParser')
    @patch('agent.ChatPromptTemplate')
    def test_classify_intent_document(self, mock_prompt, mock_parser, agent):
        """Test intent classification for document queries"""
        mock_chain = Mock()
        mock_chain.invoke.return_value = "document"
        # This mocks the 'prompt | llm | parser' chain
        mock_prompt.from_template.return_value.__or__.return_value.__or__.return_value = mock_chain
        
        state = {
            "query": "What does the PDF say about transformers?",
            "chat_history": [], "intent": "", "city": "", "weather_data": {},
            "rag_response": {}, "final_answer": "", "error": ""
        }
        
        result = agent._classify_intent(state)
        assert result["intent"] == "document"
    
    # FIXED TEST 2
    @patch('agent.StrOutputParser')
    @patch('agent.ChatPromptTemplate')
    def test_extract_city(self, mock_prompt, mock_parser, agent):
        """Test city extraction from query"""
        # Mock the entire chain to return "Paris"
        mock_chain = Mock()
        mock_chain.invoke.return_value = "Paris"
        mock_prompt.from_template.return_value.__or__.return_value.__or__.return_value = mock_chain
        
        state = {
            "query": "How's the weather in Paris?",
            "chat_history": [], "intent": "weather", "city": "", "weather_data": {},
            "rag_response": {}, "final_answer": "", "error": ""
        }
        
        result = agent._extract_city(state)
        assert result["city"] == "Paris"

    def test_fetch_weather_success(self, agent):
        """Test successful weather fetching"""
        agent.weather_tool.get_weather = Mock(return_value={
            "city": "Tokyo", "temperature": 22, "description": "clear sky",
            "humidity": 60, "wind_speed": 3.5, "country": "JP"
        })
        
        state = {
            "query": "Weather in Tokyo?", "chat_history": [], "intent": "weather",
            "city": "Tokyo", "weather_data": {}, "rag_response": {},
            "final_answer": "", "error": ""
        }
        
        result = agent._fetch_weather(state)
        
        assert result["weather_data"]["city"] == "Tokyo"
        assert result["weather_data"]["temperature"] == 22
        assert not result.get("error")

    def test_fetch_weather_failure(self, agent):
        """Test weather fetching with API error"""
        agent.weather_tool.get_weather = Mock(side_effect=Exception("API Error"))
        
        state = {
            "query": "Weather in InvalidCity?", "chat_history": [], "intent": "weather",
            "city": "InvalidCity", "weather_data": {}, "rag_response": {},
            "final_answer": "", "error": ""
        }
        
        result = agent._fetch_weather(state)
        
        assert "Weather fetch failed" in result["error"]
        assert result["weather_data"] == {}
    
    def test_query_documents(self, agent):
        """Test document querying"""
        agent.rag_tool.query = Mock(return_value={
            "answer": "The transformer is a neural network architecture.",
            "sources": [{"content": "...", "metadata": {}}]
        })
        
        state = {
            "query": "What is a transformer?", "chat_history": [], "intent": "document",
            "city": "", "weather_data": {}, "rag_response": {},
            "final_answer": "", "error": ""
        }
        
        result = agent._query_documents(state)
        
        assert "transformer" in result["rag_response"]["answer"].lower()
        assert len(result["rag_response"]["sources"]) > 0
    
    def test_route_intent_weather(self, agent):
        """Test routing for weather intent"""
        state = {"intent": "weather"}
        result = agent._route_intent(state)
        assert result == "weather"
    
    def test_route_intent_document(self, agent):
        """Test routing for document intent"""
        state = {"intent": "document"}
        result = agent._route_intent(state)
        assert result == "document"
    
    # FIXED TEST 3
    @patch('agent.StrOutputParser')
    @patch('agent.ChatPromptTemplate')
    def test_generate_response_weather(self, mock_prompt, mock_parser, agent):
        """Test response generation for weather"""
        # Mock the entire chain
        mock_chain = Mock()
        mock_chain.invoke.return_value = "It's 22°C and sunny in Tokyo."
        mock_prompt.from_template.return_value.__or__.return_value.__or__.return_value = mock_chain
        
        state = {
            "query": "Weather in Tokyo?", "chat_history": [], "intent": "weather",
            "city": "Tokyo",
            "weather_data": {
                "city": "Tokyo", "country": "JP", "temperature": 22,
                "description": "clear sky", "humidity": 60, "wind_speed": 3.5
            },
            "rag_response": {}, "final_answer": "", "error": ""
        }
        
        result = agent._generate_response(state)
        assert "Tokyo" in result["final_answer"]

    def test_generate_response_document(self, agent):
        """Test response generation for documents"""
        state = {
            "query": "What is a transformer?", "chat_history": [], "intent": "document",
            "city": "", "weather_data": {},
            "rag_response": {
                "answer": "A transformer is a neural network architecture.",
                "sources": []
            },
            "final_answer": "", "error": ""
        }
        
        result = agent._generate_response(state)
        assert result["final_answer"] == "A transformer is a neural network architecture."

if __name__ == "__main__":
    pytest.main([__file__, "-v"])