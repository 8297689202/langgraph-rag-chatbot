import os
from typing import TypedDict, Literal, List
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage


from weather import WeatherTool
from rag import RAGTool
from database import ChatDatabase

load_dotenv()


# Define the state that flows through the graph
class AgentState(TypedDict):
    query: str
    chat_history: List
    intent: str
    city: str
    weather_data: dict
    rag_response: dict
    final_answer: str
    error: str


class AgentPipeline:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.weather_tool = WeatherTool()
        self.rag_tool = RAGTool()
        self.graph = self._build_graph()
    
    def _classify_intent(self, state: AgentState) -> AgentState:
        """
        Classify user intent: weather or document query
        """
        query = state["query"]
        
        intent_prompt = ChatPromptTemplate.from_template(
            """You are an intent classifier. Analyze the user's query and classify it as either:
                - "weather": If asking about weather, temperature, climate, or meteorological conditions
                - "document": If asking about document content, PDFs, or general knowledge questions

                Respond with ONLY one word: either "weather" or "document"

                Query: {query}

                Intent:
                """
        )
        
        try:
            chain = intent_prompt | self.llm | StrOutputParser()
            intent = chain.invoke({"query": query}).strip().lower()
            
            # Validate intent
            if intent not in ["weather", "document"]:
                intent = "document"  # Default fallback
            
            state["intent"] = intent
            print(f"\n[Decision Node] Intent classified as: {intent}")
            
        except Exception as e:
            state["error"] = f"Intent classification failed: {str(e)}"
            state["intent"] = "document"
        
        return state
    
    def _extract_city(self, state: AgentState) -> AgentState:
        """
        Extract city name from weather query
        """
        query = state["query"]
        
        city_prompt = ChatPromptTemplate.from_template(
            """Extract ONLY the city name from this weather query. 
Respond with just the city name, nothing else.

Query: {query}

City:"""
        )
        
        try:
            chain = city_prompt | self.llm | StrOutputParser()
            city = chain.invoke({"query": query}).strip()
            state["city"] = city
            print(f"[Weather Node] Extracted city: {city}")
            
        except Exception as e:
            state["error"] = f"City extraction failed: {str(e)}"
            state["city"] = ""
        
        return state
    
    def _fetch_weather(self, state: AgentState) -> AgentState:
        """
        Fetch weather data using WeatherTool
        """
        city = state["city"]
        
        try:
            weather_data = self.weather_tool.get_weather(city)
            state["weather_data"] = weather_data
            print(f"[Weather Node] Fetched weather for {city}")
            
        except Exception as e:
            state["error"] = f"Weather fetch failed: {str(e)}"
            state["weather_data"] = {}
        
        return state
    
    def _query_documents(self, state: AgentState) -> AgentState:
        """
        Query documents using RAG
        """
        query = state["query"]
        chat_history = state.get("chat_history", [])
        
        try:
            # Convert chat history to proper format
            formatted_history = []
            for msg in chat_history:
                if msg["role"] == "human":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "ai":
                    formatted_history.append(AIMessage(content=msg["content"]))
            
            rag_response = self.rag_tool.query(query, formatted_history)
            state["rag_response"] = rag_response
            print(f"[RAG Node] Retrieved {len(rag_response.get('sources', []))} sources")
            
        except Exception as e:
            state["error"] = f"RAG query failed: {str(e)}"
            state["rag_response"] = {
                "answer": "Failed to retrieve information from documents.",
                "sources": []
            }
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """
        Generate final response based on intent
        """
        intent = state["intent"]
        query = state["query"]
        
        try:
            if intent == "weather":
                weather_data = state.get("weather_data", {})
                print(f"DEBUG - Weather data received: {weather_data}")
                
                if weather_data:
                    # Format weather data nicely
                    weather_text = f"""City: {weather_data['city']}, {weather_data['country']}
                    Temperature: {weather_data['temperature']}°C
                    Conditions: {weather_data['description']}
                    Humidity: {weather_data['humidity']}%
                    Wind Speed: {weather_data['wind_speed']} m/s"""
                    
                    # Generate natural response
                    response_prompt = ChatPromptTemplate.from_template(
                        """
                        You are a helpful weather assistant. Based on the weather data below, provide a natural, conversational response to the user's question.
                        User Question: {query} Weather Data:{weather_data} Response:
                        """
                    )
                    
                    chain = response_prompt | self.llm | StrOutputParser()
                    answer = chain.invoke({
                        "query": query,
                        "weather_data": weather_text
                    })
                    
                    state["final_answer"] = answer
                else:
                    state["final_answer"] = "I couldn't fetch the weather data. Please try again."
            
            else:  # document intent
                rag_response = state.get("rag_response", {})
                state["final_answer"] = rag_response.get("answer", "No answer available.")
            
            # print(f"[Response Node] Generated final answer")
            
        except Exception as e:
            state["error"] = f"Response generation failed: {str(e)}"
            print(f"ERROR: {str(e)}")  
            state["final_answer"] = "An error occurred while generating the response."
        
        return state
    
    def _route_intent(self, state: AgentState) -> Literal["weather", "document"]:
        """
        Route to appropriate node based on intent
        """
        return state["intent"]
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("extract_city", self._extract_city)
        workflow.add_node("fetch_weather", self._fetch_weather)
        workflow.add_node("query_documents", self._query_documents)
        workflow.add_node("generate_response", self._generate_response)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add conditional routing from intent classification
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_intent,
            {
                "weather": "extract_city",
                "document": "query_documents"
            }
        )
        
        # Weather flow: extract_city -> fetch_weather -> generate_response
        workflow.add_edge("extract_city", "fetch_weather")
        workflow.add_edge("fetch_weather", "generate_response")
        
        # Document flow: query_documents -> generate_response
        workflow.add_edge("query_documents", "generate_response")
        
        # End after response generation
        workflow.add_edge("generate_response", END)
        
        # Compile graph
        return workflow.compile()
  
    def run(self, query: str, session_id: str, chat_history: List = None) -> dict:

        """
        Run the agent pipeline
        
        Args:
            query: User query
            session_id: Session identifier
            chat_history: List of previous messages [{"role": "human/ai", "content": "..."}]
            
        Returns:
            Final state with answer and metadata
        """
        if chat_history is None:
            chat_history = []
        
        initial_state = {
            "query": query,
            "chat_history": chat_history,
            "intent": "",
            "city": "",
            "weather_data": {},
            "rag_response": {},
            "final_answer": "",
            "error": ""
        }
        
        print(f"\n{'='*60}")
        print(f"User Query: {query}")
        print(f"{'='*60}")
        
        # Execute graph
        final_state = self.graph.invoke(initial_state)
        
        # Determine which PDF was used (if document intent)
        pdf_name = None
        if final_state["intent"] == "document" and self.rag_tool.vectorstore:
            # Try to get PDF name from vectorstore or track it separately
            # For now, we'll pass it from the UI
            pdf_name = getattr(self.rag_tool, 'current_pdf_name', None)
        
        # Save to database with PDF info
        db = ChatDatabase()
        db.insert_message(
            session_id=session_id,
            user_query=query,
            ai_response=final_state["final_answer"],
            intent=final_state["intent"],
            pdf_name=pdf_name
        )

        print(f"{'='*60}\n")
        
        return final_state


# Test the agent
if __name__ == "__main__":
    agent = AgentPipeline()

    agent.rag_tool.load_pdf("sample.pdf")
    db = ChatDatabase()  
    test_session = "test_session_001"

    
    # Test 1: Weather query
    # print("\n--- Test 1: Weather Query ---")
    # result = agent.run("What's the humidity  in Delhi ?")
    # print(f"\nAnswer: {result['final_answer']}")
    
    # # Test 2: Document query (requires RAG to have loaded a PDF)
    # print("\n--- Question 1 ---")
    # history = db.get_session_history(test_session)
    # result = agent.run("how many encoders are used in this architecture ?", session_id=test_session, chat_history=history)
    # print(f"Answer: {result['final_answer']}")

    # # # Test 3: Follow-up with history
    # print("\n--- Question 3 ---")
    # history = db.get_session_history(test_session)  # Load updated history
    # result = agent.run("what is the dimension of k,q and v vectors in the paper?", session_id=test_session, chat_history=history)
    # print(f"Answer: {result['final_answer']}")