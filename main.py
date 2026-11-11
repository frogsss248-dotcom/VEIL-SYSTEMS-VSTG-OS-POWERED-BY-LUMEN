import sys
import requests
import webbrowser
import random
import math

from importlib import import_module

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
QLabel = QtWidgets.QLabel

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

        self.setWindowTitle(
            "FENRIME ARCHIVE SYSTEM"
        )

        self.resize(1300, 800)

        # typing system
        self.type_queue = []
        self.is_typing = False

        # animation vars
        self.fog_offset = 0

        # snow
        self.snow_particles = []

        # crown loader
        self.crown_stars = []

        star_count = 7

        for i in range(star_count):

            offset = (
                math.pi * 2 / star_count
            ) * i

            self.crown_stars.append(

                CrownStar(
                    140,       # orbit radius
                    offset,    # angle offset
                    18         # star size
                )

            )

        # build UI
        self.setup_ui()

        # generate snow
        for _ in range(120):

            self.snow_particles.append(
                SnowParticle(
                    self.width(),
                    self.height()
                )
            )

        # crown animation
        self.searching = False
        self.crown_merge_progress = 0.0
        self.crown_rotation = 0
        self.crown_center_glow = 0
        
        # animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(
            self.update_animation
        )
        self.animation_timer.start(16)

        # boot
        self.boot_sequence()

    def setup_ui(self):

        self.setStyleSheet("""

            QMainWindow {
                background-color: #07111a;
            }

            QWidget {
                background: transparent;
            }

            QTextBrowser {
                background-color: rgba(
                    10,
                    18,
                    28,
                    215
                );

                color: #b8d4e8;

                border: 2px solid #2e3c34;

                padding: 20px;

                font-size: 20px;

                font-family: Consolas;

                selection-background-color: #415248;
            }

            QLineEdit {
                background-color: rgba(
                    14,
                    24,
                    38,
                    225
                );

                color: #d9ecff;

                border: 2px solid #394940;

                padding: 12px;

                font-size: 15px;

                font-family: Consolas;
            }

            QLabel {
                color: #d4ddd6;

                font-size: 28px;

                font-weight: bold;

                letter-spacing: 4px;

                padding: 10px;

                background: transparent;
            }

        """)

        self.layout = QVBoxLayout()

        self.title = QLabel(
            "THE SOVEREIGN ARCHIVES"
        )

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.output = QTextBrowser()

        self.output.setOpenExternalLinks(False)

        self.output.anchorClicked.connect(
            self.open_link
        )

        self.output.setFont(
            QFont("Consolas", 11)
        )

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "invoke archive query..."
        )

        self.input.returnPressed.connect(
            self.process_command
        )

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        container = QWidget()
        container.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        container.setLayout(self.layout)

        self.setCentralWidget(container)

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
            "[FENRIME ARCHIVE SYSTEM INITIALIZED]"
        )

        self.type_line(
            "[ARCHIVE VAULTS UNSEALED]"
        )

        self.type_line(
            "[CROWN SYNCHRONIZATION STABLE]"
        )

        self.type_line(
            "[CRYSTAL RESONANCE ACTIVE]"
        )

        self.type_line(
            "[RELIC INDEX READY]"
        )

        self.type_line("")

        self.type_line("COMMANDS")

        self.type_line(
            "invoke <keyword> <amount>"
        )

        self.type_line("purge")
        self.type_line("doctrine")
        self.type_line("descend")

        self.type_line("-" * 70)

    def process_command(self):

        command = self.input.text().strip()

        if not command:
            return

        self.type_line(
            f"[DREADRIME//ARCHIVE] > {command}"
        )

        lowered = command.lower()

        if lowered == "purge":

            self.output.clear()

            self.boot_sequence()

        elif lowered == "descend":

            self.close()

        elif lowered == "doctrine":

            self.type_line("")
            self.type_line("COMMAND INDEX")
            self.type_line("invoke <keyword> <amount>")
            self.type_line("purge")
            self.type_line("descend")

        elif lowered.startswith("invoke "):

            parts = command.split()

            if len(parts) < 2:

                self.type_line(
                    "[INVALID INVOCATION]"
                )

                self.input.clear()

                return

            amount = 25

            if parts[-1].isdigit():

                amount = int(parts[-1])

                keyword = " ".join(parts[1:-1])

            else:

                keyword = " ".join(parts[1:])

            amount = max(
                1,
                min(amount, 500)
            )

            self.search_archive(
                keyword,
                amount
            )

        else:

            self.type_line(
                "[UNKNOWN COMMAND]"
            )

            self.type_line(
                "Type 'doctrine' for command index."
            )

        self.input.clear()

    def search_archive(self, keyword, amount):

        self.searching = True

        self.type_line("[CROWN SYNCHRONIZING...]")
        self.type_line(f"[SEARCHING FOR :: {keyword}]")
        self.type_line(f"[RELIC LIMIT :: {amount}]")

        base_url = "https://archive.org/advancedsearch.php"

        all_results = []
        seen_ids = set()

        pages = max(1, (amount + 49) // 50)

        try:

            for page in range(1, pages + 1):

                self.type_line(
                    f"[SCANNING PAGE {page}]"
                )

                query = f"""
                ({keyword})
                AND mediatype:texts
                AND NOT mediatype:movies
                AND NOT mediatype:audio
                AND NOT mediatype:web
                """

                params = {
                    "q": query,
                    "fl[]": [
                        "identifier",
                        "title",
                        "downloads",
                        "year"
                    ],
                    "rows": 50,
                    "page": page,
                    "sort[]": "downloads desc",
                    "output": "json"
                }

                response = requests.get(
                    base_url,
                    params=params
                )

                data = response.json()

                results = data["response"]["docs"]

                for item in results:

                    identifier = item.get(
                        "identifier",
                        ""
                    )

                    if identifier not in seen_ids:

                        seen_ids.add(identifier)

                        all_results.append(item)

            if not all_results:

                self.type_line(
                    "[NO RELICS FOUND]"
                )

                return

            sorted_results = sorted(
                all_results,
                key=lambda x: int(
                    x.get("downloads", 0) or 0
                ),
                reverse=True
            )

            sorted_results = sorted_results[:amount]

            self.type_line("")
            self.type_line(
                f"[TOTAL RELICS FOUND :: {len(sorted_results)}]"
            )

            for item in sorted_results:

                title = item.get(
                    "title",
                    "Unknown Relic"
                )

                identifier = item.get(
                    "identifier",
                    "unknown"
                )

                downloads = int(
                    item.get("downloads", 0) or 0
                )

                year = item.get(
                    "year",
                    "Unknown"
                )

                link = (
                    f"https://archive.org/details/"
                    f"{identifier}"
                )

                self.type_line("")

                self.type_line(
                    "════════════════════════════════════════════════════"
                )

                self.type_line(
                    f'<span style="color:#9fe3ff;">RELIC :: {title}</span>'
                )

                self.type_line(
                    f"YEAR :: {year}"
                )

                self.type_line(
                    f"DOWNLOADS :: {downloads}"
                )

                self.type_line(
                    f'<a href="{link}" '
                    f'style="color:#8fdcff;">'
                    f'{link}</a>'
                )

                self.type_line(
                    "════════════════════════════════════════════════════"
                )

            self.type_line("")
            self.type_line(
                "[ARCHIVE SEARCH COMPLETE]"
            )

        except Exception as e:

            self.type_line(
                f"[SYSTEM ERROR] {e}"
            )

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