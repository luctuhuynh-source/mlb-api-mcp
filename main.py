import argparse
import inspect
import os
import warnings

import uvicorn
import fastmcp
from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from generic_api import setup_generic_tools
from mlb_api import setup_mlb_tools

# Host header allow-list for FastMCP's built-in DNS-rebinding guard.
#
# FastMCP 3.x wraps the whole HTTP app in a HostOriginGuardMiddleware that
# validates the incoming Host header and returns "421 Misdirected Request" for
# any host not on its allow-list. Its built-in defaults are localhost-only
# ("127.0.0.1", "localhost", "::1"), so every request that arrives with the
# public Railway domain in the Host header (i.e. all real traffic, plus
# Railway's own healthcheck probes) is rejected with a 421 -- on every path,
# including /docs and /health.
#
# We therefore pass the Railway hostnames to FastMCP so the guard allows them.
# localhost/127.0.0.1/::1 remain allowed via FastMCP's own defaults. Additional
# hostnames can be supplied via the ALLOWED_HOSTS environment variable
# (comma-separated). fnmatch-style wildcards are supported (e.g. "*.railway.app").
DEFAULT_ALLOWED_HOSTS = [
    "mlb-api-mcp-production.up.railway.app",  # public Railway domain
    "*.up.railway.app",                       # other/preview Railway domains
    "*.railway.app",                          # Railway internal hosts (healthcheck.railway.app, etc.)
]


def get_allowed_hosts():
    """Return the Host allow-list to hand to FastMCP's Host/Origin guard.

    Starts from the Railway defaults and appends any hosts from the ALLOWED_HOSTS
    environment variable (comma-separated). localhost is always permitted by
    FastMCP's own built-in defaults, so it is not repeated here.
    """
    hosts = list(DEFAULT_ALLOWED_HOSTS)
    raw = os.environ.get("ALLOWED_HOSTS")
    if raw:
        for h in raw.split(","):
            h = h.strip()
            if h and h not in hosts:
                hosts.append(h)
    return hosts

# Suppress websockets deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets")

# Create FastMCP server instance
mcp = FastMCP("MLB API MCP Server")


async def get_tools_dict():
    """Return the server's registered tools as a {name: tool} dict.

    FastMCP renamed ``FastMCP.get_tools()`` (v2) to ``FastMCP.list_tools()`` (v3)
    and changed its return type from a ``dict[str, Tool]`` to a ``list[Tool]``.
    This helper works with both: it calls whichever method exists and normalizes
    to the dict shape that the custom routes below already iterate over.
    """
    if hasattr(mcp, "list_tools"):
        tools = await mcp.list_tools()  # FastMCP 3.x -> Sequence[Tool]
        return {tool.name: tool for tool in tools}
    return await mcp.get_tools()  # type: ignore[attr-defined]  # FastMCP 2.x -> dict[str, Tool]

# Setup all MLB and generic tools
setup_mlb_tools(mcp)
setup_generic_tools(mcp)

# Add custom routes to the MCP server for documentation and info
@mcp.custom_route("/", methods=["GET"])
async def root(request):
    """Root endpoint redirects to documentation"""
    return RedirectResponse(url="/docs")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "ok"})


@mcp.custom_route("/info", methods=["GET"])
async def mcp_info(request):
    """Information about the MCP server"""
    tools_list = await get_tools_dict()
    return JSONResponse(
        {
            "status": "running",
            "protocol": "mcp",
            "server_name": "MLB API MCP Server",
            "description": "Model Context Protocol server for MLB statistics and baseball data",
            "mcp_endpoint": "/mcp",
            "tools_available": len(tools_list),
            "note": "This is an MCP server. Use MCP-compatible clients to interact with the tools.",
        }
    )


