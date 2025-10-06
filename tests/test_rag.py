"""
Unit tests for RAGTool
Tests PDF loading, retrieval, and querying with mocked dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rag import RAGTool


class TestRAGTool:
    """Test suite for RAGTool class"""
    
    @pytest.fixture
    def rag_tool(self):
        """Create RAGTool instance with mocked Qdrant client"""
        with patch('rag.QdrantClient'):
            tool = RAGTool()
            return tool
    
    def test_sanitize_collection_name(self, rag_tool):
        """Test collection name sanitization"""
        # Test with spaces and special characters
        name1 = rag_tool._sanitize_collection_name("My Document (2024).pdf")
        assert name1 == "pdf_my_document__2024_"
        
        # Test with very long name
        long_name = "A" * 100 + ".pdf"
        name2 = rag_tool._sanitize_collection_name(long_name)
        assert len(name2) <= 54  # pdf_ + 50 chars
        
        # Test case sensitivity
        name3 = rag_tool._sanitize_collection_name("TEST.pdf")
        assert name3 == "pdf_test"
    
    @patch('rag.PyPDFLoader')
    @patch('rag.QdrantVectorStore')
    def test_load_pdf_success(self, mock_vectorstore_class, mock_loader, rag_tool):
        """Test successful PDF loading"""
        # Mock PDF loader
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"page": 1}
        mock_loader.return_value.load.return_value = [mock_doc]
        
        # Mock Qdrant client
        rag_tool.client.get_collections.return_value.collections = []
        rag_tool.client.create_collection = Mock()

        #  Mock vectorstore instance
        mock_vectorstore_instance = Mock()
        mock_vectorstore_class.from_documents.return_value = mock_vectorstore_instance
        mock_vectorstore_class.return_value = mock_vectorstore_instance
        
        # Test
        result = rag_tool.load_pdf("test.pdf")
        
        assert result is True
        assert rag_tool.current_pdf_name == "test.pdf"
        assert rag_tool.current_collection_name == "pdf_test"
    
    @patch('rag.PyPDFLoader')
    def test_load_pdf_failure(self, mock_loader, rag_tool):
        """Test PDF loading failure"""
        # Mock loader to raise exception
        mock_loader.side_effect = Exception("File not found")
        
        result = rag_tool.load_pdf("nonexistent.pdf")
        
        assert result is False
    
    def test_switch_to_pdf_exists(self, rag_tool):
        """Test switching to existing PDF collection"""
        # Mock collection exists
        mock_collection = Mock()
        mock_collection.name = "pdf_test"
        rag_tool.client.get_collections.return_value.collections = [mock_collection]
        
        with patch('rag.QdrantVectorStore') as mock_vs:
            result = rag_tool.switch_to_pdf("test.pdf")
            
            assert result is True
            assert rag_tool.current_pdf_name == "test.pdf"
    
    def test_switch_to_pdf_not_exists(self, rag_tool):
        """Test switching to non-existent PDF collection"""
        # Mock collection doesn't exist
        rag_tool.client.get_collections.return_value.collections = []
        
        result = rag_tool.switch_to_pdf("test.pdf")
        
        assert result is False
    
    @patch('flashrank.Ranker')
    def test_rerank_documents(self, mock_ranker_class, rag_tool):
        """Test document reranking"""
        # Create mock documents
        docs = [Mock(page_content=f"Content {i}") for i in range(5)]
        
        # Mock ranker
        mock_ranker = Mock()
        mock_ranker.rerank.return_value = [
            {"id": 2, "score": 0.9},
            {"id": 0, "score": 0.8},
            {"id": 4, "score": 0.7}
        ]
        mock_ranker_class.return_value = mock_ranker
        
        # Test
        result = rag_tool._rerank_documents("test query", docs)
        
        assert len(result) == 3
        assert result[0].page_content == "Content 2"
        assert result[1].page_content == "Content 0"
    
    @patch('rag.StrOutputParser')
    @patch('rag.ChatPromptTemplate')
    def test_query_no_vectorstore(self, mock_prompt, mock_parser, rag_tool):
        """Test query when no PDF is loaded"""
        rag_tool.vectorstore = None
        
        result = rag_tool.query("What is this about?")
        
        assert "No PDF loaded" in result["answer"]
        assert result["sources"] == []

    @patch('rag.StrOutputParser')
    @patch('rag.ChatPromptTemplate')
    @patch('flashrank.Ranker')
    def test_query_with_results(self, mock_ranker_class, mock_prompt_class, mock_parser_class, rag_tool):
        """Test successful query with results"""
        # Setup mocks for documents and retriever
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"page": 1}
        
        mock_retriever = Mock()
        mock_retriever.invoke.return_value = [mock_doc]
        
        rag_tool.vectorstore = Mock()
        rag_tool.vectorstore.as_retriever.return_value = mock_retriever
        rag_tool.current_collection_name = "pdf_test"
        
        # Mock reranker
        mock_ranker = Mock()
        mock_ranker.rerank.return_value = [{"id": 0, "score": 0.9}]
        mock_ranker_class.return_value = mock_ranker
        
        # Mock the entire LangChain chain
        mock_chain = Mock()
        mock_chain.invoke.return_value = "This is the answer"
        
        # Mock the chain construction (prompt | llm | parser)
        # This simulates the `__or__` method used for the `|` pipe operator in LCEL
        mock_prompt_instance = mock_prompt_class.from_messages.return_value
        mock_prompt_instance.__or__.return_value.__or__.return_value = mock_chain
        
        # Test the query method
        result = rag_tool.query("What is this about?")
        
        assert result["answer"] == "This is the answer"
        assert len(result["sources"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])