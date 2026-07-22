"""Application settings management using QSettings."""

from PySide6.QtCore import QSettings

SETTINGS_ORG = 'GovnyakHelper'
SETTINGS_APP = 'BatchImageProcessor'


class AppSettings:
    """Persistent application settings wrapper.

    Uses QSettings for cross-platform persistent storage.
    """

    def __init__(self) -> None:
        """Initialize settings with default values."""
        self._settings = QSettings(SETTINGS_ORG, SETTINGS_APP)

    @property
    def last_input_folder(self) -> str:
        """Get the last used input folder path."""
        return self._settings.value('last_input_folder', '', str)

    @last_input_folder.setter
    def last_input_folder(self, value: str) -> None:
        """Set the last used input folder path."""
        self._settings.setValue('last_input_folder', value)

    @property
    def last_output_folder(self) -> str:
        """Get the last used output folder path."""
        return self._settings.value('last_output_folder', '', str)

    @last_output_folder.setter
    def last_output_folder(self, value: str) -> None:
        """Set the last used output folder path."""
        self._settings.setValue('last_output_folder', value)

    @property
    def theme(self) -> str:
        """Get the current theme ('light' or 'dark')."""
        return self._settings.value('theme', 'dark', str)

    @theme.setter
    def theme(self, value: str) -> None:
        """Set the current theme."""
        self._settings.setValue('theme', value)

    @property
    def remove_bg(self) -> bool:
        """Get the 'remove background' default state."""
        return self._settings.value('remove_bg', True) in (True, 'true', 'True')

    @remove_bg.setter
    def remove_bg(self, value: bool) -> None:
        """Set the 'remove background' default state."""
        self._settings.setValue('remove_bg', value)

    @property
    def trim_edges(self) -> bool:
        """Get the 'trim edges' default state."""
        return self._settings.value('trim_edges', True) in (True, 'true', 'True')

    @trim_edges.setter
    def trim_edges(self, value: bool) -> None:
        """Set the 'trim edges' default state."""
        self._settings.setValue('trim_edges', value)

    @property
    def uniform_size(self) -> bool:
        """Get the 'uniform size' default state."""
        return self._settings.value('uniform_size', False) in (True, 'true', 'True')

    @uniform_size.setter
    def uniform_size(self, value: bool) -> None:
        """Set the 'uniform size' default state."""
        self._settings.setValue('uniform_size', value)

    @property
    def target_width(self) -> int:
        """Get the default target width."""
        return self._settings.value('target_width', 512, int)

    @target_width.setter
    def target_width(self, value: int) -> None:
        """Set the default target width."""
        self._settings.setValue('target_width', value)

    @property
    def target_height(self) -> int:
        """Get the default target height."""
        return self._settings.value('target_height', 512, int)

    @target_height.setter
    def target_height(self, value: int) -> None:
        """Set the default target height."""
        self._settings.setValue('target_height', value)

    @property
    def center_object(self) -> bool:
        """Get the 'center object' default state."""
        return self._settings.value('center_object', False) in (True, 'true', 'True')

    @center_object.setter
    def center_object(self, value: bool) -> None:
        """Set the 'center object' default state."""
        self._settings.setValue('center_object', value)

    @property
    def overwrite_existing(self) -> bool:
        """Get the 'overwrite existing' default state."""
        return self._settings.value('overwrite_existing', False) in (True, 'true', 'True')

    @overwrite_existing.setter
    def overwrite_existing(self, value: bool) -> None:
        """Set the 'overwrite existing' default state."""
        self._settings.setValue('overwrite_existing', value)

    @property
    def preserve_structure(self) -> bool:
        """Get the 'preserve structure' default state."""
        return self._settings.value('preserve_structure', True) in (True, 'true', 'True')

    @preserve_structure.setter
    def preserve_structure(self, value: bool) -> None:
        """Set the 'preserve structure' default state."""
        self._settings.setValue('preserve_structure', value)
