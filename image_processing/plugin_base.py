"""Base classes for the image processing plugin system."""

from abc import ABC, abstractmethod
from pathlib import Path
from collections.abc import Callable
from typing import Any


class ProcessingStep(ABC):
    """Abstract base class for a single image processing step.

    Plugins should inherit from this class and implement the `process` method.
    """

    name: str = 'BaseStep'
    description: str = 'Base processing step'

    @abstractmethod
    def process(self, image: Any, settings: Any) -> Any:
        """Process a single image.

        Args:
            image: PIL Image object to process.
            settings: ProcessingSettings instance or dict with settings.

        Returns:
            Processed PIL Image object.
        """
        ...


class PluginRegistry:
    """Registry for managing processing plugin steps.

    Allows dynamic registration of new processing steps without
    modifying the core architecture.
    """

    def __init__(self) -> None:
        """Initialize an empty plugin registry."""
        self._plugins: dict[str, ProcessingStep] = {}

    def register(self, plugin: ProcessingStep) -> None:
        """Register a processing plugin.

        Args:
            plugin: ProcessingStep instance to register.
        """
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """Remove a processing plugin by name.

        Args:
            name: Name of the plugin to remove.
        """
        self._plugins.pop(name, None)

    def get(self, name: str) -> ProcessingStep | None:
        """Get a registered plugin by name.

        Args:
            name: Name of the plugin to retrieve.

        Returns:
            The plugin instance, or None if not found.
        """
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        """Get sorted list of registered plugin names.

        Returns:
            List of plugin names.
        """
        return sorted(self._plugins.keys())

    def process_all(self, image: Any, settings: Any) -> Any:
        """Run all registered processing steps on an image.

        Args:
            image: PIL Image object to process.
            settings: ProcessingSettings instance.

        Returns:
            Processed PIL Image object.
        """
        result = image
        for plugin in self._plugins.values():
            result = plugin.process(result, settings)
        return result


# Global plugin registry
registry = PluginRegistry()
