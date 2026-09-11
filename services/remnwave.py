import aiohttp
from typing import Optional, Dict, List
from utils.logger import setup_logger
from utils.config import settings

logger = setup_logger(__name__)


class RemnwaveAPIError(Exception):
    """Базовое исключение для ошибок Remnwave API"""
    pass


class AccountNotFoundError(RemnwaveAPIError):
    """Аккаунт не найден"""
    pass


class QuotaExceededError(RemnwaveAPIError):
    """Превышена квота создания аккаунтов"""
    pass


class RemnwaveClient:
    """Клиент для работы с Remnwave API"""

    def __init__(self):
        self.api_key = settings.REMNWAVE_API_KEY
        self.api_url = settings.REMNWAVE_API_URL
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
        return self.session

    async def close(self):
        """Закрыть сессию"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Обработка ответов API с проверкой ошибок"""
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise AccountNotFoundError("VPN аккаунт не найден")
        elif response.status == 429:
            raise QuotaExceededError("Превышена квота создания аккаунтов")
        else:
            try:
                data = await response.json()
                error_message = data.get('message', 'Unknown error')
            except:
                error_message = await response.text()

            logger.error(f"Remnwave API error {response.status}: {error_message}")
            raise RemnwaveAPIError(f"API error {response.status}: {error_message}")

    async def create_account(
        self,
        user_id: str,
        plan: str,
        duration_days: int
    ) -> Dict:
        """
        Создает новый VPN аккаунт в Remnwave

        Args:
            user_id: ID пользователя
            plan: ID тарифного плана
            duration_days: Длительность подписки в днях

        Returns:
            {
                'account_id': 'abc123',
                'config_url': 'https://...',
                'qr_code': 'data:image/png;base64,...',
                'expires_at': '2026-10-11T00:00:00Z'
            }
        """
        session = await self._get_session()
        payload = {
            'user_id': user_id,
            'plan': plan,
            'duration_days': duration_days
        }

        logger.info(f"Creating VPN account for user {user_id}, plan {plan}")

        try:
            async with session.post(
                f'{self.api_url}/accounts',
                json=payload
            ) as resp:
                result = await self._handle_response(resp)
                logger.info(f"VPN account created: {result.get('account_id')}")
                return result
        except Exception as e:
            logger.error(f"Failed to create VPN account: {e}")
            raise

    async def get_account(self, account_id: str) -> Dict:
        """
        Получает информацию о VPN аккаунте

        Returns:
            {
                'account_id': 'abc123',
                'status': 'active',
                'expires_at': '2026-10-11T00:00:00Z',
                'traffic_used_gb': 15.3,
                'devices_connected': 1,
                'last_connection': '2026-09-11T10:30:00Z'
            }
        """
        session = await self._get_session()

        logger.info(f"Getting VPN account info: {account_id}")

        try:
            async with session.get(
                f'{self.api_url}/accounts/{account_id}'
            ) as resp:
                return await self._handle_response(resp)
        except Exception as e:
            logger.error(f"Failed to get VPN account: {e}")
            raise

    async def extend_account(
        self,
        account_id: str,
        additional_days: int
    ) -> Dict:
        """
        Продлевает существующий VPN аккаунт

        Returns:
            {
                'account_id': 'abc123',
                'expires_at': '2026-11-11T00:00:00Z'
            }
        """
        session = await self._get_session()
        payload = {'additional_days': additional_days}

        logger.info(f"Extending VPN account {account_id} by {additional_days} days")

        try:
            async with session.post(
                f'{self.api_url}/accounts/{account_id}/extend',
                json=payload
            ) as resp:
                result = await self._handle_response(resp)
                logger.info(f"VPN account extended: {account_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to extend VPN account: {e}")
            raise

    async def cancel_account(self, account_id: str) -> Dict:
        """
        Отменяет (деактивирует) VPN аккаунт

        Returns:
            {
                'account_id': 'abc123',
                'status': 'cancelled'
            }
        """
        session = await self._get_session()

        logger.info(f"Cancelling VPN account: {account_id}")

        try:
            async with session.delete(
                f'{self.api_url}/accounts/{account_id}'
            ) as resp:
                result = await self._handle_response(resp)
                logger.info(f"VPN account cancelled: {account_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to cancel VPN account: {e}")
            raise

    async def get_servers(self) -> List[Dict]:
        """
        Получает список доступных VPN серверов

        Returns:
            [
                {
                    'server_id': 'us-ny-01',
                    'country': 'US',
                    'city': 'New York',
                    'load': 45,
                    'ping': 120,
                    'available': true
                },
                ...
            ]
        """
        session = await self._get_session()

        logger.info("Getting VPN servers list")

        try:
            async with session.get(
                f'{self.api_url}/servers'
            ) as resp:
                return await self._handle_response(resp)
        except Exception as e:
            logger.error(f"Failed to get VPN servers: {e}")
            raise


# Singleton instance
remnwave_client = RemnwaveClient()
