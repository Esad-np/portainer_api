"""
Portainer API Client

Handles authentication and API communications with Portainer server.
Supports REST API operations for container management.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import urllib3

# Disable SSL warnings if verify_ssl is False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


@dataclass
class AuthToken:
    """Represents a JWT authentication token."""
    token: str
    issued_at: datetime

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid (basic check)."""
        return bool(self.token)


class PortainerClient:
    """
    Client for interacting with Portainer API.
    
    Handles authentication, JWT token management, and API requests.
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize Portainer API client.
        
        Args:
            url: Base URL of Portainer server (e.g., https://portainer.example.com)
            username: Portainer username for authentication
            password: Portainer password for authentication
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.auth_token: Optional[AuthToken] = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        _retry_on_auth: bool = True,
        **kwargs,
    ) -> requests.Response:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., /stacks)
            data: JSON request body
            params: Query parameters
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object from requests library
            
        Raises:
            ConnectionError: If unable to connect to Portainer server
            PortainerAuthError: If authentication fails
        """
        # Ensure we're authenticated
        if not self.auth_token:
            self._authenticate()

        url = f"{self.url}/api{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth_token.token}",
            "Content-Type": "application/json",
        }

        logger.debug(f"{method} {endpoint}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                verify=self.verify_ssl,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            response_text = e.response.text if e.response is not None else str(e)

            if status_code == 401 and _retry_on_auth:
                # Token expired, re-authenticate and retry
                self.auth_token = None
                self._authenticate()
                return self._make_request(
                    method,
                    endpoint,
                    data,
                    params,
                    _retry_on_auth=False,
                    **kwargs,
                )

            logger.error(f"HTTP error {status_code}: {response_text}")
            raise PortainerAPIError(f"API request failed ({status_code}): {response_text}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise PortainerAPIError(f"Connection error: {str(e)}") from e
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {str(e)}")
            raise PortainerAPIError(f"Request timeout: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise PortainerAPIError(f"Request error: {str(e)}") from e

    def _authenticate(self) -> None:
        """
        Authenticate with Portainer server and obtain JWT token.
        
        Raises:
            PortainerAuthError: If authentication fails
        """
        url = f"{self.url}/api/auth"
        payload = {
            "Username": self.username,
            "Password": self.password,
        }

        logger.info(f"Authenticating with Portainer server at {self.url}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            data = response.json()
            self.auth_token = AuthToken(
                token=data["jwt"],
                issued_at=datetime.now(),
            )
            logger.info("Authentication successful")
        except requests.exceptions.HTTPError:
            if response.status_code == 422:
                raise PortainerAuthError("Invalid credentials (username or password)")
            raise PortainerAuthError(f"Authentication failed: {response.text}")
        except Exception as e:
            raise PortainerAuthError(f"Authentication error: {str(e)}")

    def get_stacks(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of all stacks.
        
        Returns:
            List of stack objects
        """
        response = self._make_request("GET", "/stacks")
        stacks = response.json()
        if not isinstance(stacks, list):
            return []
        return stacks

    def get_stack(self, stack_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific stack.
        
        Args:
            stack_id: Stack identifier
            
        Returns:
            Stack object details
        """
        response = self._make_request("GET", f"/stacks/{stack_id}")
        return response.json()

    def get_stack_file_content(self, stack_id: int) -> str:
        """
        Retrieve the compose file content for a specific stack.

        Args:
            stack_id: Stack identifier

        Returns:
            Stack file content as text
        """
        response = self._make_request("GET", f"/stacks/{stack_id}/file")
        payload = response.json()

        if not isinstance(payload, dict):
            raise PortainerAPIError(f"Unexpected response for stack file {stack_id}: {payload!r}")

        stack_file_content = payload.get("StackFileContent")
        if not isinstance(stack_file_content, str):
            raise PortainerAPIError(
                f"Stack file response for {stack_id} did not include StackFileContent"
            )

        return stack_file_content

    def start_stack(self, stack_id: int, endpoint_id: int) -> Dict[str, Any]:
        """
        Start a stopped stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint identifier
            
        Returns:
            Updated stack object
        """
        params = {"endpointId": endpoint_id}
        response = self._make_request("POST", f"/stacks/{stack_id}/start", params=params)
        return response.json()

    def stop_stack(self, stack_id: int, endpoint_id: int) -> Dict[str, Any]:
        """
        Stop a running stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint identifier
            
        Returns:
            Updated stack object
        """
        params = {"endpointId": endpoint_id}
        response = self._make_request("POST", f"/stacks/{stack_id}/stop", params=params)
        return response.json()

    def delete_stack(self, stack_id: int, endpoint_id: int, external: bool = False) -> None:
        """
        Delete/remove a stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint identifier
            external: Whether this is an external stack (for Swarm)
        """
        params = {"endpointId": endpoint_id, "external": external}
        self._make_request("DELETE", f"/stacks/{stack_id}", params=params)
        logger.info(f"Stack {stack_id} deleted successfully")

    def get_endpoints(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of all environments/endpoints.
        
        Returns:
            List of endpoint objects
        """
        response = self._make_request("GET", "/endpoints")
        endpoints = response.json()
        if not isinstance(endpoints, list):
            return []
        return endpoints

    def get_endpoint(self, endpoint_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific endpoint/environment.
        
        Args:
            endpoint_id: Endpoint identifier
            
        Returns:
            Endpoint object details
        """
        response = self._make_request("GET", f"/endpoints/{endpoint_id}")
        return response.json()


class PortainerAuthError(Exception):
    """Raised when Portainer authentication fails."""
    pass


class PortainerAPIError(Exception):
    """Raised when Portainer API calls fail."""
    pass
