import json
import re
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QEvent, QPoint, QRect
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QSlider,
    QTabWidget,
    QTabBar,
    QSizeGrip,
    QLayout,
    QSizePolicy,
    QToolButton,
    QWidgetItem,
    QTextEdit,
    QMenu,
    QVBoxLayout,
    QWidget,
)


class TransparentNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_path = None
        self.project_name = None
        self.notes = []
        self.project_meta = {'name': '', 'notes': []}
        # default projects folder - uses user's home directory for portability and security
        self.app_root = Path.home() / "AppData" / "Local" / "TransparentNotes" / "Projects"
        self.app_root.mkdir(parents=True, exist_ok=True)

        self.setWindowTitle('Notes')
        self.setMinimumSize(QSize(760, 520))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        self.central_layout.setSpacing(10)
        self.central_widget.setStyleSheet('background: transparent;')

        self.background_widget = QWidget()
        self.background_widget.setObjectName('background_widget')
        self.background_widget.setStyleSheet(
            '#background_widget { background: rgba(22, 26, 40, 0.88); border: 1px solid rgba(255,255,255,0.18); border-radius: 24px; }'
            'QLabel, QPushButton, QSlider { color: #e6e6ef; }'
            'QPushButton { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14); border-radius: 18px; padding: 8px 12px; }'
            'QPushButton:hover { background: rgba(255,255,255,0.14); }'
            'QSlider::groove:horizontal { height: 8px; background: rgba(255,255,255,0.16); border-radius: 4px; }'
            'QSlider::handle:horizontal { width: 16px; background: rgba(255,255,255,0.95); border-radius: 8px; margin: -4px 0; }'
            'QTabWidget::pane { background: transparent; border: none; }'
            'QTabBar::tab { background: rgba(255,255,255,0.08); color: #ececf7; padding: 10px 14px; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 2px; }'
            'QTabBar::tab:selected { background: rgba(255,255,255,0.18); }'
        )
        self.background_layout = QVBoxLayout(self.background_widget)
        self.background_layout.setContentsMargins(18, 18, 18, 18)
        self.background_layout.setSpacing(12)

        self.top_bar = QWidget()
        self.top_bar.setStyleSheet('background: transparent;')
        self.top_bar.installEventFilter(self)
        self.background_widget.installEventFilter(self)
        self.central_widget.installEventFilter(self)
        top_layout = QVBoxLayout()
        self.top_bar.setLayout(top_layout)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        title_row = QWidget()
        title_layout = QHBoxLayout()
        title_row.setLayout(title_layout)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        self.title_label = QLabel('Notes')
        self.title_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.opacity_controls = QWidget()
        slider_layout = QVBoxLayout()
        self.opacity_controls.setLayout(slider_layout)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(4)

        self.opacity_label = QLabel('85%')
        self.opacity_label.setStyleSheet('color: #d8d8e0; font-size: 10px;')
        self.opacity_label.setAlignment(Qt.AlignRight)
        slider_layout.addWidget(self.opacity_label)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(85)
        self.opacity_slider.setFixedSize(160, 10)
        self.opacity_slider.valueChanged.connect(self.opacity_slider_changed)
        self.opacity_slider.setStyleSheet(
            'QSlider::groove:horizontal { height: 6px; background: rgba(255,255,255,0.16); border-radius: 3px; }'
            'QSlider::handle:horizontal { width: 10px; height: 10px; background: rgba(255,255,255,0.9); border-radius: 5px; margin: -2px 0; }'
        )
        slider_layout.addWidget(self.opacity_slider)
        title_layout.addWidget(self.opacity_controls)

        self.min_button = QPushButton('—')
        self.min_button.setFixedSize(28, 28)
        self.min_button.setStyleSheet(
            'color: white; background: rgba(255,255,255,0.06); border: none; border-radius: 14px; font-weight: 600;'
        )
        self.min_button.clicked.connect(self.handle_minimize)
        title_layout.addWidget(self.min_button)

        self.max_button = QPushButton('•')
        self.max_button.setFixedSize(28, 28)
        self.max_button.setStyleSheet(
            'color: white; background: rgba(255,255,255,0.06); border: none; border-radius: 14px;'
        )
        self.max_button.clicked.connect(self.toggle_maximize_restore)
        title_layout.addWidget(self.max_button)

        self.close_button = QPushButton('✕')
        self.close_button.setFixedSize(28, 28)
        self.close_button.setStyleSheet(
            'color: white; background: rgba(255,255,255,0.08); border: none; border-radius: 14px;'
        )
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        self.project_label = QLabel('Nenhum projeto')
        self.project_label.setStyleSheet('color: white; font-size: 24px; font-weight: 700; letter-spacing: 0.2px;')

        self.drag_handle = QLabel()
        self.drag_handle.setFixedSize(72, 6)
        self.drag_handle.setStyleSheet('background: rgba(255,255,255,0.24); border-radius: 3px;')
        self.drag_handle.setCursor(Qt.OpenHandCursor)
        self.drag_handle.installEventFilter(self)

        top_layout.addWidget(title_row)
        top_layout.addWidget(self.project_label)
        top_layout.addWidget(self.drag_handle, alignment=Qt.AlignHCenter)
        self.background_layout.addWidget(self.top_bar)

        self.action_bar = QWidget()
        self.action_bar.setStyleSheet('background: transparent;')
        action_layout = QHBoxLayout(self.action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        # FlowLayout implementation for wrapping tab buttons
        class FlowLayout(QLayout):
            def __init__(self, parent=None, margin=0, spacing=6):
                super().__init__(parent)
                self._items = []
                self.setContentsMargins(margin, margin, margin, margin)
                self.setSpacing(spacing)

            def addItem(self, item):
                self._items.append(item)

            def addWidget(self, widget):
                self.addItem(QWidgetItem(widget))

            def count(self):
                return len(self._items)

            def itemAt(self, index):
                return self._items[index] if 0 <= index < len(self._items) else None

            def takeAt(self, index):
                if 0 <= index < len(self._items):
                    return self._items.pop(index)
                return None

            def removeWidget(self, widget):
                for i, item in enumerate(self._items):
                    if item.widget() is widget:
                        self._items.pop(i)
                        return True
                return False

            def expandingDirections(self):
                return Qt.Orientations(Qt.Horizontal)

            def hasHeightForWidth(self):
                return True

            def heightForWidth(self, width):
                height = self.doLayout(QRect(0, 0, width, 0), True)
                return height

            def setGeometry(self, rect):
                super().setGeometry(rect)
                self.doLayout(rect, False)

            def sizeHint(self):
                return self.minimumSize()

            def minimumSize(self):
                size = QSize(0, 0)
                for item in self._items:
                    size = size.expandedTo(item.minimumSize())
                size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
                return size

            def doLayout(self, rect, testOnly):
                x = rect.x()
                y = rect.y()
                lineHeight = 0
                spaceX = self.spacing()
                spaceY = self.spacing()
                for item in self._items:
                    widget = item.widget()
                    hint = widget.sizeHint()
                    w = hint.width()
                    h = hint.height()
                    if x + w > rect.x() + rect.width() and lineHeight > 0:
                        x = rect.x()
                        y += lineHeight + spaceY
                        lineHeight = 0
                    if not testOnly:
                        item.setGeometry(QRect(QPoint(x, y), hint))
                    x += w + spaceX
                    lineHeight = max(lineHeight, h)
                return y + lineHeight - rect.y()

        # create container for wrapping tab buttons (will be placed above editor)
        self.tabs_container = QWidget()
        self.tabs_container.setStyleSheet('background: transparent; border-radius: 24px;')
        self.tabs_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tabs_container.setMinimumHeight(44)
        # We'll manage tab button positions manually (wrap to new lines)
        self._tab_buttons = []

        self.new_project_button = QPushButton('Novo projeto')
        self.new_project_button.clicked.connect(self.create_project)
        self.new_project_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.new_project_button)

        self.open_button = QPushButton('Abrir projeto')
        self.open_button.clicked.connect(self.open_project)
        self.open_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.open_button)

        self.rename_project_button = QPushButton('Renomear projeto')
        self.rename_project_button.clicked.connect(self.rename_project)
        self.rename_project_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.rename_project_button)

        self.delete_project_button = QPushButton('Excluir projeto')
        self.delete_project_button.clicked.connect(self.delete_project)
        self.delete_project_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.delete_project_button)

        self.new_button = QPushButton('Nova aba')
        self.new_button.clicked.connect(self.create_note)
        self.new_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.new_button)

        self.save_button = QPushButton('Salvar tudo')
        self.save_button.clicked.connect(self.save_all_notes)
        self.save_button.setStyleSheet(self._button_style())
        action_layout.addWidget(self.save_button)

        action_layout.addStretch()

        self.background_layout.addWidget(self.action_bar)


        self.editor_panel = QWidget()
        # keep the editor panel visually minimal so tabs appear to float
        self.editor_panel.setStyleSheet('background: transparent; border: none;')
        editor_layout = QVBoxLayout(self.editor_panel)
        editor_layout.setContentsMargins(12, 12, 12, 12)
        editor_layout.setSpacing(10)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_note_tab)
        try:
            self.tab_widget.tabBarDoubleClicked.connect(self.rename_note)
        except AttributeError:
            pass
        self.tab_widget.setStyleSheet(
            'QTabWidget { background: transparent; }'
            'QTabWidget::pane { background: transparent; border: none; border-radius: 28px; margin: 0px; padding: 0px; }'
            'QTabBar { qproperty-drawBase: 0; spacing: 6px; }'
            'QTabBar::tab { background: rgba(255,255,255,0.06); color: #f2f2ff; padding: 6px 12px; border: 1px solid rgba(255,255,255,0.04); border-radius: 16px; margin: 4px 6px; min-width: 100px; }'
            'QTabBar::tab:selected { background: rgba(255,255,255,0.20); color: white; border-color: rgba(255,255,255,0.18); }'
            'QTabBar::tab:hover { background: rgba(255,255,255,0.12); }'
            'QTabBar::close-button { subcontrol-position: right; subcontrol-origin: padding; margin: 0 6px; width: 14px; height: 14px; }'
            'QTabWidget::tab-bar { alignment: left; margin-left: 12px; }'
        )

        # hide the default QTabBar since we use custom wrapping buttons
        try:
            self.tab_widget.tabBar().hide()
        except Exception:
            pass

        editor_layout.addWidget(self.tabs_container)
        editor_layout.addWidget(self.tab_widget)
        self.background_layout.addWidget(self.editor_panel, 1)

        self.status_label = QLabel('')
        self.status_label.setStyleSheet('color: #b8b8c8; font-size: 12px;')
        self.status_label.hide()

        # add a QSizeGrip to allow resizing the frameless window (bottom-right)
        self.size_grip = QSizeGrip(self.background_widget)
        self.size_grip.setToolTip('Arraste para redimensionar')
        # Put the grip into a bottom row so it's anchored properly
        bottom_row = QWidget()
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.size_grip, 0, Qt.AlignRight | Qt.AlignBottom)
        # small corner handle for easier resizing on rounded corners
        self.corner_handle = QWidget(self.background_widget)
        self.corner_handle.setObjectName('corner_handle')
        self.corner_handle.setCursor(Qt.SizeFDiagCursor)
        self.corner_handle.setStyleSheet('background: rgba(255,255,255,0.04); border-radius: 8px;')
        self.corner_handle.setFixedSize(20, 20)
        # place in the bottom row aligned to the right
        bottom_layout.addWidget(self.corner_handle, 0, Qt.AlignRight | Qt.AlignBottom)
        self.background_layout.addWidget(bottom_row)

        self.central_layout.addWidget(self.background_widget)
        self.setCentralWidget(self.central_widget)

        self.opacity_value = 0.85
        self.setWindowOpacity(self.opacity_value)
        self.setMouseTracking(True)
        self.background_widget.setMouseTracking(True)
        self.central_widget.setMouseTracking(True)
        self.tab_widget.setMouseTracking(True)
        self._drag_position = None
        self._resize_direction = None
        self._resize_start_rect = None

        # no note created on startup; user opens or creates a project first
        # ensure additional widgets forward mouse events for resizing
        for w in (self.tabs_container, self.tab_widget, self.editor_panel, self.action_bar):
            try:
                w.installEventFilter(self)
                w.setMouseTracking(True)
            except Exception:
                pass

    def _button_style(self) -> str:
        return (
            'color: white; background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.15);'
            ' border-radius: 16px; padding: 10px 14px;'
        )

    def _note_style(self) -> str:
        return (
            'background: rgba(255,255,255,0.14); color: #f8f8ff; border: 1px solid rgba(255,255,255,0.20); '
            'border-radius: 32px; padding: 20px;'
        )

    def opacity_slider_changed(self, value: int):
        self.opacity_value = value / 100.0
        self.setWindowOpacity(self.opacity_value)
        self.opacity_label.setText(f'{value}%')

    def handle_minimize(self):
        # save before minimizing
        try:
            self.save_all_notes()
        except Exception:
            pass
        self.showMinimized()

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def create_project(self):
        # if there is an open project or notes, ask whether to save before creating new
        if self.tab_widget.count() > 0:
            reply = QMessageBox.question(self, 'Salvar projeto atual?', 'Deseja salvar o projeto atual antes de criar um novo?', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return
            if reply == QMessageBox.Yes:
                try:
                    self.save_all_notes()
                except Exception:
                    pass

        name, ok = QInputDialog.getText(self, 'Novo projeto', 'Nome do projeto:')
        if not ok or not name.strip():
            return

        safe_name = self.safe_filename(name.strip())
        project_path = self.app_root / safe_name
        project_path.mkdir(parents=True, exist_ok=True)

        # clear current state and set new project as clean
        self.project_path = project_path
        self.project_name = name.strip()
        self.project_meta = {'name': self.project_name, 'notes': []}
        self.project_label.setText(self.project_name)
        self._clear_tab_buttons()
        self.tab_widget.clear()
        self.notes = []

        self.save_project_meta()
        self.status_label.setText('Projeto criado')

    def rename_project(self):
        if not self.project_path:
            QMessageBox.information(self, 'Nenhum projeto', 'Abra ou crie um projeto primeiro.')
            return
        new_name, ok = QInputDialog.getText(self, 'Renomear projeto', 'Nome do projeto:', text=self.project_name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        safe_name = self.safe_filename(new_name)
        new_project_path = self.app_root / safe_name
        if new_project_path.exists() and new_project_path != self.project_path:
            QMessageBox.warning(self, 'Nome existente', 'Já existe um projeto com esse nome.')
            return
        try:
            self.project_path.rename(new_project_path)
        except Exception:
            try:
                shutil.copytree(self.project_path, new_project_path)
                shutil.rmtree(self.project_path)
            except Exception:
                QMessageBox.warning(self, 'Erro', 'Não foi possível renomear o projeto no disco.')
                return
        self.project_path = new_project_path
        self.project_name = new_name
        self.project_label.setText(self.project_name)
        self.save_project_meta()
        self.status_label.setText('Projeto renomeado')

    def delete_project(self):
        if not self.project_path:
            QMessageBox.information(self, 'Nenhum projeto', 'Abra ou crie um projeto primeiro.')
            return
        reply = QMessageBox.question(self, 'Excluir projeto', f"Excluir o projeto '{self.project_name}' e todos os arquivos?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            shutil.rmtree(self.project_path)
        except Exception:
            QMessageBox.warning(self, 'Erro', 'Não foi possível excluir o projeto.')
            return
        self.project_path = None
        self.project_name = None
        self.project_meta = {'name': '', 'notes': []}
        self.project_label.setText('Nenhum projeto')
        self._clear_tab_buttons()
        self.tab_widget.clear()
        self.notes = []
        self.status_label.setText('Projeto excluído')

    def open_project(self):
        folder = QFileDialog.getExistingDirectory(self, 'Abrir pasta de projeto')
        if folder:
            self.project_path = Path(folder)
            self.project_name = self.project_path.name
            self.project_label.setText(self.project_name)
            self.load_project()

    def load_project(self):
        self._clear_tab_buttons()
        self.tab_widget.clear()
        self.notes = []
        self.project_meta = {'name': self.project_name or '', 'notes': []}

        index_file = self.project_path / '.notes.json'
        if index_file.exists():
            try:
                self.project_meta = json.loads(index_file.read_text(encoding='utf-8'))
            except Exception:
                self.project_meta = {'name': self.project_name or '', 'notes': []}

        self.project_name = self.project_meta.get('name', self.project_path.name)
        self.project_label.setText(self.project_name)

        for note_meta in self.project_meta.get('notes', []):
            note_file = self.project_path / note_meta['fileName']
            content = note_file.read_text(encoding='utf-8') if note_file.exists() else ''
            self.add_note_tab(note_meta['name'], note_meta['fileName'], content)

        self.status_label.setText('Projeto carregado')

    def safe_filename(self, text: str) -> str:
        safe = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        return safe or 'nota'

    def create_note(self):
        default_name = f'Nota {self.tab_widget.count() + 1}'
        name, ok = QInputDialog.getText(self, 'Nova nota', 'Nome da nota:', text=default_name)
        if not ok or not name.strip():
            return
        note_name = name.strip()
        note_file = f'{self.safe_filename(note_name)}.md'
        header = f'# {note_name}\n\n'
        self.add_note_tab(note_name, note_file, header)
        self.status_label.setText(f'Criou aba: {note_name}')
        if self.project_path:
            self._create_note_file(self.notes[-1])
            self.save_project_meta()

    def add_note_tab(self, name: str, file_name: str, content: str):
        editor = QTextEdit()
        editor.setPlainText(content)
        editor.setFrameShape(QTextEdit.NoFrame)
        editor.setAttribute(Qt.WA_TranslucentBackground, True)
        editor.setStyleSheet('background: transparent; color: #f8f8ff; border: none; font-size: 14px; border-radius: 28px; padding: 16px 24px;')
        editor.setViewportMargins(24, 16, 24, 16)
        editor.viewport().setStyleSheet('background: transparent; border-radius: 28px;')
        editor.viewport().setAutoFillBackground(False)
        # auto-save when the editor content changes
        try:
            editor.textChanged.connect(lambda e=editor: self._on_editor_text_changed(e))
        except Exception:
            pass
        # wrap the editor in a styled page so the note area itself can be rounded
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)
        page.setStyleSheet(
            'background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.20); '
            'border-radius: 32px;')
        page.setAttribute(Qt.WA_StyledBackground, True)
        page.setAutoFillBackground(True)

        inner_frame = QWidget()
        inner_frame.setStyleSheet(
            'background: transparent; border-radius: 32px; padding: 20px;')
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)
        inner_layout.addWidget(editor)
        page_layout.addWidget(inner_frame)
        self.notes.append({'name': name, 'fileName': file_name, 'widget': page, 'editor': editor, 'tab_button': None})
        index = self.tab_widget.addTab(page, name)
        self.tab_widget.setCurrentWidget(page)

        note_button_style = self._button_style()
        hover_button_style = (
            'color: white; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.18); '
            'border-radius: 16px; padding: 10px 14px;'
        )

        # create a TabButton that shows actions on hover
        class TabButton(QWidget):
            def __init__(self, label: str, parent=None):
                super().__init__(parent)
                self.setCursor(Qt.PointingHandCursor)
                self.setFixedHeight(44)
                self.layout = QHBoxLayout(self)
                self.layout.setContentsMargins(16, 10, 16, 10)
                self.layout.setSpacing(10)
                # container styled like the new project button
                self.setStyleSheet(note_button_style)
                # ensure stylesheet background is painted
                self.setAttribute(Qt.WA_StyledBackground, True)
                self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                self.name_btn = QPushButton(label)
                self.name_btn.setCursor(Qt.PointingHandCursor)
                self.name_btn.setStyleSheet('color: #f2f2ff; background: transparent; border: none; border-radius: 16px; font-size: 13px; padding: 0px 8px;')
                # allow context menu for renaming (connected by parent when button is created)
                self.name_btn.setContextMenuPolicy(Qt.CustomContextMenu)
                self.layout.addWidget(self.name_btn)

                self.delete_btn = QPushButton('-')
                self.delete_btn.setCursor(Qt.PointingHandCursor)
                self.delete_btn.setFixedSize(22, 22)
                self.delete_btn.setToolTip('Excluir nota')
                self.delete_btn.setStyleSheet(
                    'color: #f2f2ff; background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); '
                    'border-radius: 11px; font-size: 12px; line-height: 1; padding: 0;')
                self.layout.addWidget(self.delete_btn)

                self.close_btn = QPushButton('x')
                self.close_btn.setCursor(Qt.PointingHandCursor)
                self.close_btn.setFixedSize(22, 22)
                self.close_btn.setStyleSheet(
                    'color: rgba(255,255,255,0.95); background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); '
                    'border-radius: 11px; font-weight: 700; font-size: 12px; padding: 0;')
                self.layout.addWidget(self.close_btn)

            def enterEvent(self, e):
                self.setStyleSheet(hover_button_style)
                self.close_btn.setStyleSheet(
                    'color: white; background: rgba(255,255,255,0.20); border: 1px solid rgba(255,255,255,0.16); '
                    'border-radius: 9px; font-weight: 700; font-size: 12px; padding: 0;')
                self.delete_btn.setStyleSheet(
                    'color: #f2f2ff; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.16); '
                    'border-radius: 9px; font-size: 12px; line-height: 1; padding: 0;')
                return super().enterEvent(e)

            def leaveEvent(self, e):
                self.setStyleSheet(note_button_style)
                self.close_btn.setStyleSheet(
                    'color: rgba(255,255,255,0.95); background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); '
                    'border-radius: 9px; font-weight: 700; font-size: 12px; padding: 0;')
                self.delete_btn.setStyleSheet(
                    'color: #f2f2ff; background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); '
                    'border-radius: 9px; font-size: 12px; line-height: 1; padding: 0;')
                return super().leaveEvent(e)

                # initial visibility: both visible but minimalistic
                self.close_btn.show()
                self.delete_btn.show()

            def enterEvent(self, e):
                self.close_btn.setStyleSheet(
                    'color: white; background: rgba(255,255,255,0.20); border: 1px solid rgba(255,255,255,0.16); '
                    'border-radius: 9px; font-weight: 700; font-size: 12px; padding: 0;')
                self.delete_btn.setStyleSheet(
                    'color: #f2f2ff; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.16); '
                    'border-radius: 9px; font-size: 12px; line-height: 1; padding: 0;')
                return super().enterEvent(e)

            def leaveEvent(self, e):
                self.close_btn.setStyleSheet(
                    'color: rgba(255,255,255,0.95); background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.14); '
                    'border-radius: 9px; font-weight: 700; font-size: 12px; padding: 0;')
                self.delete_btn.setStyleSheet(
                    'color: #f2f2ff; background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.14); '
                    'border-radius: 9px; font-size: 12px; line-height: 1; padding: 0;')
                return super().leaveEvent(e)

        btn = TabButton(name, parent=self.tabs_container)
        # attach reference for context callbacks and connect context menu to renaming
        btn._parent_ref = self
        btn.name_btn.customContextMenuRequested.connect(lambda pos, w=editor, b=btn: self._show_note_context_menu(w, pos, b))
        # wire actions
        btn.name_btn.clicked.connect(lambda _, w=editor: self.tab_widget.setCurrentWidget(w))
        btn.name_btn.mouseDoubleClickEvent = lambda event, w=editor: self._rename_note_by_widget(w)
        btn.delete_btn.clicked.connect(lambda _, w=editor: self._delete_note_by_widget(w))
        btn.close_btn.clicked.connect(lambda _, w=editor: self._close_note_by_widget(w))

        # add to manual buttons list and parent into tabs_container
        btn.setParent(self.tabs_container)
        btn.show()
        btn.raise_()
        self._tab_buttons.append(btn)
        # save reference to tab button
        self.notes[-1]['tab_button'] = btn
        self._reflow_tabs()

    def current_note_index(self):
        return self.tab_widget.currentIndex()

    def current_note(self):
        idx = self.current_note_index()
        return self.notes[idx] if 0 <= idx < len(self.notes) else None

    def eventFilter(self, watched, event):
        watched_resize_targets = []
        for name in ('top_bar','background_widget','central_widget','tabs_container','tab_widget','editor_panel','action_bar','corner_handle'):
            if hasattr(self, name):
                watched_resize_targets.append(getattr(self, name))
        # special-case the corner handle to force bottom-right resize behavior
        try:
            if hasattr(self, 'corner_handle') and watched is self.corner_handle:
                if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                    # start a bottom-right resize
                    self._resize_direction = 'bottom-right'
                    self._resize_start_rect = self.geometry()
                    return True
                if event.type() == QEvent.MouseMove and (event.buttons() & Qt.LeftButton):
                    # perform resize using global position
                    try:
                        self._resize_window(event.globalPosition().toPoint())
                    except Exception:
                        pass
                    return True
                if event.type() == QEvent.MouseButtonRelease:
                    self._resize_direction = None
                    self._resize_start_rect = None
                    return True
        except Exception:
            pass

        if watched in tuple(watched_resize_targets):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.mousePressEvent(event)
            elif event.type() == QEvent.MouseMove:
                self.mouseMoveEvent(event)
            elif event.type() == QEvent.MouseButtonRelease:
                self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def _clear_tab_buttons(self):
        for btn in list(self._tab_buttons):
            try:
                btn.setParent(None)
                btn.deleteLater()
            except Exception:
                pass
        self._tab_buttons = []

    def _create_note_file(self, note):
        if not self.project_path:
            return
        self.project_path.mkdir(parents=True, exist_ok=True)
        content = note['widget'].toPlainText()
        note_file = self.project_path / note['fileName']
        note_file.write_text(content, encoding='utf-8')

    def _on_editor_text_changed(self, editor_widget):
        # find associated note and auto-save its content immediately when possible
        try:
            note = next((n for n in self.notes if n.get('editor') is editor_widget), None)
            if note is None:
                return
            if not self.project_path:
                # nothing to auto-save to yet
                return
            # write the file for this note
            self.project_path.mkdir(parents=True, exist_ok=True)
            file_path = self.project_path / note['fileName']
            file_path.write_text(editor_widget.toPlainText(), encoding='utf-8')
            # update metadata timestamp/status
            self.status_label.setText(f"Auto-salvou: {note['name']}")
        except Exception:
            pass

    def rename_note(self, index: int):
        if index < 0 or index >= len(self.notes):
            return
        note = self.notes[index]
        new_name, ok = QInputDialog.getText(self, 'Renomear nota', 'Nome da nota:', text=note['name'])
        if ok and new_name.strip():
            note['name'] = new_name.strip()
            self.tab_widget.setTabText(index, note['name'])
            self.status_label.setText(f'Nota renomeada: {note["name"]}')
            self.save_project_meta()

    def close_note_tab(self, index: int):
        if index < 0 or index >= len(self.notes):
            return
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        # remove associated tab button if present
        for note in list(self.notes):
            if note['widget'] is widget:
                btn = note.get('tab_button')
                if btn is not None:
                    try:
                        if btn in self._tab_buttons:
                            self._tab_buttons.remove(btn)
                    except Exception:
                        pass
                    btn.setParent(None)
                    btn.deleteLater()
                self.notes.remove(note)
                break
        # select previous tab if possible
        try:
            if self.tab_widget.count() > 0:
                new_index = min(index, self.tab_widget.count() - 1)
                if new_index >= 0:
                    self.tab_widget.setCurrentIndex(new_index)
        except Exception:
            pass

        # reflow tab buttons to remove gaps and update UI
        try:
            self._reflow_tabs()
        except Exception:
            pass

        self.status_label.setText('Nota fechada')

        self.save_project_meta()

    def _close_note_by_widget(self, widget):
        note = next((n for n in self.notes if n.get('editor') is widget or n['widget'] is widget), None)
        if note is None:
            return
        idx = self.tab_widget.indexOf(note['widget'])
        if idx != -1:
            self.close_note_tab(idx)

    def _delete_note_by_widget(self, widget):
        # confirm deletion
        note = next((n for n in self.notes if n.get('editor') is widget or n['widget'] is widget), None)
        if note is None:
            return
        idx = self.tab_widget.indexOf(note['widget'])
        if idx == -1:
            return
        if note is None:
            return
        reply = QMessageBox.question(self, 'Excluir nota', f"Excluir nota '{note['name']}' permanentemente?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        # delete file if exists
        try:
            if self.project_path:
                file_path = self.project_path / note['fileName']
                if file_path.exists():
                    file_path.unlink()
        except Exception:
            pass
        # now close tab and remove button
        self._close_note_by_widget(widget)
        self.save_project_meta()

    def _reflow_tabs(self):
        # lay out buttons left-to-right and wrap to next line when needed
        padding = 8
        spacing = 8
        x = padding
        y = padding
        max_w = self.tabs_container.width() or self.width()
        row_height = 0
        for btn in self._tab_buttons:
            btn.adjustSize()
            bw = btn.width()
            bh = btn.height()
            if x + bw + padding > max_w and row_height > 0:
                x = padding
                y += row_height + spacing
                row_height = 0
            btn.move(x, y)
            btn.raise_()
            x += bw + spacing
            row_height = max(row_height, bh)
        total_h = y + row_height + padding
        if total_h != self.tabs_container.height():
            self.tabs_container.setMinimumHeight(total_h)
        # ensure container repaints so styles become visible
        try:
            self.tabs_container.update()
        except Exception:
            pass

    def _show_note_context_menu(self, widget, pos, tab_button=None):
        try:
            menu = QMenu(self)
            rename_action = menu.addAction('Renomear')
            # show menu at the button location if provided
            global_pos = tab_button.name_btn.mapToGlobal(pos) if tab_button is not None else self.mapToGlobal(pos)
            action = menu.exec_(global_pos)
            if action == rename_action:
                self._rename_note_by_widget(widget)
        except Exception:
            pass

    def _rename_note_by_widget(self, widget):
        # find the note
        note = next((n for n in self.notes if n['widget'] is widget), None)
        if note is None:
            return
        new_name, ok = QInputDialog.getText(self, 'Renomear nota', 'Nome da nota:', text=note['name'])
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        old_file = note.get('fileName')
        new_file = f"{self.safe_filename(new_name)}.md"
        # attempt to rename file on disk if project exists
        try:
            if self.project_path:
                old_path = self.project_path / old_file
                new_path = self.project_path / new_file
                if old_path.exists():
                    # if new_path exists, overwrite
                    try:
                        old_path.rename(new_path)
                    except Exception:
                        # fallback: write new file and remove old
                        new_path.write_text(old_path.read_text(encoding='utf-8'), encoding='utf-8')
                        try:
                            old_path.unlink()
                        except Exception:
                            pass
                # update file content to current editor text
                new_path.write_text(widget.toPlainText(), encoding='utf-8')
                note['fileName'] = new_file
        except Exception:
            pass
        # update in-memory name and UI
        note['name'] = new_name
        if note.get('tab_button') is not None:
            try:
                note['tab_button'].name_btn.setText(new_name)
            except Exception:
                pass
        idx = self.tab_widget.indexOf(widget)
        if idx != -1:
            try:
                self.tab_widget.setTabText(idx, new_name)
            except Exception:
                pass
        self.save_project_meta()
        self.status_label.setText(f'Nota renomeada: {new_name}')

    def save_project_meta(self):
        if not self.project_path:
            return
        self.project_meta['name'] = self.project_name or self.project_path.name
        self.project_meta['notes'] = [
            {
                'name': note['name'],
                'fileName': note['fileName'],
            }
            for note in self.notes
        ]
        self.project_path.mkdir(parents=True, exist_ok=True)
        meta_file = self.project_path / '.notes.json'
        meta_file.write_text(json.dumps(self.project_meta, indent=2, ensure_ascii=False), encoding='utf-8')

    def save_all_notes(self):
        if self.tab_widget.count() == 0:
            self.status_label.setText('Nenhuma nota para salvar')
            return
        if not self.project_path:
            # ask user to create a project in app root
            name, ok = QInputDialog.getText(self, 'Salvar projeto', 'Nome do novo projeto:')
            if not ok or not name.strip():
                self.status_label.setText('Salvar cancelado')
                return
            safe_name = self.safe_filename(name.strip())
            self.project_path = self.app_root / safe_name
            self.project_path.mkdir(parents=True, exist_ok=True)
            self.project_name = name.strip()
            self.project_label.setText(self.project_name)

        self.project_path.mkdir(parents=True, exist_ok=True)

        for note in self.notes:
            content = note['widget'].toPlainText()
            note_file = self.project_path / note['fileName']
            note_file.write_text(content, encoding='utf-8')

        self.save_project_meta()
        self.status_label.setText('Todas as notas foram salvas')
        try:
            QMessageBox.information(self, 'Salvo', 'Todas as notas foram salvas com sucesso.')
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # reflow tab buttons when window changes size
        try:
            self._reflow_tabs()
        except Exception:
            pass
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._resize_direction = self._get_resize_direction(event.pos())
            self._resize_start_rect = self.geometry()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        direction = self._get_resize_direction(event.pos())
        if event.buttons() & Qt.LeftButton:
            if self._resize_direction:
                self._resize_window(event.globalPosition().toPoint())
            elif self._drag_position:
                self.move(event.globalPosition().toPoint() - self._drag_position)
        else:
            cursor = Qt.ArrowCursor
            if direction in ('left', 'right'):
                cursor = Qt.SizeHorCursor
            elif direction in ('top', 'bottom'):
                cursor = Qt.SizeVerCursor
            elif direction in ('top-left', 'bottom-right'):
                cursor = Qt.SizeFDiagCursor
            elif direction in ('top-right', 'bottom-left'):
                cursor = Qt.SizeBDiagCursor
            self.setCursor(cursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        self._resize_direction = None
        self._resize_start_rect = None
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def _get_resize_direction(self, pos):
        margin = 12
        rect = self.rect()
        left = pos.x() <= margin
        right = pos.x() >= rect.width() - margin
        top = pos.y() <= margin
        bottom = pos.y() >= rect.height() - margin

        if top and left:
            return 'top-left'
        if top and right:
            return 'top-right'
        if bottom and left:
            return 'bottom-left'
        if bottom and right:
            return 'bottom-right'
        if left:
            return 'left'
        if right:
            return 'right'
        if top:
            return 'top'
        if bottom:
            return 'bottom'
        return None

    def _resize_window(self, global_pos):
        if not self._resize_start_rect or not self._resize_direction:
            return

        rect = self._resize_start_rect
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        min_w, min_h = 420, 300
        new_x, new_y = x, y
        new_w, new_h = w, h

        if self._resize_direction in ('left', 'top-left', 'bottom-left'):
            new_x = global_pos.x()
            new_w = x + w - new_x
            if new_w < min_w:
                new_x = x + w - min_w
                new_w = min_w
        if self._resize_direction in ('right', 'top-right', 'bottom-right'):
            new_w = max(min_w, global_pos.x() - x)
        if self._resize_direction in ('top', 'top-left', 'top-right'):
            new_y = global_pos.y()
            new_h = y + h - new_y
            if new_h < min_h:
                new_y = y + h - min_h
                new_h = min_h
        if self._resize_direction in ('bottom', 'bottom-left', 'bottom-right'):
            new_h = max(min_h, global_pos.y() - y)

        self.setGeometry(new_x, new_y, new_w, new_h)

    def closeEvent(self, event):
        if self.tab_widget.count() > 0:
            reply = QMessageBox.question(self, 'Salvar antes de sair', 'Deseja salvar todas as notas antes de fechar?', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.Yes:
                try:
                    self.save_all_notes()
                except Exception:
                    pass
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentNotesApp()
    window.show()
    sys.exit(app.exec())
