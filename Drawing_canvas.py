import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar,
    QLabel, QSlider, QPushButton, QMessageBox,
    QSizePolicy, QStatusBar
)
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, Signal, Slot
from PySide6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QCursor,
    QIcon, QPainterPath, QBrush, QPolygonF
)

def make_palette_icon(size: int = 32) -> QIcon:
    """Paint palette icon — mirip emoji 🎨."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    s = size / 32.0

    palette_path = QPainterPath()
    palette_path.moveTo(16*s, 3*s)
    palette_path.cubicTo(8*s,  3*s,  2*s,  9*s,  2*s,  16*s)
    palette_path.cubicTo(2*s,  23*s, 8*s,  29*s, 16*s, 29*s)
    palette_path.cubicTo(19*s, 29*s, 21*s, 27*s, 21*s, 25*s)
    palette_path.cubicTo(21*s, 23*s, 22*s, 22*s, 24*s, 22*s)
    palette_path.cubicTo(28*s, 22*s, 30*s, 20*s, 30*s, 17*s)
    palette_path.cubicTo(30*s, 9*s,  24*s, 3*s,  16*s, 3*s)
    palette_path.closeSubpath()

    p.setBrush(QBrush(QColor("#FADADD")))   # light pink base
    p.setPen(QPen(QColor("#c0636e"), 1.2*s))
    p.drawPath(palette_path)

    p.setBrush(QBrush(Qt.transparent))
    p.setPen(QPen(QColor("#c0636e"), 1.2*s))
    p.drawEllipse(QRectF(22*s, 23*s, 5*s, 5*s))

    dots = [
        (8*s,  10*s, "#e74c3c"),   # red
        (14*s,  7*s, "#3498db"),   # blue
        (20*s,  9*s, "#2ecc71"),   # green
        (24*s, 14*s, "#f39c12"),   # orange
        ( 8*s, 18*s, "#9b59b6"),   # purple
    ]
    r = 2.6*s
    for cx, cy, color in dots:
        p.setBrush(QBrush(QColor(color)))
        p.setPen(QPen(QColor("#ffffff"), 0.8*s))
        p.drawEllipse(QRectF(cx - r, cy - r, 2*r, 2*r))

    p.end()
    return QIcon(px)


def make_trash_icon(size: int = 18, color: str = "#ffffff") -> QIcon:
    """Ikon tempat sampah / trash can."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    s  = size / 18.0
    c  = QColor(color)
    pen = QPen(c, 1.4*s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    # lid
    p.drawLine(QPointF(3*s, 5*s),  QPointF(15*s, 5*s))
    p.drawLine(QPointF(7*s, 5*s),  QPointF(7*s,  3*s))
    p.drawLine(QPointF(7*s, 3*s),  QPointF(11*s, 3*s))
    p.drawLine(QPointF(11*s, 3*s), QPointF(11*s, 5*s))

    # body
    body_path = QPainterPath()
    body_path.moveTo(4.5*s, 6*s)
    body_path.lineTo(5*s,   15*s)
    body_path.lineTo(13*s,  15*s)
    body_path.lineTo(13.5*s, 6*s)
    p.drawPath(body_path)

    # vertical lines inside
    p.drawLine(QPointF(7.5*s,  7.5*s), QPointF(7.5*s,  13.5*s))
    p.drawLine(QPointF(9*s,    7.5*s), QPointF(9*s,    13.5*s))
    p.drawLine(QPointF(10.5*s, 7.5*s), QPointF(10.5*s, 13.5*s))

    p.end()
    return QIcon(px)

class Canvas(QWidget):
    mouseMoved = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CrossCursor))

        self._pen_color  = QColor("#e74c3c")
        self._pen_width  = 5
        self._last_point = QPoint()
        self._drawing    = False
        self._pixmap     = QPixmap(self.size())
        self._pixmap.fill(Qt.white)

    @Slot(QColor)
    def setColor(self, color: QColor):
        self._pen_color = color

    @Slot(int)
    def setBrushSize(self, size: int):
        self._pen_width = size

    @Slot()
    def clearCanvas(self):
        self._pixmap.fill(Qt.white)
        self.update()

    def resizeEvent(self, event):
        new_pixmap = QPixmap(self.size())
        new_pixmap.fill(Qt.white)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.end()
        self._pixmap = new_pixmap
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(
            self.rect().adjusted(0, 0, -10, -8),
            Qt.AlignBottom | Qt.AlignRight,
            "Double-click untuk clear"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing    = True
            self._last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        self.mouseMoved.emit(pos.x(), pos.y())

        if self._drawing and (event.buttons() & Qt.LeftButton):
            painter = QPainter(self._pixmap)
            pen = QPen(
                self._pen_color, self._pen_width,
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin,
            )
            painter.setPen(pen)
            painter.drawLine(self._last_point, pos)
            painter.end()
            self._last_point = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clearCanvas()

class ColorButton(QPushButton):
    colorSelected = Signal(QColor)

    def __init__(self, color: QColor, name: str, parent=None):
        super().__init__(parent)
        self._color    = color
        self._name     = name
        self._selected = False
        self.setFixedSize(32, 32)
        self.setToolTip(name)
        self._apply_style(False)
        self.clicked.connect(lambda: self.colorSelected.emit(self._color))

    def _apply_style(self, selected: bool):
        self._selected = selected
        self.update()   # trigger paintEvent

    def setSelected(self, selected: bool):
        self._apply_style(selected)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        if self._selected:
            # outer white ring
            p.setBrush(QBrush(QColor("#ffffff")))
            p.setPen(Qt.NoPen)
            p.drawEllipse(2, 2, w - 4, h - 4)
            # colour circle (slightly smaller)
            p.setBrush(QBrush(self._color))
            p.drawEllipse(5, 5, w - 10, h - 10)
        else:
            # full colour circle
            p.setBrush(QBrush(self._color))
            p.setPen(Qt.NoPen)
            p.drawEllipse(2, 2, w - 4, h - 4)

        p.end()

class DrawingCanvas(QMainWindow):
    colorChanged = Signal(QColor)

    COLORS = [
        ("#e74c3c", "Merah"),
        ("#3498db", "Biru"),
        ("#2ecc71", "Hijau"),
        ("#f39c12", "Oranye"),
        ("#2c3e50", "Hitam"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Canvas")
        self.resize(1000, 620)
        self._active_color_name = "Merah"
        self._last_x, self._last_y = 0, 0
        self._color_buttons: list[ColorButton] = []

        # ── window icon: paint palette ──
        self.setWindowIcon(make_palette_icon(64))

        self._build_ui()
        self._connect_signals()
        self._color_buttons[0].setSelected(True)

    def _build_ui(self):
        self._canvas = Canvas(self)
        self.setCentralWidget(self._canvas)

        toolbar = QToolBar("Tools", self)
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #2c3e50;
                padding: 6px 12px;
                spacing: 10px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        toolbar.addWidget(QLabel("Warna:"))
        for hex_color, name in self.COLORS:

            btn = ColorButton(QColor(hex_color), name)
            self._color_buttons.append(btn)
            toolbar.addWidget(btn)

        spacer1 = QWidget(); spacer1.setFixedWidth(20)
        toolbar.addWidget(spacer1)

        toolbar.addWidget(QLabel("Ukuran:"))
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setRange(1, 30)
        self._slider.setValue(5)
        self._slider.setFixedWidth(140)
        self._slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255,255,255,0.25);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px; height: 16px;
                margin: -5px 0;
                border-radius: 8px;
                background: #3498db;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 3px;
            }
        """)
        toolbar.addWidget(self._slider)

        self._size_label = QLabel("5px")
        self._size_label.setFixedWidth(36)
        toolbar.addWidget(self._size_label)

        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(stretch)

        self._clear_btn = QPushButton("  Clear")
        self._clear_btn.setIcon(make_trash_icon(18, "#ffffff"))
        self._clear_btn.setIconSize(self._clear_btn.sizeHint())
        self._clear_btn.setFixedHeight(32)
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 18px 0 12px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover   { background: #c0392b; }
            QPushButton:pressed { background: #a93226; }
        """)
        toolbar.addWidget(self._clear_btn)

        self._status = QStatusBar(self)
        self._status.setStyleSheet("""
            QStatusBar {
                background: #f0f0f0;
                color: #555;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 2px 8px;
            }
        """)
        self.setStatusBar(self._status)
        self._status.showMessage("X: 0 | Y: 0 | Warna: Merah | Brush: 5px")

    def _connect_signals(self):
        for btn in self._color_buttons:
            btn.colorSelected.connect(self._on_color_selected)

        self._slider.valueChanged.connect(self._canvas.setBrushSize)
        self._slider.valueChanged.connect(lambda v: self._size_label.setText(f"{v}px"))
        self._slider.valueChanged.connect(lambda _: self._update_status())

        self._canvas.mouseMoved.connect(self._update_status)
        self._clear_btn.clicked.connect(self._confirm_clear)

    @Slot(QColor)
    def _on_color_selected(self, color: QColor):
        for btn in self._color_buttons:
            is_selected = btn._color == color
            btn.setSelected(is_selected)
            if is_selected:
                self._active_color_name = btn._name
        self._canvas.setColor(color)
        self._update_status()

    @Slot(int, int)
    def _update_status(self, x: int = None, y: int = None):
        if x is not None:
            self._last_x, self._last_y = x, y
        brush = self._slider.value()
        self._status.showMessage(
            f"X: {self._last_x} | Y: {self._last_y} | "
            f"Warna: {self._active_color_name} | Brush: {brush}px"
        )

    @Slot()
    def _confirm_clear(self):
        reply = QMessageBox.question(
            self,
            "Konfirmasi Clear",
            "Apakah kamu yakin ingin menghapus semua gambar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._canvas.clearCanvas()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DrawingCanvas()
    window.show()
    sys.exit(app.exec())