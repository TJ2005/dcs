"""
SENTINEL Phase 0 - Victim Chatbot Backend
Flask server for intentionally vulnerable chatbot
NO SECURITY MEASURES - DIRECT PASSTHROUGH TO LLM
"""
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openrouter_client import OpenRouterClient
import logging
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS - no restrictions

# Initialize OpenRouter client
try:
    client = OpenRouterClient()
except ValueError as e:
    logger.error(f"Failed to initialize OpenRouter client: {e}")
    client = None


def run_async(coro):
    """Run async function in Flask context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route("/health", methods=["GET"])
def health() -> tuple[Dict[str, Any], int]:
    """
    Health check endpoint.
    
    NO AUTHENTICATION - no token required.
    
    Returns:
        JSON status response
    """
    return (
        {
            "status": "ok",
            "model": client.model if client else "unknown",
            "version": "0.1.0",
        },
        200,
    )


@app.route("/chat", methods=["POST"])
def chat() -> tuple[Dict[str, Any], int]:
    """
    Chat endpoint - receive message and send to LLM.
    
    NO INPUT VALIDATION - messages are passed directly to LLM.
    NO RATE LIMITING - unlimited requests allowed.
    NO AUTHENTICATION - no user verification.
    
    Expected JSON body:
        {
            "message": "user message",
            "temperature": 0.7 (optional)
        }
    
    Returns:
        JSON with response from LLM
    """
    if not client:
        return {"error": "OpenRouter client not initialized"}, 500

    try:
        # Get request data - NO VALIDATION
        data = request.get_json()
        if not data:
            return {"error": "No JSON body provided"}, 400

        message = data.get("message", "")
        if not message:
            return {"error": "No message provided"}, 400

        temperature = data.get("temperature", 0.7)

        # INTENTIONALLY NO VALIDATION:
        # - No message length limits
        # - No content filtering
        # - No injection checks
        # - No rate limiting per user
        # - No authentication checks

        logger.info(f"Chat request received (length: {len(message)})")

        # Send directly to LLM - ZERO SECURITY
        response = run_async(client.chat(message, temperature=temperature))

        return {
            "status": "success",
            "response": response,
            "message_length": len(message),
        }, 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return {
            "error": str(e),
            "status": "error",
        }, 500


@app.route("/test", methods=["GET"])
def test() -> tuple[Dict[str, Any], int]:
    """
    Test endpoint for quick API verification.
    
    NO AUTHENTICATION - no token required.
    
    Returns:
        JSON test response
    """
    return {
        "status": "test_ok",
        "message": "Backend is running and ready for attacks",
        "vulnerable": True,
        "security_level": "NONE",
    }, 200


@app.errorhandler(404)
def not_found(error) -> tuple[Dict[str, Any], int]:
    """Handle 404 errors."""
    return {"error": "Endpoint not found"}, 404


@app.errorhandler(500)
def internal_error(error) -> tuple[Dict[str, Any], int]:
    """Handle 500 errors."""
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting SENTINEL Phase 0 Victim Chatbot on port {port}")
    logger.warning("⚠️  THIS IS AN INTENTIONALLY VULNERABLE SYSTEM")
    logger.warning("⚠️  NO SECURITY MEASURES IMPLEMENTED")
    logger.warning("⚠️  FOR EDUCATIONAL PURPOSES ONLY")
    app.run(debug=True, port=port, host="0.0.0.0")
