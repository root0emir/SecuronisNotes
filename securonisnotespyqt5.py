#!/usr/bin/env python3
# DEVELOPER: root0emir 
import sys
import os
import json
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                           QPushButton, QComboBox, QListWidget, QListWidgetItem,
                           QMessageBox, QFileDialog, QCalendarWidget, QDialog,
                           QTabWidget, QFrame, QScrollArea, QCheckBox,
                           QSpinBox, QColorDialog, QFontDialog, QMenuBar,
                           QMenu, QAction, QStatusBar, QToolBar, QToolButton,
                           QInputDialog, QSplitter, QStyle, QStyleFactory,
                           QStyleOptionButton)
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QTextCharFormat, QLinearGradient, QPainter
from cryptography.fernet import Fernet

class ModernCheckBox(QCheckBox):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 4px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #4d4d4d;
                background-color: #2d2d2d;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4d4d4d;
                background-color: #4d4d4d;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked:hover {
                border: 2px solid #5d5d5d;
                background-color: #5d5d5d;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #5d5d5d;
                background-color: #3d3d3d;
            }
            QCheckBox::indicator:pressed {
                border: 2px solid #3d3d3d;
                background-color: #2d2d2d;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            painter = QPainter(self)
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 16))
            
            # Checkbox'ın konumunu bul
            style = self.style()
            opt = QStyleOptionButton()
            self.initStyleOption(opt)
            indicator_rect = style.subElementRect(QStyle.SE_CheckBoxIndicator, opt, self)
            
            # Tik işaretini checkbox'ın tam ortasına çiz
            painter.drawText(indicator_rect, Qt.AlignCenter | Qt.AlignVCenter, "✓")

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        
        # Add hover animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.start()
        
    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self.animation.start()

class Note:
    def __init__(self, title="", content="", tags=None, priority="low",
                 due_date=None, category="general", color="#ffffff",
                 font_family="Arial", font_size=10, is_encrypted=False):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.priority = priority
        self.due_date = due_date or datetime.now()
        self.category = category
        self.color = color
        self.font_family = font_family
        self.font_size = font_size
        self.is_encrypted = is_encrypted
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.attachments = []
        self.reminder = None
        self.is_favorite = False
        self.is_archived = False

class NoteEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title with modern styling
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.title_edit = QLineEdit()
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4d4d4d;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # Content with rich text support
        content_label = QLabel("Content:")
        content_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.content_edit = QTextEdit()
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 1px solid #4d4d4d;
            }
        """)
        layout.addWidget(content_label)
        layout.addWidget(self.content_edit)
        
        # Tags with modern styling
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Tags:")
        tags_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Comma separated tags")
        self.tags_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4d4d4d;
            }
        """)
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_edit)
        layout.addLayout(tags_layout)
        
        # Priority and Category with modern styling
        priority_category_layout = QHBoxLayout()
        
        priority_label = QLabel("Priority:")
        priority_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])
        self.priority_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #4d4d4d;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        priority_category_layout.addWidget(priority_label)
        priority_category_layout.addWidget(self.priority_combo)
        
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["general", "work", "personal", "ideas"])
        self.category_combo.setEditable(True)
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #4d4d4d;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        priority_category_layout.addWidget(category_label)
        priority_category_layout.addWidget(self.category_combo)
        
        layout.addLayout(priority_category_layout)
        
        # Due Date with modern styling
        due_date_layout = QHBoxLayout()
        due_date_label = QLabel("Due Date:")
        due_date_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.due_date_edit = QLineEdit()
        self.due_date_edit.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.due_date_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4d4d4d;
            }
        """)
        due_date_layout.addWidget(due_date_label)
        due_date_layout.addWidget(self.due_date_edit)
        layout.addLayout(due_date_layout)
        
        # Formatting Tools with modern styling
        format_toolbar = QToolBar()
        format_toolbar.setIconSize(QSize(16, 16))
        format_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
        """)
        
        # Color picker
        color_action = QAction("Color", self)
        color_action.triggered.connect(self.choose_color)
        format_toolbar.addAction(color_action)
        
        # Font picker
        font_action = QAction("Font", self)
        font_action.triggered.connect(self.choose_font)
        format_toolbar.addAction(font_action)
        
        layout.addWidget(format_toolbar)
        
        # Additional features
        features_layout = QHBoxLayout()
        
        # Encryption
        self.encrypt_check = ModernCheckBox("Encrypt Note")
        features_layout.addWidget(self.encrypt_check)
        
        # Favorite
        self.favorite_check = ModernCheckBox("Favorite")
        features_layout.addWidget(self.favorite_check)
        
        # Archive
        self.archive_check = ModernCheckBox("Archive")
        features_layout.addWidget(self.archive_check)
        
        # Reminder
        self.reminder_check = ModernCheckBox("Set Reminder")
        features_layout.addWidget(self.reminder_check)
        
        # Attachments
        self.attachment_check = ModernCheckBox("Add Attachment")
        features_layout.addWidget(self.attachment_check)
        
        layout.addLayout(features_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("Save Note")
        save_btn.clicked.connect(self.save_note)
        button_layout.addWidget(save_btn)
        
        clear_btn = ModernButton("Clear")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.content_edit.setTextColor(color)
    
    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.content_edit.setFont(font)

    def clear_form(self):
        self.title_edit.clear()
        self.content_edit.clear()
        self.tags_edit.clear()
        self.priority_combo.setCurrentText("low")
        self.category_combo.setCurrentText("general")
        self.due_date_edit.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.encrypt_check.setChecked(False)
        self.favorite_check.setChecked(False)
        self.archive_check.setChecked(False)
        self.reminder_check.setChecked(False)
        self.attachment_check.setChecked(False)
        
    def save_note(self):
        # Ana pencereye sinyal gönder
        if hasattr(self.parent(), 'save_note'):
            self.parent().save_note()

class NoteList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search with modern styling
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search notes...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4d4d4d;
            }
        """)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Filters with modern styling
        filter_layout = QHBoxLayout()
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "Low", "Medium", "High"])
        self.priority_filter.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #4d4d4d;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        filter_layout.addWidget(QLabel("Priority:"))
        filter_layout.addWidget(self.priority_filter)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "General", "Work", "Personal", "Ideas"])
        self.category_filter.setEditable(True)
        self.category_filter.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #4d4d4d;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)
        
        layout.addLayout(filter_layout)
        
        # View options
        view_layout = QHBoxLayout()
        
        self.show_favorites = ModernCheckBox("Show Favorites")
        view_layout.addWidget(self.show_favorites)
        
        self.show_archived = ModernCheckBox("Show Archived")
        view_layout.addWidget(self.show_archived)
        
        self.show_encrypted = ModernCheckBox("Show Encrypted")
        view_layout.addWidget(self.show_encrypted)
        
        layout.addLayout(view_layout)
        
        # Note List with modern styling
        self.note_list = QListWidget()
        self.note_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #4d4d4d;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        layout.addWidget(self.note_list)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.total_notes = QLabel("Total Notes: 0")
        self.total_notes.setStyleSheet("color: #ffffff; font-size: 12px;")
        stats_layout.addWidget(self.total_notes)
        
        self.favorite_notes = QLabel("Favorites: 0")
        self.favorite_notes.setStyleSheet("color: #ffffff; font-size: 12px;")
        stats_layout.addWidget(self.favorite_notes)
        
        self.archived_notes = QLabel("Archived: 0")
        self.archived_notes.setStyleSheet("color: #ffffff; font-size: 12px;")
        stats_layout.addWidget(self.archived_notes)
        
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)
        
    def update_statistics(self, notes):
        total = len(notes)
        favorites = sum(1 for note in notes if note.is_favorite)
        archived = sum(1 for note in notes if note.is_archived)
        
        self.total_notes.setText(f"Total Notes: {total}")
        self.favorite_notes.setText(f"Favorites: {favorites}")
        self.archived_notes.setText(f"Archived: {archived}")

class CalendarView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        
        self.note_list = QListWidget()
        layout.addWidget(self.note_list)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Notes")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize note storage
        self.notes = []
        self.current_note = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
        # Load notes
        self.load_notes()
        
        # Setup status bar
        self.statusBar().showMessage("Ready")
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Note list
        self.note_list = NoteList()
        splitter.addWidget(self.note_list)
        
        # Right panel - Note editor
        self.note_editor = NoteEditor()
        splitter.addWidget(self.note_editor)
        
        # Set splitter sizes
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Connect signals
        self.note_list.note_list.itemClicked.connect(self.on_note_selected)
        self.note_list.search_edit.textChanged.connect(self.filter_notes)
        self.note_list.priority_filter.currentTextChanged.connect(self.filter_notes)
        self.note_list.category_filter.currentTextChanged.connect(self.filter_notes)
        self.note_list.show_favorites.stateChanged.connect(self.filter_notes)
        self.note_list.show_archived.stateChanged.connect(self.filter_notes)
        self.note_list.show_encrypted.stateChanged.connect(self.filter_notes)
        
        # Connect note editor signals
        self.note_editor.reminder_check.stateChanged.connect(self.setup_reminder)
        self.note_editor.attachment_check.stateChanged.connect(self.handle_attachment)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Note", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_note)
        file_menu.addAction(new_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_note)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("Import from CSV", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_notes)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export to CSV", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_notes)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        delete_action = QAction("Delete Note", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_note)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        encrypt_action = QAction("Encrypt Note", self)
        encrypt_action.setShortcut("Ctrl+Shift+E")
        encrypt_action.triggered.connect(self.toggle_encryption)
        edit_menu.addAction(encrypt_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        calendar_action = QAction("Calendar View", self)
        calendar_action.setShortcut("Ctrl+Shift+C")
        calendar_action.triggered.connect(self.show_calendar)
        view_menu.addAction(calendar_action)
        
        view_menu.addSeparator()
        
        show_favorites_action = QAction("Show Favorites", self)
        show_favorites_action.setShortcut("Ctrl+Shift+F")
        show_favorites_action.triggered.connect(self.toggle_favorites)
        view_menu.addAction(show_favorites_action)
        
        show_archived_action = QAction("Show Archived", self)
        show_archived_action.setShortcut("Ctrl+Shift+A")
        show_archived_action.triggered.connect(self.toggle_archived)
        view_menu.addAction(show_archived_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        backup_action = QAction("Backup Notes", self)
        backup_action.setShortcut("Ctrl+Shift+B")
        backup_action.triggered.connect(self.backup_notes)
        tools_menu.addAction(backup_action)
        
        restore_action = QAction("Restore from Backup", self)
        restore_action.setShortcut("Ctrl+Shift+R")
        restore_action.triggered.connect(self.restore_notes)
        tools_menu.addAction(restore_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)
        
        # New note button
        new_btn = QToolButton()
        new_btn.setText("New")
        new_btn.setToolTip("New Note (Ctrl+N)")
        new_btn.clicked.connect(self.new_note)
        toolbar.addWidget(new_btn)
        
        # Save button
        save_btn = QToolButton()
        save_btn.setText("Save")
        save_btn.setToolTip("Save Note (Ctrl+S)")
        save_btn.clicked.connect(self.save_note)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Format buttons
        color_btn = QToolButton()
        color_btn.setText("Color")
        color_btn.setToolTip("Change Text Color")
        color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(color_btn)
        
        font_btn = QToolButton()
        font_btn.setText("Font")
        font_btn.setToolTip("Change Font")
        font_btn.clicked.connect(self.choose_font)
        toolbar.addWidget(font_btn)
        
        toolbar.addSeparator()
        
        # View buttons
        calendar_btn = QToolButton()
        calendar_btn.setText("Calendar")
        calendar_btn.setToolTip("Calendar View (Ctrl+Shift+C)")
        calendar_btn.clicked.connect(self.show_calendar)
        toolbar.addWidget(calendar_btn)
        
        favorites_btn = QToolButton()
        favorites_btn.setText("Favorites")
        favorites_btn.setToolTip("Show Favorites (Ctrl+Shift+F)")
        favorites_btn.clicked.connect(self.toggle_favorites)
        toolbar.addWidget(favorites_btn)
        
        archived_btn = QToolButton()
        archived_btn.setText("Archived")
        archived_btn.setToolTip("Show Archived (Ctrl+Shift+A)")
        archived_btn.clicked.connect(self.toggle_archived)
        toolbar.addWidget(archived_btn)
        
    def setup_reminder(self, state):
        if not self.current_note:
            self.current_note = Note()
            
        if state == Qt.Checked:
            dialog = QDialog(self)
            dialog.setWindowTitle("Set Reminder")
            dialog.setGeometry(200, 200, 400, 200)
            
            layout = QVBoxLayout()
            
            # Date picker
            date_label = QLabel("Date:")
            date_label.setStyleSheet("color: #ffffff; font-weight: bold;")
            date_picker = QCalendarWidget()
            date_picker.setStyleSheet("""
                QCalendarWidget {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(date_label)
            layout.addWidget(date_picker)
            
            # Time picker
            time_label = QLabel("Time:")
            time_label.setStyleSheet("color: #ffffff; font-weight: bold;")
            time_edit = QLineEdit()
            time_edit.setText("00:00")
            time_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #3d3d3d;
                    padding: 8px;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(time_label)
            layout.addWidget(time_edit)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            ok_btn = ModernButton("OK")
            ok_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_btn)
            
            cancel_btn = ModernButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                date = date_picker.selectedDate()
                time = time_edit.text()
                self.current_note.reminder = datetime.combine(
                    date.toPyDate(),
                    datetime.strptime(time, "%H:%M").time()
                )
                self.statusBar().showMessage(
                    f"Reminder set for {self.current_note.reminder.strftime('%Y-%m-%d %H:%M')}"
                )
        else:
            self.current_note.reminder = None
            self.statusBar().showMessage("Reminder removed")
            
    def handle_attachment(self, state):
        if state == Qt.Checked:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Add Attachment", "", "All Files (*.*)"
            )
            if file_path:
                self.current_note.attachments.append(file_path)
                self.statusBar().showMessage(f"Attachment added: {os.path.basename(file_path)}")
        else:
            if self.current_note.attachments:
                self.current_note.attachments.pop()
                self.statusBar().showMessage("Attachment removed")
                
    def toggle_favorites(self):
        self.note_list.show_favorites.setChecked(
            not self.note_list.show_favorites.isChecked()
        )
        self.filter_notes()
        
    def toggle_archived(self):
        self.note_list.show_archived.setChecked(
            not self.note_list.show_archived.isChecked()
        )
        self.filter_notes()
        
    def filter_notes(self):
        search_text = self.note_list.search_edit.text().lower()
        priority_filter = self.note_list.priority_filter.currentText()
        category_filter = self.note_list.category_filter.currentText()
        show_favorites = self.note_list.show_favorites.isChecked()
        show_archived = self.note_list.show_archived.isChecked()
        show_encrypted = self.note_list.show_encrypted.isChecked()
        
        self.note_list.note_list.clear()
        for note in self.notes:
            if (search_text in note.title.lower() or
                search_text in note.content.lower() or
                any(search_text in tag.lower() for tag in note.tags)):
                if (priority_filter == "All" or
                    note.priority.capitalize() == priority_filter):
                    if (category_filter == "All" or
                        note.category.capitalize() == category_filter):
                        if (not show_favorites or note.is_favorite):
                            if (not show_archived or note.is_archived):
                                if (not show_encrypted or note.is_encrypted):
                                    item = QListWidgetItem(note.title)
                                    item.setData(Qt.UserRole, note)
                                    self.note_list.note_list.addItem(item)
                                    
        self.note_list.update_statistics(self.notes)
        
    def new_note(self):
        self.current_note = Note()
        self.update_editor()
        
    def save_note(self):
        if not self.current_note:
            self.current_note = Note()
            
        # Update note data from editor
        self.current_note.title = self.note_editor.title_edit.text()
        self.current_note.content = self.note_editor.content_edit.toPlainText()
        self.current_note.tags = [tag.strip() for tag in self.note_editor.tags_edit.text().split(",")]
        self.current_note.priority = self.note_editor.priority_combo.currentText()
        self.current_note.category = self.note_editor.category_combo.currentText()
        self.current_note.due_date = datetime.strptime(self.note_editor.due_date_edit.text(),
                                                     "%Y-%m-%d %H:%M")
        self.current_note.is_encrypted = self.note_editor.encrypt_check.isChecked()
        self.current_note.modified_at = datetime.now()
        
        # Add or update note in list
        if self.current_note not in self.notes:
            self.notes.append(self.current_note)
            
        self.update_note_list()
        self.save_notes()
        
        QMessageBox.information(self, "Success", "Note saved successfully!")
        
    def delete_note(self):
        if not self.current_note:
            return
            
        reply = QMessageBox.question(self, "Confirm Delete",
                                   "Are you sure you want to delete this note?",
                                   QMessageBox.Yes | QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            self.notes.remove(self.current_note)
            self.current_note = None
            self.update_editor()
            self.update_note_list()
            self.save_notes()
            
    def on_note_selected(self, item):
        note_index = self.note_list.note_list.row(item)
        self.current_note = self.notes[note_index]
        self.update_editor()
        
    def update_editor(self):
        if not self.current_note:
            self.note_editor.title_edit.clear()
            self.note_editor.content_edit.clear()
            self.note_editor.tags_edit.clear()
            self.note_editor.priority_combo.setCurrentText("low")
            self.note_editor.category_combo.setCurrentText("general")
            self.note_editor.due_date_edit.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))
            self.note_editor.encrypt_check.setChecked(False)
        else:
            self.note_editor.title_edit.setText(self.current_note.title)
            self.note_editor.content_edit.setText(self.current_note.content)
            self.note_editor.tags_edit.setText(", ".join(self.current_note.tags))
            self.note_editor.priority_combo.setCurrentText(self.current_note.priority)
            self.note_editor.category_combo.setCurrentText(self.current_note.category)
            self.note_editor.due_date_edit.setText(self.current_note.due_date.strftime("%Y-%m-%d %H:%M"))
            self.note_editor.encrypt_check.setChecked(self.current_note.is_encrypted)
            
    def update_note_list(self):
        self.note_list.note_list.clear()
        for note in self.notes:
            item = QListWidgetItem(note.title)
            item.setData(Qt.UserRole, note)
            self.note_list.note_list.addItem(item)
            
    def show_calendar(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Calendar View")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        calendar = QCalendarWidget()
        layout.addWidget(calendar)
        
        note_list = QListWidget()
        layout.addWidget(note_list)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def backup_notes(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Notes",
                                                 "", "JSON files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump([note.__dict__ for note in self.notes],
                             file, default=str)
                QMessageBox.information(self, "Success",
                                      "Notes backed up successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                   f"Error during backup: {str(e)}")
                
    def restore_notes(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Notes",
                                                 "", "JSON files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    notes_data = json.load(file)
                    self.notes = [Note(**data) for data in notes_data]
                self.update_note_list()
                QMessageBox.information(self, "Success",
                                      "Notes restored successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                   f"Error during restore: {str(e)}")
                
    def import_notes(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Notes",
                                                 "", "CSV files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        note = Note(
                            title=row['title'],
                            content=row['content'],
                            tags=row['tags'].split(','),
                            priority=row['priority'],
                            due_date=datetime.strptime(row['due_date'],
                                                     "%Y-%m-%d %H:%M"),
                            category=row['category']
                        )
                        self.notes.append(note)
                self.update_note_list()
                self.save_notes()
                QMessageBox.information(self, "Success",
                                      "Notes imported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                   f"Error during import: {str(e)}")
                
    def export_notes(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Notes",
                                                 "", "CSV files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.DictWriter(file,
                                          fieldnames=['title', 'content', 'tags',
                                                    'priority', 'due_date',
                                                    'category'])
                    writer.writeheader()
                    for note in self.notes:
                        writer.writerow({
                            'title': note.title,
                            'content': note.content,
                            'tags': ','.join(note.tags),
                            'priority': note.priority,
                            'due_date': note.due_date.strftime("%Y-%m-%d %H:%M"),
                            'category': note.category
                        })
                QMessageBox.information(self, "Success",
                                      "Notes exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                   f"Error during export: {str(e)}")
                
    def show_about(self):
        QMessageBox.about(self, "About Advanced Notes",
                         "Advanced Notes v1.0\n\n"
                         "A modern and feature-rich note-taking application.\n"
                         "Created with PyQt5.")
                         
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.note_editor.content_edit.setTextColor(color)
            
    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.note_editor.content_edit.setFont(font)
            
    def toggle_encryption(self):
        if not self.current_note:
            return
            
        if not self.current_note.is_encrypted:
            # Encrypt note
            key = Fernet.generate_key()
            f = Fernet(key)
            self.current_note.content = f.encrypt(
                self.current_note.content.encode()).decode()
            self.current_note.is_encrypted = True
        else:
            # Decrypt note
            key = Fernet.generate_key()
            f = Fernet(key)
            self.current_note.content = f.decrypt(
                self.current_note.content.encode()).decode()
            self.current_note.is_encrypted = False
            
        self.update_editor()
        
    def load_notes(self):
        try:
            if os.path.exists('notes.json'):
                with open('notes.json', 'r') as file:
                    notes_data = json.load(file)
                    self.notes = [Note(**data) for data in notes_data]
                self.update_note_list()
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Error loading notes: {str(e)}")
            
    def save_notes(self):
        try:
            with open('notes.json', 'w') as file:
                json.dump([note.__dict__ for note in self.notes],
                         file, default=str)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Error saving notes: {str(e)}")
            
    def closeEvent(self, event):
        self.save_notes()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create dark palette with modern colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(35, 35, 35))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    # Set application font
    app.setFont(QFont("Segoe UI", 9))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
