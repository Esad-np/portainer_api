"""
Stack Management Module

Provides high-level operations for managing Docker stacks in Portainer.
Supports listing, starting, stopping, and deleting stacks.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from portainer_client import PortainerClient, PortainerAuthError, PortainerAPIError

logger = logging.getLogger(__name__)


class StackStatus(Enum):
    """Stack status enumeration."""
    RUNNING = 1
    STOPPED = 2
    UNKNOWN = 0


@dataclass
class Stack:
    """Represents a Docker stack in Portainer."""
    id: int
    name: str
    status: int
    endpoint_id: int
    created_by: str
    creation_date: int
    
    @property
    def status_name(self) -> str:
        """Get human-readable status name."""
        status_map = {
            1: "Running",
            2: "Stopped",
        }
        return status_map.get(self.status, "Unknown")


class StackManager:
    """
    Manager for Portainer stack operations.
    
    Provides simplified interface for common stack operations:
    - List stacks
    - Start stack
    - Stop stack
    - Delete stack
    """

    def __init__(self, client: PortainerClient, default_endpoint_id: int = 1):
        """
        Initialize Stack Manager.
        
        Args:
            client: PortainerClient instance
            default_endpoint_id: Default environment/endpoint to use
        """
        self.client = client
        self.default_endpoint_id = default_endpoint_id

    def list_stacks(self) -> List[Stack]:
        """
        List all available stacks.
        
        Returns:
            List of Stack objects
        """
        try:
            stacks_data = self.client.get_stacks()
            stacks = []
            
            for stack_data in stacks_data:
                stack = Stack(
                    id=stack_data.get("Id"),
                    name=stack_data.get("Name"),
                    status=stack_data.get("Status"),
                    endpoint_id=stack_data.get("EndpointId"),
                    created_by=stack_data.get("CreatedBy", "Unknown"),
                    creation_date=stack_data.get("CreationDate", 0),
                )
                stacks.append(stack)
            
            return stacks
        except Exception as e:
            logger.error(f"Failed to list stacks: {str(e)}")
            raise StackManagerError(f"Failed to list stacks: {str(e)}")

    def get_stack(self, stack_id: int) -> Stack:
        """
        Get details of a specific stack.
        
        Args:
            stack_id: Stack identifier
            
        Returns:
            Stack object with details
        """
        try:
            stack_data = self.client.get_stack(stack_id)
            
            return Stack(
                id=stack_data.get("Id"),
                name=stack_data.get("Name"),
                status=stack_data.get("Status"),
                endpoint_id=stack_data.get("EndpointId"),
                created_by=stack_data.get("CreatedBy", "Unknown"),
                creation_date=stack_data.get("CreationDate", 0),
            )
        except Exception as e:
            logger.error(f"Failed to get stack {stack_id}: {str(e)}")
            raise StackManagerError(f"Failed to get stack {stack_id}: {str(e)}")

    def start_stack(self, stack_id: int, endpoint_id: Optional[int] = None) -> Stack:
        """
        Start a stopped stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint ID (uses default if not provided)
            
        Returns:
            Updated Stack object
        """
        endpoint_id = endpoint_id or self.default_endpoint_id
        
        try:
            # Check current status first to avoid redundant start
            try:
                current = self.get_stack(stack_id)
            except StackManagerError:
                current = None

            if current and current.status == StackStatus.RUNNING.value:
                logger.info(f"Stack {stack_id} is already running; skipping start")
                return current

            logger.info(f"Starting stack {stack_id} on endpoint {endpoint_id}")
            stack_data = self.client.start_stack(stack_id, endpoint_id)

            logger.info(f"Stack {stack_id} started successfully")

            return Stack(
                id=stack_data.get("Id"),
                name=stack_data.get("Name"),
                status=stack_data.get("Status"),
                endpoint_id=stack_data.get("EndpointId"),
                created_by=stack_data.get("CreatedBy", "Unknown"),
                creation_date=stack_data.get("CreationDate", 0),
            )
        except Exception as e:
            logger.error(f"Failed to start stack {stack_id}: {str(e)}")
            raise StackManagerError(f"Failed to start stack {stack_id}: {str(e)}")

    def stop_stack(self, stack_id: int, endpoint_id: Optional[int] = None) -> Stack:
        """
        Stop a running stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint ID (uses default if not provided)
            
        Returns:
            Updated Stack object
        """
        endpoint_id = endpoint_id or self.default_endpoint_id
        
        try:
            # Check current status first to avoid redundant stop
            try:
                current = self.get_stack(stack_id)
            except StackManagerError:
                current = None

            if current and current.status == StackStatus.STOPPED.value:
                logger.info(f"Stack {stack_id} is already stopped; skipping stop")
                return current

            logger.info(f"Stopping stack {stack_id} on endpoint {endpoint_id}")
            stack_data = self.client.stop_stack(stack_id, endpoint_id)

            logger.info(f"Stack {stack_id} stopped successfully")

            return Stack(
                id=stack_data.get("Id"),
                name=stack_data.get("Name"),
                status=stack_data.get("Status"),
                endpoint_id=stack_data.get("EndpointId"),
                created_by=stack_data.get("CreatedBy", "Unknown"),
                creation_date=stack_data.get("CreationDate", 0),
            )
        except Exception as e:
            logger.error(f"Failed to stop stack {stack_id}: {str(e)}")
            raise StackManagerError(f"Failed to stop stack {stack_id}: {str(e)}")

    def delete_stack(self, stack_id: int, endpoint_id: Optional[int] = None, external: bool = False) -> None:
        """
        Delete/remove a stack.
        
        Args:
            stack_id: Stack identifier
            endpoint_id: Environment/endpoint ID (uses default if not provided)
            external: Whether this is an external stack
        """
        endpoint_id = endpoint_id or self.default_endpoint_id
        
        try:
            logger.info(f"Deleting stack {stack_id} from endpoint {endpoint_id}")
            self.client.delete_stack(stack_id, endpoint_id, external=external)
        except Exception as e:
            logger.error(f"Failed to delete stack {stack_id}: {str(e)}")
            raise StackManagerError(f"Failed to delete stack {stack_id}: {str(e)}")

    def get_stack_by_name(self, stack_name: str) -> Optional[Stack]:
        """
        Find a stack by name.
        
        Args:
            stack_name: Name of the stack to find
            
        Returns:
            Stack object or None if not found
        """
        try:
            stacks = self.list_stacks()
            for stack in stacks:
                if stack.name.lower() == stack_name.lower():
                    return stack
            return None
        except Exception as e:
            logger.error(f"Failed to find stack '{stack_name}': {str(e)}")
            return None

    def list_stacks_by_endpoint(self, endpoint_id: int) -> List[Stack]:
        """
        List stacks for a specific endpoint/environment.
        
        Args:
            endpoint_id: Environment/endpoint identifier
            
        Returns:
            List of Stack objects for the endpoint
        """
        try:
            all_stacks = self.list_stacks()
            return [s for s in all_stacks if s.endpoint_id == endpoint_id]
        except Exception as e:
            logger.error(f"Failed to list stacks for endpoint {endpoint_id}: {str(e)}")
            return []


class StackManagerError(Exception):
    """Raised when stack management operations fail."""
    pass
