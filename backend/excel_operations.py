#!/usr/bin/env python3
"""
Excel Operations Module

Provides Excel-specific automation operations:
- Window detection and focus
- VLM-based element extraction (cells, columns, buttons)
- Operations: set_filter, save_as
"""

import pygetwindow as gw
import pyautogui
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelWindowManager:
    """Manage Excel window detection and focus."""

    @staticmethod
    def find_excel_window() -> Optional[gw.Win32Window]:
        """
        Find the active Excel window.

        Returns:
            Window object if found, None otherwise
        """
        try:
            # Search for Excel windows (Microsoft Excel title pattern)
            windows = gw.getWindowsWithTitle('Excel')
            if not windows:
                # Try alternative pattern (filename - Excel)
                all_windows = gw.getAllTitles()
                excel_windows = [w for w in all_windows if 'Excel' in w]
                if excel_windows:
                    windows = [gw.getWindowsWithTitle(excel_windows[0])[0]]

            if windows:
                logger.info(f"Found Excel window: {windows[0].title}")
                return windows[0]
            else:
                logger.warning("No Excel window found")
                return None

        except Exception as e:
            logger.error(f"Error finding Excel window: {e}")
            return None

    @staticmethod
    def focus_excel_window(window: gw.Win32Window) -> bool:
        """
        Bring Excel window to foreground.

        Args:
            window: Excel window object

        Returns:
            bool: True if successful
        """
        try:
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.5)  # Wait for window to activate
            logger.info("Excel window activated")
            return True
        except Exception as e:
            logger.error(f"Failed to activate Excel window: {e}")
            return False

    @staticmethod
    def get_excel_region(window: gw.Win32Window) -> Dict[str, int]:
        """
        Get Excel window region for screenshot capture.

        Args:
            window: Excel window object

        Returns:
            Dict with {left, top, width, height}
        """
        return {
            'left': window.left,
            'top': window.top,
            'width': window.width,
            'height': window.height
        }


class ExcelOperations:
    """Excel-specific automation operations."""

    def __init__(self):
        """Initialize Excel operations."""
        self.window_manager = ExcelWindowManager()
        logger.info("ExcelOperations initialized")

    def set_filter(self, column_name: str, filter_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply filter to an Excel column.

        Implementation strategy:
        1. Detect Excel window and focus
        2. Use VLM to locate column header
        3. Click column header dropdown
        4. If filter_value provided, select specific filter value
        5. Otherwise, just open filter menu

        Args:
            column_name: Name of the column to filter
            filter_value: Optional specific value to filter for

        Returns:
            Dict with result: {"success": bool, "message": str}
        """
        try:
            # Find and focus Excel window
            window = self.window_manager.find_excel_window()
            if not window:
                return {
                    "success": False,
                    "error": "Excel window not found. Please open an Excel file."
                }

            self.window_manager.focus_excel_window(window)

            # TODO: VLM integration to locate column header
            # For now, log the intent
            logger.info(f"set_filter operation: column='{column_name}', filter_value='{filter_value}'")

            return {
                "success": True,
                "message": f"Filter operation prepared for column '{column_name}'",
                "action": "set_filter",
                "column": column_name,
                "filter_value": filter_value,
                "note": "VLM integration pending - column detection not yet implemented"
            }

        except Exception as e:
            logger.error(f"set_filter failed: {e}")
            return {"success": False, "error": str(e)}

    def save_as(self, file_path: str, file_format: str = "xlsx") -> Dict[str, Any]:
        """
        Save Excel file with specified name and format.

        Implementation strategy:
        1. Press Ctrl+Shift+S or Alt+F,A (Save As shortcut)
        2. Wait for Save As dialog
        3. Type file path
        4. Select format if needed
        5. Confirm save

        Args:
            file_path: Destination path for saved file
            file_format: Format (xlsx, xls, csv, etc.)

        Returns:
            Dict with result: {"success": bool, "message": str}
        """
        try:
            # Find and focus Excel window
            window = self.window_manager.find_excel_window()
            if not window:
                return {
                    "success": False,
                    "error": "Excel window not found. Please open an Excel file."
                }

            self.window_manager.focus_excel_window(window)

            # Open Save As dialog (Ctrl+Shift+S on Windows/Excel 365)
            logger.info("Opening Save As dialog...")
            pyautogui.hotkey('ctrl', 'shift', 's')
            time.sleep(1.0)  # Wait for dialog

            # Type file path
            logger.info(f"Entering file path: {file_path}")
            pyautogui.write(file_path, interval=0.05)

            # Note: File format selection would require VLM to detect dropdown
            # For now, assume default format matches request

            logger.info(f"save_as operation: file_path='{file_path}', format='{file_format}'")

            return {
                "success": True,
                "message": f"Save As dialog opened with path '{file_path}'",
                "action": "save_as",
                "file_path": file_path,
                "format": file_format,
                "note": "Manual confirmation required - auto-save not yet implemented"
            }

        except Exception as e:
            logger.error(f"save_as failed: {e}")
            return {"success": False, "error": str(e)}

    def detect_excel_elements(self, screenshot_data: bytes) -> Dict[str, Any]:
        """
        Use VLM to detect Excel UI elements (columns, cells, buttons).

        This will be integrated with vlm_service.py for element detection.

        Args:
            screenshot_data: PNG screenshot bytes of Excel window

        Returns:
            Dict with detected elements
        """
        # TODO: Integrate with VLM service
        logger.info("detect_excel_elements called (VLM integration pending)")
        return {
            "elements": [],
            "columns": [],
            "cells": [],
            "note": "VLM integration pending"
        }
