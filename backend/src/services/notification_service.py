"""Notification service for sending alerts."""
import logging
import urllib.parse
from typing import Optional
import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via various channels."""
    
    def __init__(self):
        self.callmebot_phone = getattr(settings, 'CALLMEBOT_PHONE', None)
        self.callmebot_apikey = getattr(settings, 'CALLMEBOT_APIKEY', None)
    
    async def send_whatsapp_message(self, message: str) -> bool:
        """
        Send a WhatsApp message using CallMeBot API.
        
        Args:
            message: The message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        logger.info(f"[NOTIFICATION] Attempting to send WhatsApp message...")
        logger.info(f"[NOTIFICATION] Phone configured: {self.callmebot_phone}")
        logger.info(f"[NOTIFICATION] API Key configured: {'Yes' if self.callmebot_apikey else 'No'}")
        
        if not self.callmebot_phone or not self.callmebot_apikey:
            logger.warning("CallMeBot credentials not configured. Skipping WhatsApp notification.")
            return False
        
        try:
            # URL encode the message
            encoded_message = urllib.parse.quote(message)
            
            # Build the API URL
            url = (
                f"https://api.callmebot.com/whatsapp.php"
                f"?phone={self.callmebot_phone}"
                f"&text={encoded_message}"
                f"&apikey={self.callmebot_apikey}"
            )
            
            logger.info(f"[NOTIFICATION] Sending request to CallMeBot API...")
            logger.info(f"[NOTIFICATION] URL: {url[:80]}...")  # Log only first 80 chars for security
            
            # Send the request
            async with httpx.AsyncClient() as client:
                response = await client.post(url, timeout=10.0)
                
                logger.info(f"[NOTIFICATION] Response status: {response.status_code}")
                logger.info(f"[NOTIFICATION] Response body: {response.text}")
                
                if response.status_code == 200:
                    logger.info(f"[NOTIFICATION] ✅ WhatsApp message sent successfully!")
                    return True
                else:
                    logger.error(f"[NOTIFICATION] ❌ Failed to send WhatsApp message. Status: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"[NOTIFICATION] ❌ Error sending WhatsApp message: {e}", exc_info=True)
            return False
    
    async def notify_new_user_registration(self, username: str, email: str) -> bool:
        """
        Send notification when a new user registers.
        
        Args:
            username: Username of the new user
            email: Email of the new user
            
        Returns:
            bool: True if notification was sent successfully
        """
        logger.info(f"[NOTIFICATION] 📢 New user registration detected!")
        logger.info(f"[NOTIFICATION] Username: {username}, Email: {email}")
        
        message = (
            f"🔔 Nova conta criada!\n\n"
            f"👤 Usuário: {username}\n"
            f"📧 Email: {email}\n\n"
            f"Acesse o painel para aprovar o acesso."
        )
        
        result = await self.send_whatsapp_message(message)
        logger.info(f"[NOTIFICATION] Notification result: {'SUCCESS' if result else 'FAILED'}")
        return result


# Global notification service instance
notification_service = NotificationService()
