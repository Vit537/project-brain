"""
Telegram Channel - Remote Notification & Chat Interface
Allows JARVIS to send notifications and receive commands via Telegram.

Setup:
1. Create a bot via @BotFather on Telegram
2. Set TELEGRAM_BOT_TOKEN in .env
3. Set TELEGRAM_CHAT_ID in .env (your personal chat ID)
   (Send /start to your bot, then use https://api.telegram.org/bot<TOKEN>/getUpdates)

Features:
- Send notifications/messages to user
- Receive commands via Telegram and process through agent loop
- Status reports
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from datetime import datetime


class TelegramChannel:
    """
    Telegram bot integration for JARVIS.
    Uses raw HTTP API (no python-telegram-bot dependency needed).
    """

    BASE_URL = "https://api.telegram.org/bot{token}"

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()

        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)
        self._last_update_id = 0
        self._command_handler: Optional[Callable[[str, str], Awaitable[str]]] = None

        if self.enabled:
            print(f"✓ Telegram Channel ready (chat_id={self.chat_id[:4]}...)")
        else:
            print("○ Telegram Channel disabled (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env)")

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_command_handler(self, handler: Callable[[str, str], Awaitable[str]]):
        """
        Register a callback for incoming Telegram messages.
        handler(text: str, language: str) -> response: str
        """
        self._command_handler = handler

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------
    async def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Send a message to the configured Telegram chat."""
        if not self.enabled:
            return False

        target = chat_id or self.chat_id
        url = f"{self.BASE_URL.format(token=self.token)}/sendMessage"
        payload = {
            "chat_id": target,
            "text": text,
            "parse_mode": "Markdown",
        }

        try:
            response = await self._http_post(url, payload)
            return response.get("ok", False)
        except Exception as exc:
            print(f"[Telegram] Send error: {exc}")
            return False

    async def send_notification(self, title: str, body: str) -> bool:
        """Send a formatted notification."""
        message = f"🔔 *{title}*\n\n{body}\n\n_{datetime.now().strftime('%H:%M')}_"
        return await self.send_message(message)

    async def send_status(self, status_dict: Dict[str, Any]) -> bool:
        """Send a formatted status report."""
        lines = ["📊 *JARVIS Status Report*\n"]
        for key, value in status_dict.items():
            lines.append(f"• *{key}*: {value}")
        lines.append(f"\n_{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
        return await self.send_message("\n".join(lines))

    # ------------------------------------------------------------------
    # Receiving (polling)
    # ------------------------------------------------------------------
    async def poll_messages(self) -> None:
        """
        Long-poll for new messages. Runs in a loop.
        Call this as a background task.
        """
        if not self.enabled:
            return

        print("[Telegram] Starting message polling...")
        while True:
            try:
                updates = await self._get_updates()
                for update in updates:
                    await self._handle_update(update)
            except Exception as exc:
                print(f"[Telegram] Poll error: {exc}")

            await asyncio.sleep(2)  # Poll every 2 seconds

    async def check_once(self) -> list:
        """Check for new messages once (non-blocking). Returns list of message texts."""
        if not self.enabled:
            return []

        messages = []
        try:
            updates = await self._get_updates()
            for update in updates:
                msg = update.get("message", {})
                text = msg.get("text", "")
                if text:
                    messages.append(text)
                self._last_update_id = update["update_id"] + 1
        except Exception:
            pass
        return messages

    async def _get_updates(self) -> list:
        """Fetch pending updates from Telegram."""
        url = f"{self.BASE_URL.format(token=self.token)}/getUpdates"
        params = {
            "offset": self._last_update_id,
            "timeout": 5,
            "limit": 10,
        }

        try:
            # Build URL with query params
            query = "&".join(f"{k}={v}" for k, v in params.items())
            full_url = f"{url}?{query}"
            response = await self._http_get(full_url)
            if response and response.get("ok"):
                return response.get("result", [])
        except Exception as exc:
            print(f"[Telegram] Get updates error: {exc}")
        return []

    async def _handle_update(self, update: Dict) -> None:
        """Process a single Telegram update."""
        self._last_update_id = update["update_id"] + 1

        msg = update.get("message", {})
        text = msg.get("text", "")
        sender_id = str(msg.get("chat", {}).get("id", ""))

        if not text:
            return

        # Only respond to authorized chat
        if sender_id != self.chat_id:
            print(f"[Telegram] Ignoring message from unauthorized chat: {sender_id}")
            return

        print(f"[Telegram] Received: {text}")

        # Handle special commands
        if text.startswith("/"):
            if text == "/status":
                await self.send_message("🟢 JARVIS is online and running.")
                return
            elif text == "/help":
                await self.send_message(
                    "📋 *JARVIS Telegram Commands*\n\n"
                    "• /status - Check if JARVIS is running\n"
                    "• /help - Show this help\n"
                    "• Any other text - Processed as a command\n"
                )
                return

        # Forward to command handler (agent loop)
        if self._command_handler:
            try:
                # Simple language detection
                spanish_words = ['crear', 'leer', 'buscar', 'carpeta', 'archivo', 'resumir']
                lang = 'es' if any(w in text.lower() for w in spanish_words) else 'en'

                response = await self._command_handler(text, lang)
                # Truncate long responses for Telegram (4096 char limit)
                if len(response) > 4000:
                    response = response[:4000] + "\n...[truncated]"
                await self.send_message(response)
            except Exception as exc:
                await self.send_message(f"❌ Error: {exc}")
        else:
            await self.send_message("⚠️ JARVIS received your message but the agent loop is not connected.")

    # ------------------------------------------------------------------
    # HTTP helpers (minimal, no external deps beyond stdlib)
    # ------------------------------------------------------------------
    async def _http_post(self, url: str, data: Dict) -> Dict:
        """POST JSON to URL."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=data)
                return resp.json()
        except ImportError:
            import urllib.request
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))

    async def _http_get(self, url: str) -> Optional[Dict]:
        """GET JSON from URL."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url)
                return resp.json()
        except ImportError:
            import urllib.request
            with urllib.request.urlopen(url, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def status(self) -> Dict:
        return {
            "enabled": self.enabled,
            "chat_id": self.chat_id[:4] + "..." if self.chat_id else "not set",
            "last_update_id": self._last_update_id,
        }
