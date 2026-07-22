"""Stylesheets for light and dark themes."""

LIGHT_THEME = """
/* Global */
QMainWindow, QDialog {
    background-color: #F8F9FA;
    color: #212529;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

/* Labels */
QLabel {
    color: #495057;
    padding: 0;
}

QLabel#titleLabel {
    font-size: 16px;
    font-weight: bold;
    color: #212529;
}

QLabel#folderLabel {
    color: #6C757D;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #4361EE;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3A56D4;
}

QPushButton:pressed {
    background-color: #2F4BC4;
}

QPushButton:disabled {
    background-color: #ADB5BD;
    color: #E9ECEF;
}

QPushButton#secondaryButton {
    background-color: #E9ECEF;
    color: #495057;
    border: 1px solid #DEE2E6;
}

QPushButton#secondaryButton:hover {
    background-color: #DEE2E6;
}

QPushButton#dangerButton {
    background-color: #DC3545;
    color: white;
}

QPushButton#dangerButton:hover {
    background-color: #C82333;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #495057;
    padding: 3px 0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #CED4DA;
    border-radius: 4px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #4361EE;
    border-color: #4361EE;
}

QCheckBox::indicator:hover {
    border-color: #4361EE;
}

/* Group Box */
QGroupBox {
    font-weight: bold;
    color: #495057;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #212529;
}

/* Spin Box */
QSpinBox {
    background-color: white;
    border: 1px solid #DEE2E6;
    border-radius: 4px;
    padding: 4px 8px;
    color: #212529;
    min-width: 70px;
}

QSpinBox:focus {
    border-color: #4361EE;
}

/* Progress Bar */
QProgressBar {
    border: none;
    border-radius: 8px;
    background-color: #E9ECEF;
    text-align: center;
    color: #212529;
    font-weight: bold;
    font-size: 12px;
    min-height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4361EE, stop:1 #7209B7);
    border-radius: 8px;
}

/* Text Edit (Log) */
QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: 8px;
    color: #212529;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #4361EE;
    selection-color: white;
}

/* Scrollbar */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #CED4DA;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #ADB5BD;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* Status Bar */
QStatusBar {
    background-color: #F8F9FA;
    color: #6C757D;
    border-top: 1px solid #DEE2E6;
    font-size: 12px;
}
"""

DARK_THEME = """
/* Global */
QMainWindow, QDialog {
    background-color: #1A1B2E;
    color: #E4E6F0;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

/* Labels */
QLabel {
    color: #B0B4CC;
    padding: 0;
}

QLabel#titleLabel {
    font-size: 16px;
    font-weight: bold;
    color: #E4E6F0;
}

QLabel#folderLabel {
    color: #7B7F99;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #6C63FF;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #5A52E0;
}

QPushButton:pressed {
    background-color: #4A42C8;
}

QPushButton:disabled {
    background-color: #3D3F5C;
    color: #6B6D87;
}

QPushButton#secondaryButton {
    background-color: #2D2F48;
    color: #B0B4CC;
    border: 1px solid #3D3F5C;
}

QPushButton#secondaryButton:hover {
    background-color: #363858;
}

QPushButton#dangerButton {
    background-color: #E74C3C;
    color: white;
}

QPushButton#dangerButton:hover {
    background-color: #C0392B;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #B0B4CC;
    padding: 3px 0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3D3F5C;
    border-radius: 4px;
    background-color: #2D2F48;
}

QCheckBox::indicator:checked {
    background-color: #6C63FF;
    border-color: #6C63FF;
}

QCheckBox::indicator:hover {
    border-color: #6C63FF;
}

/* Group Box */
QGroupBox {
    font-weight: bold;
    color: #B0B4CC;
    border: 1px solid #2D2F48;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #22243A;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #E4E6F0;
}

/* Spin Box */
QSpinBox {
    background-color: #2D2F48;
    border: 1px solid #3D3F5C;
    border-radius: 4px;
    padding: 4px 8px;
    color: #E4E6F0;
    min-width: 70px;
}

QSpinBox:focus {
    border-color: #6C63FF;
}

/* Progress Bar */
QProgressBar {
    border: none;
    border-radius: 8px;
    background-color: #2D2F48;
    text-align: center;
    color: #E4E6F0;
    font-weight: bold;
    font-size: 12px;
    min-height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6C63FF, stop:1 #F72585);
    border-radius: 8px;
}

/* Text Edit (Log) */
QTextEdit {
    background-color: #22243A;
    border: 1px solid #2D2F48;
    border-radius: 8px;
    padding: 8px;
    color: #E4E6F0;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #6C63FF;
    selection-color: white;
}

/* Scrollbar */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #3D3F5C;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4D4F6C;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1B2E;
    color: #7B7F99;
    border-top: 1px solid #2D2F48;
    font-size: 12px;
}
"""
