import sys
import webbrowser
import random
import math
import html

from importlib import import_module

from brain import LumenCore
from archive_search import search_texts, display_results

QtWidgets = None
QtCore = None
QtGui = None

for base in ("PyQt5", "PySide6"):
    try:
        QtWidgets = import_module(f"{base}.QtWidgets")
        QtCore = import_module(f"{base}.QtCore")
        QtGui = import_module(f"{base}.QtGui")
        break
    except ImportError:
        continue

if QtWidgets is None:
    raise ImportError(
        "Neither PyQt5 nor PySide6 is installed"
    )

QApplication = QtWidgets.QApplication
QMainWindow = QtWidgets.QMainWindow
QWidget = QtWidgets.QWidget
QTextBrowser = QtWidgets.QTextBrowser
QLineEdit = QtWidgets.QLineEdit
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QPushButton = QtWidgets.QPushButton
QStackedWidget = QtWidgets.QStackedWidget
QLabel = QtWidgets.QLabel
QListWidget = QtWidgets.QListWidget
QTextEdit = QtWidgets.QTextEdit

QPainter = QtGui.QPainter
QColor = QtGui.QColor
QBrush = QtGui.QBrush
QFont = QtGui.QFont

Qt = QtCore.Qt
QTimer = QtCore.QTimer
QUrl = QtCore.QUrl

class CrownStar:

    def __init__(self, radius, offset, size):

        self.radius = radius
        self.offset = offset
        self.size = size

        self.x = 0
        self.y = 0

        self.glow = random.randint(170, 255)

    def update(self, center_x, center_y, rotation):

        angle = rotation + self.offset

        self.x = center_x + (
            math.cos(angle) * self.radius
        )

        self.y = center_y + (
            math.sin(angle) * self.radius
        )