@mcp.custom_route("/tools", methods=["GET"])
async def list_tools(request):
    """List available MCP tools"""
    tools = []
    tools_list = await get_tools_dict()
    for tool_name, tool in tools_list.items():
        tools.append(
            {
                "name": tool_name,
                "description": getattr(tool, "description", None)
                or "No description available",
                "parameters": getattr(tool, "parameters", None) or {},
            }
        )
    return JSONResponse({"tools": tools})

# Add a basic docs endpoint that provides information about available endpoints
@mcp.custom_route("/docs", methods=["GET"])
async def docs(request):
    """Basic documentation endpoint"""
    tools_list = await get_tools_dict()
    docs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLB API MCP Server Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .endpoint {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .method {{ font-weight: bold; color: #0066cc; }}
            .path {{ font-weight: bold; color: #cc6600; }}
            .tools {{ margin: 10px 0; }}
            .tool {{ margin: 5px 0; padding: 10px; background: #f5f5f5; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>MLB API MCP Server Documentation</h1>
        <p>A Model Context Protocol server that provides comprehensive access to MLB statistics and baseball data.</p>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/health</span>
            <p>Health check endpoint</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/info</span>
            <p>Information about the MCP server</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/tools</span>
            <p>List all available MCP tools</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/mcp</span>
            <p>MCP protocol endpoint for MCP-compatible clients</p>
        </div>
        
        <h2>Available MCP Tools ({len(tools_list)} total)</h2>
        <div class="tools">
    """
    for tool_name, tool in tools_list.items():
        description = getattr(tool, "description", None) or "No description available"
        docs_html += (
            f'<div class="tool"><strong>{tool_name}</strong>: {description}</div>'
        )
    docs_html += """
        </div>
        
        <h2>Usage</h2>
        <p>This server implements the Model Context Protocol (MCP). Use MCP-compatible clients to interact with the tools.</p>
        <p>For direct HTTP access, you can use the endpoints listed above.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=docs_html)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MLB API MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run server with HTTP transport (default: stdio transport)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000, env PORT takes priority)"
    )
    args = parser.parse_args()

    if args.http:
        # Environment variable takes priority over command line argument
        port = int(os.environ.get("PORT", args.port))

        print(f"Starting MLB API MCP Server on port {port}...")
        print(f"- Documentation: http://localhost:{port}/docs")
        print(f"- Health check: http://localhost:{port}/health")
        print(f"- MCP server info: http://localhost:{port}/info")
        print(f"- Tools list: http://localhost:{port}/tools")
        print(f"- MCP protocol: http://localhost:{port}/mcp")

        # Create middleware configuration
        from starlette.middleware import Middleware

        # CORS: allow browser-based MCP clients to reach the server.
        cors_middleware = Middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure this more restrictively in production
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id"],  # Allow client to read session ID
            max_age=86400,
        )

        # Configure FastMCP's built-in Host/Origin guard so it accepts the Railway
        # domain instead of answering "421 Misdirected Request" for every request.
        # The `allowed_hosts`/`host_origin_protection` parameters exist on FastMCP
        # 3.x's http_app(); they do not exist on 2.x (which has no such guard), so
        # we pass them only when the running FastMCP supports them.
        allowed_hosts = get_allowed_hosts()
        print(f"- Allowed hosts: {', '.join(allowed_hosts)}")

        http_app_kwargs = {"middleware": [cors_middleware]}
        if "allowed_hosts" in inspect.signature(mcp.http_app).parameters:
            http_app_kwargs["allowed_hosts"] = allowed_hosts

        # Get the Starlette app with middleware (using modern http_app method).
        # FastMCP mounts the streamable-HTTP transport at /mcp/ and serves it
        # directly. Do NOT add a path-rewrite middleware here: rewriting /mcp -> /mcp/
        # fights FastMCP's own redirect and produces an infinite 307 loop.
        app = mcp.http_app(**http_app_kwargs)

        # Run the MCP server with HTTP transport using uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    else:
        # Run with stdio transport (for Smithery)
        mcp.run(transport="stdio")
