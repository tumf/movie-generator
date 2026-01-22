"""Core script generation functionality.

Provides library functions for script generation that can be called
directly by worker processes or other Python code, without CLI overhead.
"""

import asyncio
import logging
from collections.abc import Callable
from pathlib import Path

import yaml

from ..agent.agent_loop import AgentLoop
from ..config import Config, load_config
from ..content.fetcher import fetch_url_sync
from ..content.parser import parse_html
from ..exceptions import MCPError
from ..mcp.client import MCPClient
from ..mcp.config import load_mcp_config
from .generator import generate_script

logger = logging.getLogger(__name__)


async def generate_script_from_url(
    url: str,
    output_dir: Path,
    script_filename: str = "script.yaml",
    config_path: Path | None = None,
    config: Config | None = None,
    api_key: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Path:
    """Generate script from URL.

    Fetches content from the URL, generates narration script using LLM,
    and saves it to script.yaml.

    Args:
        url: Blog URL to convert.
        output_dir: Output directory for script.yaml.
        script_filename: Name of the script file (default: "script.yaml").
        config_path: Path to config file (mutually exclusive with config).
        config: Config object (mutually exclusive with config_path).
        api_key: OpenRouter API key (overrides config/environment).
        progress_callback: Optional callback(current, total, message) called during generation.

    Returns:
        Path to generated script.yaml file.

    Raises:
        ValueError: If config_path and config are both provided.
        RuntimeError: If content fetching or script generation fails.

    Example:
        >>> import asyncio
        >>> from pathlib import Path
        >>>
        >>> async def main():
        ...     script_path = await generate_script_from_url(
        ...         url="https://example.com/blog",
        ...         output_dir=Path("output"),
        ...         api_key="your-api-key",
        ...         progress_callback=lambda c, t, m: print(f"{c}/{t}: {m}")
        ...     )
        ...     return script_path
        >>>
        >>> asyncio.run(main())
    """
    # Validate arguments
    if config_path and config:
        raise ValueError("Cannot specify both config_path and config")

    # Load configuration
    if config is None:
        cfg = load_config(config_path) if config_path else Config()
    else:
        cfg = config

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = output_dir / script_filename

    if progress_callback:
        progress_callback(0, 100, "Fetching content from URL...")

    # Fetch content
    try:
        html_content = fetch_url_sync(url)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch URL: {e}") from e

    if progress_callback:
        progress_callback(20, 100, "Parsing HTML content...")

    # Parse HTML
    try:
        parsed = parse_html(html_content, base_url=url)
    except Exception as e:
        raise RuntimeError(f"Failed to parse HTML: {e}") from e

    if progress_callback:
        progress_callback(40, 100, "Generating script with LLM...")

    # Prepare images metadata for script generation
    images_metadata = None
    if parsed.images:
        images_metadata = [
            img.model_dump(
                include={"src", "alt", "title", "aria_describedby"},
                exclude_none=True,
            )
            for img in parsed.images
        ]

    # Prepare personas if defined (enables multi-speaker mode automatically)
    personas_for_script = None
    if cfg.personas:
        personas_for_script = [
            p.model_dump(include={"id", "name", "character"}) for p in cfg.personas
        ]

    # Prepare persona pool config for random selection
    pool_config = None
    if cfg.persona_pool:
        pool_config = cfg.persona_pool.model_dump()
        logger.info(
            f"Persona pool enabled: will select {cfg.persona_pool.count} "
            f"from {len(cfg.personas)} personas"
        )

    # Generate script
    try:
        script = await generate_script(
            content=parsed.markdown,
            title=parsed.metadata.title,
            description=parsed.metadata.description,
            character=cfg.narration.character,
            style=cfg.narration.style,
            api_key=api_key,
            model=cfg.content.llm.model,
            base_url=cfg.content.llm.base_url,
            images=images_metadata,
            personas=personas_for_script,
            pool_config=pool_config,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate script: {e}") from e

    if progress_callback:
        progress_callback(80, 100, "Saving script to file...")

    # Save script to YAML using Pydantic's model_dump()
    # This ensures all fields are included automatically
    script_dict = script.model_dump(exclude_none=True)
    with open(script_path, "w", encoding="utf-8") as f:
        yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)

    if progress_callback:
        progress_callback(100, 100, "Script generation complete")

    return script_path


def generate_script_from_url_sync(
    url: str,
    output_dir: Path,
    script_filename: str = "script.yaml",
    config_path: Path | None = None,
    config: Config | None = None,
    api_key: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Path:
    """Synchronous wrapper for generate_script_from_url.

    This is a convenience function that runs the async version in an event loop.
    Use this when calling from synchronous code.

    Args:
        Same as generate_script_from_url.

    Returns:
        Path to generated script.yaml file.

    Example:
        >>> from pathlib import Path
        >>> script_path = generate_script_from_url_sync(
        ...     url="https://example.com/blog",
        ...     output_dir=Path("output"),
        ...     api_key="your-api-key"
        ... )
    """
    return asyncio.run(
        generate_script_from_url(
            url=url,
            output_dir=output_dir,
            script_filename=script_filename,
            config_path=config_path,
            config=config,
            api_key=api_key,
            progress_callback=progress_callback,
        )
    )


async def generate_script_from_url_with_agent(
    url: str,
    output_dir: Path,
    mcp_config_path: Path,
    script_filename: str = "script.yaml",
    config_path: Path | None = None,
    config: Config | None = None,
    api_key: str | None = None,
    mcp_server_name: str = "firecrawl",
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Path:
    """Generate script from URL using MCP agent.

    Uses an LLM agent that can autonomously select and execute MCP tools
    to fetch and analyze content before generating the script.

    Args:
        url: Blog URL to convert.
        output_dir: Output directory for script.yaml.
        mcp_config_path: Path to MCP configuration file.
        script_filename: Name of the script file (default: "script.yaml").
        config_path: Path to config file (mutually exclusive with config).
        config: Config object (mutually exclusive with config_path).
        api_key: OpenRouter API key (overrides config/environment).
        mcp_server_name: Name of MCP server to use (default: "firecrawl").
        progress_callback: Optional callback(current, total, message) called during generation.

    Returns:
        Path to generated script.yaml file.

    Raises:
        ValueError: If config_path and config are both provided.
        MCPError: If MCP agent execution fails.
        RuntimeError: If script generation fails.

    Example:
        >>> import asyncio
        >>> from pathlib import Path
        >>>
        >>> async def main():
        ...     script_path = await generate_script_from_url_with_agent(
        ...         url="https://example.com/blog",
        ...         output_dir=Path("output"),
        ...         mcp_config_path=Path("mcp.jsonc"),
        ...         api_key="your-api-key",
        ...         progress_callback=lambda c, t, m: print(f"{c}/{t}: {m}")
        ...     )
        ...     return script_path
        >>>
        >>> asyncio.run(main())
    """
    # Validate arguments
    if config_path and config:
        raise ValueError("Cannot specify both config_path and config")

    # Load configuration
    if config is None:
        cfg = load_config(config_path) if config_path else Config()
    else:
        cfg = config

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = output_dir / script_filename

    if progress_callback:
        progress_callback(0, 100, "Loading MCP configuration...")

    # Load MCP configuration
    try:
        mcp_config = load_mcp_config(mcp_config_path)
    except Exception as e:
        raise MCPError(f"Failed to load MCP config: {e}") from e

    if progress_callback:
        progress_callback(10, 100, "Connecting to MCP server...")

    # Connect to MCP server and run agent
    async with MCPClient(mcp_config, mcp_server_name) as mcp_client:
        if progress_callback:
            progress_callback(20, 100, "Running agent to fetch content...")

        # Create task prompt for the agent
        task_prompt = f"""
Fetch and analyze the content from the following URL: {url}

Your task is to:
1. Scrape the URL to get the full content
2. Extract the main article/blog content in markdown format
3. Return the complete markdown content

Please use the available tools to accomplish this task.
""".strip()

        # Get API key from argument or environment
        import os

        openrouter_api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not openrouter_api_key:
            raise ValueError(
                "OpenRouter API key is required (set OPENROUTER_API_KEY or pass api_key)"
            )

        # Run agent loop
        async with AgentLoop(
            mcp_client=mcp_client,
            openrouter_api_key=openrouter_api_key,
            model=cfg.content.llm.model,
            base_url=cfg.content.llm.base_url,
        ) as agent:
            try:
                markdown_content = await agent.run(task_prompt)
            except Exception as e:
                raise MCPError(f"Agent execution failed: {e}") from e

        if progress_callback:
            progress_callback(60, 100, "Generating script with LLM...")

        # Parse the markdown content to extract metadata
        # Note: We're using the markdown directly from the agent
        # In a real scenario, you might want to parse it further
        title = "Generated Video"  # Default title
        description = ""

        # Prepare personas if defined (enables multi-speaker mode automatically)
        personas_for_script = None
        if cfg.personas:
            personas_for_script = [
                p.model_dump(include={"id", "name", "character"}) for p in cfg.personas
            ]

        # Prepare persona pool config for random selection
        pool_config = None
        if cfg.persona_pool:
            pool_config = cfg.persona_pool.model_dump()
            logger.info(
                f"Persona pool enabled: will select {cfg.persona_pool.count} "
                f"from {len(cfg.personas)} personas"
            )

        # Generate script
        try:
            script = await generate_script(
                content=markdown_content,
                title=title,
                description=description,
                character=cfg.narration.character,
                style=cfg.narration.style,
                api_key=api_key,
                model=cfg.content.llm.model,
                base_url=cfg.content.llm.base_url,
                images=None,  # Agent doesn't extract images metadata yet
                personas=personas_for_script,
                pool_config=pool_config,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate script: {e}") from e

        if progress_callback:
            progress_callback(90, 100, "Saving script to file...")

        # Save script to YAML using Pydantic's model_dump()
        script_dict = script.model_dump(exclude_none=True)
        with open(script_path, "w", encoding="utf-8") as f:
            yaml.dump(script_dict, f, allow_unicode=True, sort_keys=False)

        if progress_callback:
            progress_callback(100, 100, "Script generation complete")

        logger.info(f"Script generated successfully using agent: {script_path}")
        return script_path


def generate_script_from_url_with_agent_sync(
    url: str,
    output_dir: Path,
    mcp_config_path: Path,
    script_filename: str = "script.yaml",
    config_path: Path | None = None,
    config: Config | None = None,
    api_key: str | None = None,
    mcp_server_name: str = "firecrawl",
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> Path:
    """Synchronous wrapper for generate_script_from_url_with_agent.

    This is a convenience function that runs the async version in an event loop.
    Use this when calling from synchronous code.

    Args:
        Same as generate_script_from_url_with_agent.

    Returns:
        Path to generated script.yaml file.

    Example:
        >>> from pathlib import Path
        >>> script_path = generate_script_from_url_with_agent_sync(
        ...     url="https://example.com/blog",
        ...     output_dir=Path("output"),
        ...     mcp_config_path=Path("mcp.jsonc"),
        ...     api_key="your-api-key"
        ... )
    """
    return asyncio.run(
        generate_script_from_url_with_agent(
            url=url,
            output_dir=output_dir,
            mcp_config_path=mcp_config_path,
            script_filename=script_filename,
            config_path=config_path,
            config=config,
            api_key=api_key,
            mcp_server_name=mcp_server_name,
            progress_callback=progress_callback,
        )
    )
