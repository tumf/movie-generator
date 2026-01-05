"""Tests for MCP to OpenAI tool conversion."""

from movie_generator.agent.tool_converter import convert_mcp_tools_to_openai


class TestToolConverter:
    """Test suite for convert_mcp_tools_to_openai function."""

    def test_empty_tool_list(self) -> None:
        """Test conversion with empty tool list."""
        result = convert_mcp_tools_to_openai([])
        assert result == []

    def test_single_tool_conversion(self) -> None:
        """Test conversion of a single tool."""
        mcp_tools = [
            {
                "name": "firecrawl_scrape",
                "description": "Scrape a URL and return markdown content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                        "formats": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Output formats",
                        },
                    },
                    "required": ["url"],
                },
            }
        ]

        result = convert_mcp_tools_to_openai(mcp_tools)

        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "firecrawl_scrape"
        assert result[0]["function"]["description"] == "Scrape a URL and return markdown content"
        assert result[0]["function"]["parameters"] == mcp_tools[0]["inputSchema"]

    def test_multiple_tools_conversion(self) -> None:
        """Test conversion of multiple tools."""
        mcp_tools = [
            {
                "name": "tool1",
                "description": "First tool",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "tool2",
                "description": "Second tool",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

        result = convert_mcp_tools_to_openai(mcp_tools)

        assert len(result) == 2
        assert result[0]["function"]["name"] == "tool1"
        assert result[1]["function"]["name"] == "tool2"

    def test_tool_with_complex_schema(self) -> None:
        """Test conversion with complex JSON schema."""
        mcp_tools = [
            {
                "name": "complex_tool",
                "description": "A complex tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nested": {
                            "type": "object",
                            "properties": {
                                "field1": {"type": "string"},
                                "field2": {"type": "integer"},
                            },
                        },
                        "array_field": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["nested"],
                    "additionalProperties": False,
                },
            }
        ]

        result = convert_mcp_tools_to_openai(mcp_tools)

        assert result[0]["function"]["parameters"]["type"] == "object"
        assert "nested" in result[0]["function"]["parameters"]["properties"]
        assert result[0]["function"]["parameters"]["required"] == ["nested"]

    def test_tool_with_missing_fields(self) -> None:
        """Test conversion when optional fields are missing."""
        mcp_tools = [
            {
                "name": "minimal_tool",
                # Missing description
                # Missing inputSchema
            }
        ]

        result = convert_mcp_tools_to_openai(mcp_tools)

        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "minimal_tool"
        assert result[0]["function"]["description"] == ""
        assert result[0]["function"]["parameters"] == {}