class SnowParticle:

    def __init__(self, width, height):

        self.x = random.randint(0, width)
        self.y = random.randint(0, height)

        self.size = random.randint(1, 4)

        self.speed = random.uniform(0.5, 2.5)

        self.drift = random.uniform(-0.5, 0.5)

        self.opacity = random.randint(80, 200)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # ====================================================
        # VSTG OS IDENTITY
        # ====================================================

        self.setWindowTitle("VSTG OS | VEIL SYSTEMS")
        self.resize(1300, 800)

        # ====================================================
        # LUMEN CORE
        # ====================================================

        self.lumen = LumenCore()

        # ====================================================
        # TYPING SYSTEM
        # ====================================================

        self.type_queue = []
        self.is_typing = False

        # ====================================================
        # ANIMATION VARIABLES
        # ====================================================

        self.fog_offset = 0

        # ====================================================
        # SNOW PARTICLES
        # ====================================================

        self.snow_particles = []

        # ====================================================
        # CROWN LOADER
        # ====================================================

        self.crown_stars = []

        star_count = 7

        for i in range(star_count):

            offset = (
                math.pi * 2 / star_count
            ) * i

            self.crown_stars.append(

                CrownStar(
                    140,
                    offset,
                    18
                )

            )

        # ====================================================
        # BUILD INTERFACE
        # ====================================================

        self.setup_ui()

        # ====================================================
        # GENERATE SNOW
        # ====================================================

        for _ in range(120):

            self.snow_particles.append(
                SnowParticle(
                    self.width(),
                    self.height()
                )
            )

        # ====================================================
        # CROWN ANIMATION STATE
        # ====================================================

        self.searching = False
        self.crown_merge_progress = 0.0
        self.crown_rotation = 0
        self.crown_center_glow = 0

        # ====================================================
        # ANIMATION TIMER
        # ====================================================

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(
            self.update_animation
        )
        self.animation_timer.start(16)

        # ====================================================
        # BOOT
        # ====================================================

        self.boot_sequence()

    def setup_ui(self):

        self.setStyleSheet("""

            QMainWindow {
                background-color: #080d10;
            }

            QWidget {
                background: transparent;
                color: #d5e2dc;
                font-family: Consolas;
            }

            QLabel {
                color: #d5e2dc;
            }

            QTextBrowser {
                background-color: rgba(12, 19, 23, 230);
                color: #b8d4c5;
                border: 1px solid #263b32;
                padding: 16px;
                font-size: 14px;
                font-family: Consolas;
                selection-background-color: #28533c;
            }

            QLineEdit {
                background-color: rgba(12, 20, 23, 245);
                color: #e0f2e8;
                border: 1px solid #527b60;
                border-radius: 4px;
                padding: 13px;
                font-size: 14px;
                font-family: Consolas;
            }

            QLineEdit:focus {
                border: 1px solid #79bd8d;
            }

        """)

        # ================================================
        # MAIN LAYOUT
        # ================================================

        root = QHBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # ================================================
        # LEFT NAVIGATION
        # ================================================

        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(8)

        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setLayout(self.sidebar)

        self.sidebar.addWidget(
            QLabel("VEIL SYSTEMS")
        )

        self.sidebar.addSpacing(20)
        self.nav_buttons = []

        navigation_items = [
            ("01  OVERVIEW", 0),
            ("02  LUMEN", 1),
            ("03  ARCHIVE", 2),
            ("04  MEMORY", 3),
            ("05  SYSTEM", 4)
        ]

        for label, page_index in navigation_items:

            button = QPushButton(label)

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #91ad9b;
                    border: none;
                    text-align: left;
                    padding: 12px;
                    font-size: 12px;
                }

                QPushButton:hover {
                    background-color: rgba(70, 120, 85, 45);
                    color: #dcebe1;
                }
            """)

            button.clicked.connect(
                lambda checked=False, index=page_index:
                self.switch_page(index)
            )

            self.sidebar.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(13, 22, 25, 220);
                border: 1px solid #263b32;
            }

            QLabel {
                padding: 10px;
                font-size: 12px;
                color: #91ad9b;
            }
        """)

        # CENTER PANEL
        center = QVBoxLayout()
        center.setSpacing(12)

        self.title = QLabel("VEIL SYSTEMS")
        self.title.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            letter-spacing: 5px;
            color: #dcebe1;
        """)

        self.subtitle = QLabel("VSTG OS / LUMEN INTERFACE")
        self.subtitle.setStyleSheet("""
            font-size: 11px;
            color: #638c70;
            letter-spacing: 2px;
        """)

        center.addWidget(self.title)
        center.addWidget(self.subtitle)

        # PAGE CONTAINER
        self.pages = QStackedWidget()

        # OVERVIEW PAGE
        overview_page = QWidget()
        overview_layout = QVBoxLayout()
        overview_layout.setSpacing(12)

        self.output = QTextBrowser()
        self.output.setOpenExternalLinks(False)
        self.output.anchorClicked.connect(self.open_link)
        self.output.setFont(QFont("Consolas", 11))

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter a command...")
        self.input.returnPressed.connect(self.process_command)

        overview_layout.addWidget(self.output)
        overview_layout.addWidget(self.input)

        overview_page.setLayout(overview_layout)

        # ====================================================
        # LUMEN PAGE
        # ====================================================

        lumen_page = QWidget()
        lumen_layout = QVBoxLayout()
        lumen_layout.setSpacing(14)

        # HEADER

        lumen_header = QLabel("LUMEN INTELLIGENCE")
        lumen_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 3px;
            color: #c5f5d2;
        """)

        lumen_description = QLabel(
            "VEIL SYSTEMS / CORE INTERFACE"
        )

        lumen_description.setStyleSheet("""
            font-size: 10px;
            letter-spacing: 2px;
            color: #638c70;
        """)

        lumen_layout.addWidget(lumen_header)
        lumen_layout.addWidget(lumen_description)

        # CORE STATUS

        self.lumen_core_status = QLabel(
            "● CORE ONLINE"
        )

        self.lumen_core_status.setStyleSheet("""
            color: #62d889;
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
            background-color: rgba(70, 150, 95, 30);
            border: 1px solid #315d40;
        """)

        lumen_layout.addWidget(self.lumen_core_status)

        # CONVERSATION PANEL

        self.lumen_chat = QTextBrowser()
        self.lumen_chat.setFont(QFont("Consolas", 11))
        self.lumen_chat.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(5, 12, 14, 220);
                color: #c5d8cc;
                border: 1px solid #263b32;
                padding: 12px;
            }
        """)

        self.lumen_chat.append(
            '<span style="color:#62d889;">'
            '[LUMEN]</span> Core interface initialized.'
        )

        self.lumen_chat.append(
            '<span style="color:#638c70;">'
            '[LUMEN]</span> Awaiting input.'
        )

        lumen_layout.addWidget(self.lumen_chat, 1)

        # MESSAGE INPUT

        lumen_input_row = QHBoxLayout()

        self.lumen_input = QLineEdit()
        self.lumen_input.setPlaceholderText(
            "Communicate with Lumen..."
        )

        self.lumen_input.returnPressed.connect(
            self.send_lumen_message
        )

        self.lumen_send_button = QPushButton("SEND")

        self.lumen_send_button.clicked.connect(
            self.send_lumen_message
        )

        lumen_input_row.addWidget(self.lumen_input, 1)
        lumen_input_row.addWidget(self.lumen_send_button)

        lumen_layout.addLayout(lumen_input_row)

        lumen_page.setLayout(lumen_layout)

        # ARCHIVE PAGE
        archive_page = QWidget()
        archive_layout = QVBoxLayout()

        archive_layout.addWidget(QLabel("ARCHIVE ENGINE"))
        archive_layout.addWidget(
            QLabel("Search and retrieve archived knowledge.")
        )

        archive_page.setLayout(archive_layout)

        # ====================================================
        # MEMORY PAGE
        # ====================================================

        memory_page = QWidget()
        memory_layout = QVBoxLayout()
        memory_layout.setSpacing(12)

        memory_header = QLabel("LUMEN MEMORY ARCHIVE")
        memory_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 3px;
            color: #c5f5d2;
        """)

        memory_description = QLabel(
            "PERSISTENT STORAGE / MEMORY MANAGEMENT"
        )

        memory_description.setStyleSheet("""
            font-size: 10px;
            letter-spacing: 2px;
            color: #638c70;
        """)

        memory_layout.addWidget(memory_header)
        memory_layout.addWidget(memory_description)

        # SEARCH

        self.memory_search = QLineEdit()
        self.memory_search.setPlaceholderText(
            "Search stored memories..."
        )

        self.memory_search.returnPressed.connect(
            self.refresh_memory_page
        )

        memory_layout.addWidget(self.memory_search)

        # MEMORY LIST

        self.memory_list = QListWidget()
        self.memory_list.currentRowChanged.connect(
            self.load_selected_memory
        )

        memory_layout.addWidget(self.memory_list, 1)

        # MEMORY EDITOR

        memory_layout.addWidget(QLabel("MEMORY TITLE"))

        self.memory_title_input = QLineEdit()
        self.memory_title_input.setPlaceholderText(
            "Memory title..."
        )

        memory_layout.addWidget(self.memory_title_input)

        memory_layout.addWidget(QLabel("CATEGORY"))

        self.memory_category_input = QLineEdit()
        self.memory_category_input.setPlaceholderText(
            "general"
        )
        self.memory_category_input.setText("general")

        memory_layout.addWidget(self.memory_category_input)

        memory_layout.addWidget(QLabel("CONTENT"))

        self.memory_content_input = QTextEdit()
        self.memory_content_input.setPlaceholderText(
            "Memory contents..."
        )
        self.memory_content_input.setMaximumHeight(130)

        memory_layout.addWidget(self.memory_content_input)

        # ACTION BUTTONS

        memory_buttons = QHBoxLayout()

        self.memory_add_button = QPushButton("ADD MEMORY")
        self.memory_add_button.clicked.connect(
            self.add_memory
        )

        self.memory_update_button = QPushButton("UPDATE")
        self.memory_update_button.clicked.connect(
            self.update_memory
        )

        self.memory_delete_button = QPushButton("DELETE")
        self.memory_delete_button.clicked.connect(
            self.delete_memory
        )

        self.memory_refresh_button = QPushButton("REFRESH")
        self.memory_refresh_button.clicked.connect(
            self.refresh_memory_page
        )

        memory_buttons.addWidget(self.memory_add_button)
        memory_buttons.addWidget(self.memory_update_button)
        memory_buttons.addWidget(self.memory_delete_button)
        memory_buttons.addWidget(self.memory_refresh_button)

        memory_layout.addLayout(memory_buttons)

        self.memory_feedback = QLabel(
            "MEMORY DATABASE CONNECTED"
        )

        self.memory_feedback.setStyleSheet("""
            color: #62d889;
            font-size: 11px;
            padding: 6px;
        """)

        memory_layout.addWidget(self.memory_feedback)

        self.memory_confirm_input = QLineEdit()
        self.memory_confirm_input.setPlaceholderText(
            "Type DELETE to confirm memory deletion"
        )

        memory_layout.addWidget(self.memory_confirm_input)

        memory_page.setLayout(memory_layout)

        self.memory_records = []
        self.refresh_memory_page()

        # SYSTEM PAGE
        system_page = QWidget()
        system_layout = QVBoxLayout()

        system_layout.addWidget(QLabel("SYSTEM CONFIGURATION"))
        system_layout.addWidget(
            QLabel("VSTG OS settings and system information.")
        )

        system_page.setLayout(system_layout)

        # REGISTER PAGES
        self.pages.addWidget(overview_page)
        self.pages.addWidget(lumen_page)
        self.pages.addWidget(archive_page)
        self.pages.addWidget(memory_page)
        self.pages.addWidget(system_page)
        self.switch_page(0)

        center.addWidget(self.pages)

        center_widget = QWidget()
        center_widget.setLayout(center)

        # ================================================
        # RIGHT STATUS PANEL
        # ================================================

        status = QVBoxLayout()
        status.setSpacing(12)

        status.addWidget(QLabel("SYSTEM STATUS"))

        self.lumen_status = QLabel(
            "LUMEN\nINITIALIZING"
        )

        status.addWidget(self.lumen_status)

        status.addWidget(QLabel("MEMORY"))

        self.memory_count = QLabel("0 RECORDS")

        status.addWidget(self.memory_count)

        status.addStretch()

        status.addWidget(QLabel("VEIL SYSTEMS"))

        status_widget = QWidget()
        status_widget.setFixedWidth(200)
        status_widget.setLayout(status)

        status_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(13, 22, 25, 220);
                border: 1px solid #263b32;
            }

            QLabel {
                padding: 7px;
                font-size: 11px;
                color: #8fa99a;
            }
        """)


        # ================================================
        # ASSEMBLE INTERFACE
        # ================================================

        root.addWidget(sidebar_widget)
        root.addWidget(center_widget, 1)
        root.addWidget(status_widget)

        container = QWidget()

        container.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        container.setLayout(root)

        self.setCentralWidget(container)

        # ================================================
        # INITIAL STATUS
        # ================================================

        status_data = self.lumen.status()

        self.memory_count.setText(
            f"{status_data['memory_count']} RECORDS"
        )

        self.lumen_status.setText(
            "LUMEN\nOPERATIONAL"
        )

    def refresh_memory_page(self):

        query = self.memory_search.text().strip()

        if query:
            records = self.lumen.memory.recall(query, 100)
        else:
            records = self.lumen.memory.get_all(100)

        self.memory_records = records

        self.memory_list.blockSignals(True)
        self.memory_list.clear()

        for memory in records:

            self.memory_list.addItem(
                f"#{memory['id']}  |  {memory['title']}  "
                f"[{memory['category']}]"
            )

        self.memory_list.blockSignals(False)

        self.memory_title_input.clear()
        self.memory_category_input.setText("general")
        self.memory_content_input.clear()

        if hasattr(self, "memory_count"):
            self.memory_count.setText(
                f"{len(self.lumen.memory.get_all(100000))} RECORDS"
            )

        self.memory_feedback.setText(
            f"{len(records)} MEMORY RECORDS DISPLAYED"
        )

    def load_selected_memory(self, row):

        if row < 0 or row >= len(self.memory_records):
            return

        memory = self.memory_records[row]

        self.memory_title_input.setText(
            memory["title"]
        )

        self.memory_category_input.setText(
            memory["category"]
        )

        self.memory_content_input.setPlainText(
            memory["content"]
        )

        self.memory_feedback.setText(
            f"SELECTED MEMORY #{memory['id']}"
        )

    def add_memory(self):

        title = self.memory_title_input.text().strip()
        category = self.memory_category_input.text().strip()
        content = self.memory_content_input.toPlainText().strip()

        if not title or not content:

            self.memory_feedback.setText(
                "ERROR: TITLE AND CONTENT REQUIRED"
            )
            return

        if not category:
            category = "general"

        try:

            memory_id = self.lumen.memory.remember(
                title=title,
                content=content,
                category=category
            )

            self.refresh_memory_page()

            self.memory_feedback.setText(
                f"MEMORY #{memory_id} STORED"
            )

        except Exception as error:

            self.memory_feedback.setText(
                f"ERROR: {html.escape(str(error))}"
            )

    def update_memory(self):

        row = self.memory_list.currentRow()

        if row < 0 or row >= len(self.memory_records):

            self.memory_feedback.setText(
                "SELECT A MEMORY TO UPDATE"
            )
            return

        title = self.memory_title_input.text().strip()
        content = self.memory_content_input.toPlainText().strip()

        if not title or not content:

            self.memory_feedback.setText(
                "ERROR: TITLE AND CONTENT REQUIRED"
            )
            return

        memory = self.memory_records[row]
        memory_id = memory["id"]

        try:

            with self.lumen.memory.connection:

                self.lumen.memory.connection.execute("""
                    UPDATE memories
                    SET title = ?,
                        category = ?,
                        content = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    title,
                    self.memory_category_input.text().strip() or "general",
                    content,
                    __import__("datetime").datetime.now(
                        __import__("datetime").timezone.utc
                    ).isoformat(),
                    memory_id
                ))

            self.refresh_memory_page()

            self.memory_feedback.setText(
                f"MEMORY #{memory_id} UPDATED"
            )

        except Exception as error:

            self.memory_feedback.setText(
                f"ERROR: {html.escape(str(error))}"
            )

    def delete_memory(self):

        row = self.memory_list.currentRow()

        if row < 0 or row >= len(self.memory_records):

            self.memory_feedback.setText(
                "SELECT A MEMORY TO DELETE"
            )
            return

        memory = self.memory_records[row]

        confirmation = self.memory_confirm_input.text().strip()

        if confirmation != "DELETE":

            self.memory_feedback.setText(
                "TYPE DELETE IN THE CONFIRMATION FIELD"
            )
            return

        memory_id = memory["id"]

        self.lumen.memory.forget(memory_id)

        self.memory_confirm_input.clear()

        self.refresh_memory_page()

        self.memory_feedback.setText(
            f"MEMORY #{memory_id} DELETED"
        )

    def send_lumen_message(self):

        message = self.lumen_input.text().strip()

        if not message:
            return

        safe_message = html.escape(message)

        self.lumen_chat.append(
            f'<span style="color:#8fdcff;">'
            f'[YOU]</span> {safe_message}'
        )

        self.lumen_input.clear()

        lowered = message.lower()

        if lowered == "status":

            status = self.lumen.status()

            response = (
                f"Core: {status['name']}<br>"
                f"Version: {status['version']}<br>"
                f"Memories: {status['memory_count']}<br>"
                "All reported systems operational."
            )

        elif lowered.startswith("recall "):

            query = message[7:].strip()
            memories = self.lumen.memory.recall(query)

            if memories:

                response = "<b>MEMORY RECORDS FOUND</b><br><br>"

                for memory in memories:

                    response += (
                        f"<span style='color:#62d889;'>"
                        f"{html.escape(memory['title'])}"
                        f"</span><br>"
                        f"{html.escape(memory['content'])}"
                        f"<br><br>"
                    )

            else:

                response = "No matching memories found."

        elif lowered == "help":

            response = (
                "AVAILABLE COMMANDS<br><br>"
                "status — Check core status<br>"
                "recall [keyword] — Search memories<br>"
                "help — Display commands"
            )

        else:

            response = (
                "I received your message, but conversational "
                "reasoning is not connected yet. "
                "Try 'help' to see available commands."
            )

        self.lumen_chat.append(
            f'<span style="color:#62d889;">'
            f'[LUMEN]</span> {response}'
        )

    def switch_page(self, index):

        # Change the displayed page
        self.pages.setCurrentIndex(index)

        # Update navigation appearance
        for i, button in enumerate(self.nav_buttons):

            if i == index:

                button.setStyleSheet("""
                    QPushButton {
                        background-color: #244b35;
                        color: #d8ffe3;
                        border: 1px solid #62d889;
                        border-left: 6px solid #62d889;
                        text-align: left;
                        padding: 12px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)

            else:

                button.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #91ad9b;
                        border: 1px solid transparent;
                        border-left: 6px solid transparent;
                        text-align: left;
                        padding: 12px;
                        font-size: 12px;
                    }

                    QPushButton:hover {
                        background-color: rgba(70, 120, 85, 45);
                        color: #dcebe1;
                    }
                """)

    def open_link(self, url):

        webbrowser.open(
            url.toString()
        )

    def type_line(self, text, delay=8):

        self.type_queue.append(
            (text, delay)
        )

        if not self.is_typing:

            self.process_type_queue()

    def process_type_queue(self):

        if not self.type_queue:

            self.is_typing = False
            return

        self.is_typing = True

        text, delay = self.type_queue.pop(0)

        cursor = self.output.textCursor()

        cursor.movePosition(
            cursor.MoveOperation.End
        )

        cursor.insertBlock()

        # HTML lines render instantly
        if "<" in text and ">" in text:

            cursor.insertHtml(text)

            self.output.setTextCursor(cursor)

            self.output.ensureCursorVisible()

            self.is_typing = False

            QTimer.singleShot(
                1,
                self.process_type_queue
            )

            return

        current_index = 0

        self.type_timer = QTimer()

        def update_text():

            nonlocal current_index

            if current_index < len(text):

                cursor.insertText(
                    text[current_index]
                )

                current_index += 1

                self.output.setTextCursor(cursor)

                self.output.ensureCursorVisible()

            else:

                self.type_timer.stop()

                self.is_typing = False

                self.process_type_queue()

        self.type_timer.timeout.connect(
            update_text
        )

        self.type_timer.start(delay)

    def boot_sequence(self):

        self.type_line(
            "[VEIL SYSTEMS]"
        )

        self.type_line(
            "[VSTG OS KERNEL INITIALIZED]"
        )

        self.type_line(
            "[LUMEN CORE CONNECTED]"
        )

        self.type_line(
            "[MEMORY DATABASE ONLINE]"
        )

        self.type_line(
            "[ARCHIVE ENGINE CONNECTED]"
        )

        self.type_line(
            "[INTERFACE SYSTEMS STABLE]"
        )

        self.type_line("")

        self.type_line(
            "[LUMEN] All primary systems operational."
        )

        self.type_line("")

        self.type_line(
            "AVAILABLE COMMANDS"
        )

        self.type_line(
            "help       - Command index"
        )

        self.type_line(
            "status     - System status"
        )

        self.type_line(
            "remember   - Memory interface (coming soon)"
        )

        self.type_line(
            "recall     - Search stored memories"
        )

        self.type_line(
            "invoke     - Search Archive"
        )

        self.type_line(
            "purge      - Clear terminal"
        )

        self.type_line(
            "descend    - Shut down"
        )

        self.type_line("-" * 70)

    def process_command(self):

        command = self.input.text().strip()

        if not command:
            return

        self.type_line(
            f"[VSTG OS] > {html.escape(command)}"
        )

        lowered = command.lower()

        # ================================================
        # CLEAR TERMINAL
        # ================================================

        if lowered == "purge":

            self.output.clear()
            self.boot_sequence()

        # ================================================
        # EXIT
        # ================================================

        elif lowered == "descend":

            self.lumen.shutdown()
            self.close()

        # ================================================
        # COMMAND INDEX
        # ================================================

        elif lowered == "doctrine" or lowered == "help":

            self.type_line("")
            self.type_line("=== VSTG OS COMMAND INDEX ===")
            self.type_line("")
            self.type_line("invoke <keyword> <amount>  - Search Archive")
            self.type_line("status                    - Lumen system status")
            self.type_line("remember                  - Store a memory")
            self.type_line("recall <keyword>          - Search memories")
            self.type_line("purge                     - Clear terminal")
            self.type_line("descend                   - Shut down VSTG OS")

        # ================================================
        # LUMEN STATUS
        # ================================================

        elif lowered == "status":

            status = self.lumen.status()

            self.type_line("")
            self.type_line("[LUMEN SYSTEM STATUS]")
            self.type_line(f"CORE :: {status['name']}")
            self.type_line(f"VERSION :: {status['version']}")
            self.type_line(f"MEMORIES :: {status['memory_count']}")
            self.type_line("[CORE OPERATIONAL]")

        # ================================================
        # STORE MEMORY
        # ================================================

        elif lowered == "remember":

            title = self.input.text().strip()

            self.type_line(
                "[MEMORY INPUT REQUIRED]"
            )

            self.type_line(
                "Use the dedicated memory interface coming soon."
            )

        # ================================================
        # RECALL MEMORY
        # ================================================

        elif lowered.startswith("recall "):

            query = command[7:].strip()

            if not query:

                self.type_line("[EMPTY MEMORY QUERY]")

            else:

                memories = self.lumen.memory.recall(query)

                if not memories:

                    self.type_line("[NO MATCHING MEMORIES]")

                else:

                    self.type_line(
                        f"[MEMORIES FOUND :: {len(memories)}]"
                    )

                    for memory in memories:

                        self.type_line("")
                        self.type_line(
                            f"MEMORY :: {html.escape(memory['title'])}"
                        )
                        self.type_line(
                            f"CATEGORY :: {html.escape(memory['category'])}"
                        )
                        self.type_line(
                            html.escape(memory['content'])
                        )

        # ================================================
        # ARCHIVE SEARCH
        # ================================================

        elif lowered.startswith("invoke "):

            parts = command.split()

            if len(parts) < 2:

                self.type_line("[INVALID INVOCATION]")

            else:

                amount = 25

                if parts[-1].isdigit():

                    amount = int(parts[-1])
                    keyword = " ".join(parts[1:-1])

                else:

                    keyword = " ".join(parts[1:])

                amount = max(1, min(amount, 500))

                if keyword:

                    self.search_archive(keyword, amount)

                else:

                    self.type_line("[EMPTY SEARCH QUERY]")

        # ================================================
        # UNKNOWN COMMAND
        # ================================================

        else:

            self.type_line("[UNKNOWN COMMAND]")
            self.type_line("Type 'help' for the command index.")

        self.input.clear()

    def search_archive(self, keyword, amount):

        self.searching = True

        self.type_line("[LUMEN CONNECTED TO ARCHIVE ENGINE]")
        self.type_line(f"[SEARCHING FOR :: {keyword}]")
        self.type_line(f"[RELIC LIMIT :: {amount}]")

        try:

            self.type_line("[SCANNING ARCHIVE DATABASE...]")

            # Use the rebuilt Archive Engine
            results = search_texts(keyword, amount)

            if not results:

                self.type_line("[NO RELICS FOUND]")
                return

            self.type_line("")
            self.type_line(
                f"[TOTAL RELICS FOUND :: {len(results)}]"
            )

            for item in results:

                title = html.escape(
                    str(item.get("title", "Unknown Relic"))
                )

                identifier = str(
                    item.get("identifier", "unknown")
                )

                downloads = int(
                    item.get("downloads", 0) or 0
                )

                link = item.get("url", "")

                safe_link = html.escape(
                    str(link),
                    quote=True
                )

                self.type_line("")

                self.type_line(
                    "════════════════════════════════════════════════════"
                )

                self.type_line(
                    f'<span style="color:#9fe3ff;">'
                    f'RELIC :: {title}</span>'
                )

                self.type_line(
                    f"IDENTIFIER :: {identifier}"
                )

                self.type_line(
                    f"DOWNLOADS :: {downloads}"
                )

                self.type_line(
                    f'<a href="{safe_link}" '
                    f'style="color:#8fdcff;">'
                    f'OPEN ARCHIVE RECORD</a>'
                )

                self.type_line(
                    "════════════════════════════════════════════════════"
                )

            self.type_line("")
            self.type_line("[ARCHIVE SEARCH COMPLETE]")

        except Exception as error:

            self.type_line(
                f"[ARCHIVE ERROR] {html.escape(str(error))}"
            )

        finally:

            self.searching = False

    def update_animation(self):

        self.fog_offset += 1

        self.crown_rotation += 0.005
        self.crown_center_glow += 0.5

        for star in self.crown_stars:

            orbit_x = math.cos(
                self.crown_rotation + star.offset
            ) * star.radius

            orbit_y = math.sin(
                self.crown_rotation + star.offset
            ) * star.radius

            star.x_offset = orbit_x
            star.y_offset = orbit_y

        for particle in self.snow_particles:

            particle.y += particle.speed
            particle.x += particle.drift

            if particle.y > self.height():

                particle.y = random.randint(-100, 0)
                particle.x = random.randint(
                    0,
                    self.width()
                )

        self.update()

    def draw_crown_loader(self, painter):

        center_x = self.width() // 2
        center_y = 130

        #
        # CENTER GEM STAR
        #

        glow = 200 + int(
            math.sin(self.crown_center_glow) * 55
        )

        #
        # GOLD OUTER GLOW
        #

        painter.setBrush(
            QColor(
                255,
                215,
                90,
                glow
            )
        )

        painter.setPen(
            QColor(
                255,
                240,
                170,
                255
            )
        )

        self.draw_star(
            painter,
            center_x,
            center_y,
            42,
            center=True
        )

        #
        # GREEN GEM CORE
        #

        painter.setBrush(
            QColor(
                80,
                255,
                170,
                255
            )
        )

        painter.setPen(
            QColor(
                180,
                255,
                220,
                255
            )
        )

        painter.drawEllipse(
            center_x - 10,
            center_y - 10,
            20,
            20
        )

        #
        # ORBITING CROWN STARS
        #

        for star in self.crown_stars:

            star.update(
                center_x,
                center_y,
                self.crown_rotation
            )

            self.draw_star(
                painter,
                int(star.x),
                int(star.y),
                star.size
            )

    def draw_star(
        self,
        painter,
        x,
        y,
        size,
        center=False
    ):

        painter.save()

        painter.translate(x, y)

        if center:
            painter.scale(1.45, 0.82)
        else:
            painter.scale(1.08, 1.22)

        path = QtGui.QPainterPath()

        pts = [
            QtCore.QPointF(0, -size * 2.7),

            QtCore.QPointF(size * 0.18, -size * 0.42),
            QtCore.QPointF(size * 1.15, 0),

            QtCore.QPointF(size * 0.18, size * 0.42),
            QtCore.QPointF(0, size * 2.7),

            QtCore.QPointF(-size * 0.18, size * 0.42),
            QtCore.QPointF(-size * 1.15, 0),

            QtCore.QPointF(-size * 0.18, -size * 0.42),
        ]

        path.moveTo(pts[0])

        for pt in pts[1:]:
            path.lineTo(pt)

        path.closeSubpath()

        #
        # GOLD METAL
        #

        gold = QtGui.QLinearGradient(
            -size,
            -size,
            size,
            size
        )

        gold.setColorAt(
            0,
            QColor(255, 245, 170)
        )

        gold.setColorAt(
            0.45,
            QColor(255, 210, 90)
        )

        gold.setColorAt(
            1,
            QColor(170, 120, 30)
        )

        painter.setBrush(gold)

        painter.setPen(
            QtGui.QPen(
                QColor(255, 240, 170),
                2
            )
        )

        painter.drawPath(path)

        #
        # INNER METAL DETAIL
        #

        painter.setPen(
            QtGui.QPen(
                QColor(255, 255, 220, 90),
                1
            )
        )

        painter.drawLine(
            QtCore.QPointF(0, -size * 1.8),
            QtCore.QPointF(0, size * 1.8)
        )

        painter.drawLine(
            QtCore.QPointF(-size * 0.7, 0),
            QtCore.QPointF(size * 0.7, 0)
        )

        #
        # CENTER GEM
        #

        if center:

            gem_size = size * 0.5

            gem = QtGui.QPainterPath()

            gem.moveTo(
                0,
                -gem_size * 1.25
            )

            gem.lineTo(
                gem_size * 0.72,
                0
            )

            gem.lineTo(
                0,
                gem_size * 1.4
            )

            gem.lineTo(
                -gem_size * 0.72,
                0
            )

            gem.closeSubpath()

            emerald = QtGui.QLinearGradient(
                0,
                -gem_size,
                0,
                gem_size
            )

            emerald.setColorAt(
                0,
                QColor(170, 255, 210)
            )

            emerald.setColorAt(
                0.5,
                QColor(70, 255, 160)
            )

            emerald.setColorAt(
                1,
                QColor(10, 120, 70)
            )

            painter.setBrush(emerald)

            painter.setPen(
                QtGui.QPen(
                    QColor(220, 255, 240),
                    1
                )
            )

            painter.drawPath(gem)

        painter.restore()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        self.draw_crown_loader(painter)

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        for particle in self.snow_particles:

            color = QColor(
                220,
                255,
                235,
                particle.opacity
            )

            painter.setBrush(
                QBrush(color)
            )

            painter.drawEllipse(
                int(particle.x),
                int(particle.y),
                particle.size,
                particle.size
            )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())