import json
import re
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QEvent, QPoint, QRect
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QKeySequence, QShortcut
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
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


APP_VERSION = "v1.0.0"

TRANSLATIONS = {
    'pt': {
        'project_menu': 'Projeto  ▾',
        'new_project': 'Novo projeto',
        'open_project': 'Abrir projeto',
        'rename_project': 'Renomear projeto',
        'delete_project': 'Excluir projeto',
        'save_all': 'Salvar tudo',
        'new_note_tooltip': 'Criar nova nota',
        'default_note_name': 'Nota',
        'default_project_name': 'Geral',
        'no_project': 'Nenhum projeto',
        'saved': 'Salvo',
        'confirm': 'Confirmar',
        'cancel': 'Cancelar',
        'save': 'Salvar',
        'discard': 'Não salvar',
        'exit_title': 'Sair',
        'exit_msg': 'Deseja salvar as notas antes de fechar?',
        'delete_note_title': 'Excluir nota',
        'delete_note_msg': "Excluir a nota '{name}' permanentemente?",
        'delete_project_title': 'Excluir projeto',
        'delete_project_msg': "Excluir o projeto '{name}' e todos os arquivos permanentemente?",
        'new_project_title': 'Novo projeto',
        'rename_project_title': 'Renomear projeto',
        'new_note_title': 'Nova nota',
        'rename_note_title': 'Renomear nota',
        'project_name_prompt': 'Nome do projeto:',
        'note_name_prompt': 'Nome da nota:',
        'save_project_prompt': 'Salvar projeto',
        'new_project_prompt': 'Nome do novo projeto:',
    },
    'en': {
        'project_menu': 'Project  ▾',
        'new_project': 'New project',
        'open_project': 'Open project',
        'rename_project': 'Rename project',
        'delete_project': 'Delete project',
        'save_all': 'Save all',
        'new_note_tooltip': 'Create new note',
        'default_note_name': 'Note',
        'default_project_name': 'General',
        'no_project': 'No project',
        'saved': 'Saved',
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'save': 'Save',
        'discard': "Don't save",
        'exit_title': 'Exit',
        'exit_msg': 'Do you want to save notes before exiting?',
        'delete_note_title': 'Delete Note',
        'delete_note_msg': "Delete note '{name}' permanently?",
        'delete_project_title': 'Delete Project',
        'delete_project_msg': "Delete project '{name}' and all files permanently?",
        'new_project_title': 'New Project',
        'rename_project_title': 'Rename Project',
        'new_note_title': 'New Note',
        'rename_note_title': 'Rename Note',
        'project_name_prompt': 'Project name:',
        'note_name_prompt': 'Note name:',
        'save_project_prompt': 'Save project',
        'new_project_prompt': 'New project name:',
    }
}


class LucideIcons:
    """Ícones vetoriais modernos Lucide (100% brancos, traçado limpo de 2px, High-DPI)."""
    
    @staticmethod
    def _svg_to_icon(svg_str: str, size: int = 20) -> QIcon:
        renderer = QSvgRenderer(svg_str.encode('utf-8'))
        pixmap = QPixmap(size * 2, size * 2)  # High-DPI supersampling
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    @classmethod
    def floppy(cls, size=18) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
            '<polyline points="17 21 17 13 7 13 7 21"/>'
            '<polyline points="7 3 7 8 15 8"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)

    @classmethod
    def plus(cls, size=16) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<line x1="12" y1="5" x2="12" y2="19"/>'
            '<line x1="5" y1="12" x2="19" y2="12"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)

    @classmethod
    def folder_open(cls, size=16) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)

    @classmethod
    def file_plus(cls, size=16) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<polyline points="14 2 14 8 20 8"/>'
            '<line x1="12" y1="18" x2="12" y2="12"/>'
            '<line x1="9" y1="15" x2="15" y2="15"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)

    @classmethod
    def edit(cls, size=16) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 20h9"/>'
            '<path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)

    @classmethod
    def trash(cls, size=16) -> QIcon:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            'stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="3 6 5 6 21 6"/>'
            '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
            '<line x1="10" y1="11" x2="10" y2="17"/>'
            '<line x1="14" y1="11" x2="14" y2="17"/>'
            '</svg>'
        )
        return cls._svg_to_icon(svg, size)


class StyledDialog(QDialog):
    """Diálogo customizado moderno."""
    # mode: 'input' | 'confirm' | 'save_close' | 'info'
    def __init__(self, parent=None, title='', message='', mode='input', default_text=''):
        super().__init__(parent)
        self.result_text = ''
        self.confirmed = False
        self.choice = None          # usado pelo modo save_close: 'save' | 'discard' | 'cancel'
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(400)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setObjectName('dlg_card')
        card.setStyleSheet(
            '#dlg_card { background: rgba(22,26,40,0.97); border: 1px solid rgba(255,255,255,0.18); '
            'border-radius: 20px; }'
        )
        card.setAttribute(Qt.WA_StyledBackground, True)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(16)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet('color: #ffffff; font-size: 15px; font-weight: 700; background: transparent;')
        card_layout.addWidget(title_lbl)

        if message:
            msg_lbl = QLabel(message)
            msg_lbl.setStyleSheet('color: #c8c8d8; font-size: 13px; background: transparent;')
            msg_lbl.setWordWrap(True)
            card_layout.addWidget(msg_lbl)

        self._input = None
        if mode == 'input':
            self._input = QLineEdit()
            self._input.setText(default_text)
            self._input.selectAll()
            self._input.setStyleSheet(
                'background: rgba(255,255,255,0.10); color: #f0f0ff; border: 1px solid rgba(255,255,255,0.20); '
                'border-radius: 10px; padding: 10px 14px; font-size: 13px;'
            )
            self._input.returnPressed.connect(self._accept)
            card_layout.addWidget(self._input)

        _btn_base = 'border-radius: 12px; padding: 9px 22px; font-size: 13px; font-weight: 600; border: none;'
        _ghost = _btn_base + 'background: rgba(255,255,255,0.09); color: #c8c8d8;'
        _primary = _btn_base + 'background: rgba(255,255,255,0.18); color: #ffffff;'

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        if mode == 'save_close':
            # Cancelar — não faz nada, mantém app aberto
            cancel_btn = QPushButton('Cancelar')
            cancel_btn.setStyleSheet(_ghost)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(lambda: self._set_choice('cancel'))
            btn_row.addWidget(cancel_btn)
            # Não salvar — fecha sem salvar
            discard_btn = QPushButton('Não salvar')
            discard_btn.setStyleSheet(_ghost)
            discard_btn.setCursor(Qt.PointingHandCursor)
            discard_btn.clicked.connect(lambda: self._set_choice('discard'))
            btn_row.addWidget(discard_btn)
            # Salvar — salva e fecha
            save_btn = QPushButton('Salvar')
            save_btn.setStyleSheet(_primary)
            save_btn.setCursor(Qt.PointingHandCursor)
            save_btn.clicked.connect(lambda: self._set_choice('save'))
            btn_row.addWidget(save_btn)

        elif mode in ('input', 'confirm'):
            cancel_btn = QPushButton('Cancelar')
            cancel_btn.setStyleSheet(_ghost)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(self.reject)
            btn_row.addWidget(cancel_btn)

            ok_label = 'OK' if mode == 'input' else 'Confirmar'
            ok_btn = QPushButton(ok_label)
            ok_btn.setStyleSheet(_primary)
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.clicked.connect(self._accept)
            btn_row.addWidget(ok_btn)

        else:  # info
            ok_btn = QPushButton('OK')
            ok_btn.setStyleSheet(_primary)
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.clicked.connect(self._accept)
            btn_row.addWidget(ok_btn)

        card_layout.addLayout(btn_row)
        outer.addWidget(card)

    def _set_choice(self, choice):
        self.choice = choice
        self.accept()

    def _accept(self):
        if self._input is not None:
            self.result_text = self._input.text()
        self.confirmed = True
        self.accept()

    @staticmethod
    def get_text(parent, title, message='', default=''):
        dlg = StyledDialog(parent, title=title, message=message, mode='input', default_text=default)
        dlg.exec()
        return dlg.result_text, dlg.confirmed

    @staticmethod
    def ask_confirm(parent, title, message=''):
        dlg = StyledDialog(parent, title=title, message=message, mode='confirm')
        dlg.exec()
        return dlg.confirmed

    @staticmethod
    def ask_save_close(parent, title, message=''):
        """Retorna: 'save' | 'discard' | 'cancel'"""
        dlg = StyledDialog(parent, title=title, message=message, mode='save_close')
        dlg.exec()
        return dlg.choice or 'cancel'

    @staticmethod
    def show_info(parent, title, message=''):
        dlg = StyledDialog(parent, title=title, message=message, mode='info')
        dlg.exec()


class TransparentNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_lang = 'pt'
        self.project_path = None
        self.project_name = None
        self.notes = []
        self.project_meta = {'name': '', 'notes': []}
        self.app_root = Path(__file__).parent / "Projetos"
        self.app_root.mkdir(parents=True, exist_ok=True)
        self.settings_file = Path(__file__).parent / ".settings.json"
        self.load_settings()

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

        self.version_label = QLabel(APP_VERSION)
        self.version_label.setStyleSheet('color: rgba(255,255,255,0.45); font-size: 11px; font-weight: 500; margin-left: 2px;')
        title_layout.addWidget(self.version_label)

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

        # Botão de alternar idioma (PT / EN)
        self.lang_button = QPushButton(f'🌐 {self.current_lang.upper()}')
        self.lang_button.setToolTip('Alternar idioma / Switch language')
        self.lang_button.setFixedSize(62, 28)
        self.lang_button.setStyleSheet(
            'color: white; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14); '
            'border-radius: 14px; font-size: 11px; font-weight: 600;'
        )
        self.lang_button.setCursor(Qt.PointingHandCursor)
        self.lang_button.clicked.connect(self.toggle_language)
        title_layout.addWidget(self.lang_button)

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

        # Botão '+' ao lado das abas para criar nota automaticamente
        self.add_note_btn = QPushButton(self.tabs_container)
        self.add_note_btn.setIcon(LucideIcons.plus(14))
        self.add_note_btn.setIconSize(QSize(14, 14))
        self.add_note_btn.setToolTip('Criar nova nota')
        self.add_note_btn.setFixedSize(32, 32)
        self.add_note_btn.setCursor(Qt.PointingHandCursor)
        self.add_note_btn.setStyleSheet(
            'QPushButton { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); '
            'border-radius: 16px; } '
            'QPushButton:hover { background: rgba(255,255,255,0.24); border-color: rgba(255,255,255,0.35); }'
        )
        self.add_note_btn.clicked.connect(self.create_note_auto)

        # --- Botão "Projeto ▾" com menu cascata ---
        self.project_menu_btn = QPushButton(self.tr('project_menu'))
        self.project_menu_btn.setStyleSheet(self._button_style())
        self.project_menu_btn.setCursor(Qt.PointingHandCursor)

        self.project_menu = QMenu(self)
        self.project_menu.setStyleSheet(
            'QMenu { background: rgba(22,26,40,0.97); border: 1px solid rgba(255,255,255,0.18); '
            'border-radius: 14px; padding: 6px; color: #ffffff; font-size: 13px; }'
            'QMenu::item { padding: 10px 20px 10px 14px; border-radius: 10px; }'
            'QMenu::item:selected { background: rgba(255,255,255,0.12); }'
            'QMenu::separator { height: 1px; background: rgba(255,255,255,0.12); margin: 4px 10px; }'
        )
        self.act_new_proj = self.project_menu.addAction(LucideIcons.file_plus(16), self.tr('new_project'), self.create_project)
        self.act_open_proj = self.project_menu.addAction(LucideIcons.folder_open(16), self.tr('open_project'), self.open_project)
        self.project_menu.addSeparator()
        self.act_rename_proj = self.project_menu.addAction(LucideIcons.edit(16), self.tr('rename_project'), self.rename_project)
        self.act_delete_proj = self.project_menu.addAction(LucideIcons.trash(16), self.tr('delete_project'), self.delete_project)

        self.project_menu_btn.clicked.connect(
            lambda: self.project_menu.exec(
                self.project_menu_btn.mapToGlobal(
                    self.project_menu_btn.rect().bottomLeft()
                )
            )
        )
        action_layout.addWidget(self.project_menu_btn)

        # --- Salvar tudo (Ícone vetorial Lucide 100% branco) ---
        self.save_button = QPushButton()
        self.save_button.setIcon(LucideIcons.floppy(18))
        self.save_button.setIconSize(QSize(18, 18))
        self.save_button.setToolTip('Salvar tudo')
        self.save_button.setFixedSize(36, 36)
        self.save_button.clicked.connect(self.save_all_notes)
        self.save_button.setStyleSheet(
            'QPushButton { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.16); '
            'border-radius: 18px; } '
            'QPushButton:hover { background: rgba(255,255,255,0.22); border-color: rgba(255,255,255,0.30); }'
        )
        self.save_button.setCursor(Qt.PointingHandCursor)
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

        # ensure additional widgets forward mouse events for resizing
        for w in (self.tabs_container, self.tab_widget, self.editor_panel, self.action_bar):
            try:
                w.installEventFilter(self)
                w.setMouseTracking(True)
            except Exception:
                pass

        # Atalhos práticos de teclado
        try:
            QShortcut(QKeySequence('Ctrl+N'), self, self.create_note_auto)
            QShortcut(QKeySequence('Ctrl+S'), self, self.save_all_notes)
            QShortcut(QKeySequence('Ctrl+W'), self, lambda: self.close_note_tab(self.current_note_index()))
        except Exception:
            pass

        # Auto-carrega o projeto mais recente ou garante projeto ativo na inicialização
        try:
            self._init_startup_project()
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

    def tr(self, key: str, **kwargs) -> str:
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS['pt'])
        text = lang_dict.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'pt' else 'pt'
        self.lang_button.setText(f'🌐 {self.current_lang.upper()}')
        self.update_ui_language()
        self.save_settings()

    def update_ui_language(self):
        self.project_menu_btn.setText(self.tr('project_menu'))
        self.act_new_proj.setText(self.tr('new_project'))
        self.act_open_proj.setText(self.tr('open_project'))
        self.act_rename_proj.setText(self.tr('rename_project'))
        self.act_delete_proj.setText(self.tr('delete_project'))
        self.save_button.setToolTip(self.tr('save_all'))
        self.add_note_btn.setToolTip(self.tr('new_note_tooltip'))
        if not self.project_name or self.project_name in ('Nenhum projeto', 'No project'):
            self.project_label.setText(self.tr('no_project'))

    def load_settings(self):
        if self.settings_file.exists():
            try:
                data = json.loads(self.settings_file.read_text(encoding='utf-8'))
                self.current_lang = data.get('lang', 'pt')
            except Exception:
                self.current_lang = 'pt'

    def save_settings(self):
        try:
            data = {'lang': self.current_lang}
            self.settings_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception:
            pass

    def create_project(self):
        if self.tab_widget.count() > 0:
            if StyledDialog.ask_confirm(self, self.tr('save_project_prompt'), self.tr('exit_msg')):
                try:
                    self.save_all_notes()
                except Exception:
                    pass

        name, ok = StyledDialog.get_text(self, self.tr('new_project_title'), self.tr('project_name_prompt'))
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
            return
        new_name, ok = StyledDialog.get_text(self, self.tr('rename_project_title'), self.tr('project_name_prompt'), default=self.project_name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        safe_name = self.safe_filename(new_name)
        new_project_path = self.app_root / safe_name
        if new_project_path.exists() and new_project_path != self.project_path:
            return
        try:
            self.project_path.rename(new_project_path)
        except Exception:
            try:
                shutil.copytree(self.project_path, new_project_path)
                shutil.rmtree(self.project_path)
            except Exception:
                return
        self.project_path = new_project_path
        self.project_name = new_name
        self.project_label.setText(self.project_name)
        self.save_project_meta()
        self.status_label.setText(self.tr('saved'))

    def delete_project(self):
        if not self.project_path:
            return
        if not StyledDialog.ask_confirm(self, self.tr('delete_project_title'), self.tr('delete_project_msg', name=self.project_name)):
            return
        try:
            shutil.rmtree(self.project_path)
        except Exception:
            return
        self.project_path = None
        self.project_name = None
        self.project_meta = {'name': '', 'notes': []}
        self.project_label.setText(self.tr('no_project'))
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

    def ensure_project(self):
        """Garante que existe um projeto ativo. Se nenhum estiver aberto, usa 'Geral'."""
        if not self.project_path:
            self.project_path = self.app_root / 'Geral'
            self.project_name = 'Geral'
            self.project_meta = {'name': 'Geral', 'notes': []}
            self.project_label.setText('Geral')
        self.project_path.mkdir(parents=True, exist_ok=True)

    def _save_note_file(self, note):
        """Salva o arquivo .md da nota no disco imediatamente."""
        self.ensure_project()
        content = note['editor'].toPlainText()
        file_path = self.project_path / note['fileName']
        file_path.write_text(content, encoding='utf-8')
        self.save_project_meta()

    def _on_editor_text_changed(self, editor_widget):
        """Auto-salva a nota sempre que o texto for alterado."""
        note = next((n for n in self.notes if n['editor'] is editor_widget), None)
        if note is None:
            return
        self._save_note_file(note)
        self.status_label.setText(f'Salvo: {note["name"]}')

    def _init_startup_project(self):
        """Ao abrir o app, carrega a pasta de projeto mais recente."""
        if not self.app_root.exists():
            self.app_root.mkdir(parents=True, exist_ok=True)
        projects = [p for p in self.app_root.iterdir() if p.is_dir()]
        if projects:
            projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            self.project_path = projects[0]
            self.project_name = self.project_path.name
            self.project_label.setText(self.project_name)
            self.load_project()
        else:
            self.ensure_project()

    def load_project(self):
        self._clear_tab_buttons()
        self.tab_widget.clear()
        self.notes = []
        self.project_meta = {'name': self.project_name or self.project_path.name, 'notes': []}

        if not self.project_path or not self.project_path.exists():
            return

        index_file = self.project_path / '.notes.json'
        if index_file.exists():
            try:
                self.project_meta = json.loads(index_file.read_text(encoding='utf-8'))
            except Exception:
                self.project_meta = {'name': self.project_path.name, 'notes': []}

        self.project_name = self.project_meta.get('name', self.project_path.name)
        self.project_label.setText(self.project_name)

        loaded_files = set()
        notes_to_load = []

        # 1. Notas dos metadados
        for note_meta in self.project_meta.get('notes', []):
            file_name = note_meta['fileName']
            note_file = self.project_path / file_name
            content = note_file.read_text(encoding='utf-8') if note_file.exists() else ''
            notes_to_load.append((note_meta['name'], file_name, content))
            loaded_files.add(file_name)

        # 2. Varre arquivos .md no diretório como fallback para garantir que nada se perca
        for md_file in sorted(self.project_path.glob("*.md")):
            if md_file.name not in loaded_files:
                name = md_file.stem.replace('-', ' ').title()
                content = md_file.read_text(encoding='utf-8')
                notes_to_load.append((name, md_file.name, content))
                loaded_files.add(md_file.name)

        # 3. Carrega as abas no app
        for name, file_name, content in notes_to_load:
            self.add_note_tab(name, file_name, content)

        self.save_project_meta()
        self.status_label.setText(f'Projeto "{self.project_name}" carregado ({len(self.notes)} notas)')

    def safe_filename(self, text: str) -> str:
        safe = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        return safe or 'nota'

    def create_note_auto(self):
        """Cria uma nova nota automaticamente sem abrir dialog e salva no disco na hora."""
        self.ensure_project()
        existing_names = {note['name'] for note in self.notes}
        count = len(self.notes) + 1
        while f'Nota {count}' in existing_names:
            count += 1
        note_name = f'Nota {count}'
        note_file = f'{self.safe_filename(note_name)}.md'
        header = f'# {note_name}\n\n'
        self.add_note_tab(note_name, note_file, header)
        self._save_note_file(self.notes[-1])
        self.status_label.setText(f'Criou nota: {note_name}')

    def create_note(self):
        default_name = f'Nota {self.tab_widget.count() + 1}'
        name, ok = StyledDialog.get_text(self, 'Nova nota', 'Nome da nota:', default=default_name)
        if not ok or not name.strip():
            return
        note_name = name.strip()
        note_file = f'{self.safe_filename(note_name)}.md'
        header = f'# {note_name}\n\n'
        self.add_note_tab(note_name, note_file, header)
        self._save_note_file(self.notes[-1])
        self.status_label.setText(f'Criou nota: {note_name}')

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
        btn.name_btn.clicked.connect(lambda _, w=page: self.tab_widget.setCurrentWidget(w))
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
        if not StyledDialog.ask_confirm(self, 'Excluir nota', f"Excluir a nota '{note['name']}' permanentemente?"):
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

        # Posiciona o botão '+' ao lado da última nota
        add_w = 32
        add_h = 32
        if row_height == 0:
            row_height = 36
        if x + add_w + padding > max_w:
            x = padding
            y += row_height + spacing
            row_height = add_h

        btn_y = y + max(0, (row_height - add_h) // 2)
        self.add_note_btn.move(x, btn_y)
        self.add_note_btn.raise_()
        self.add_note_btn.show()

        total_h = y + max(row_height, add_h) + padding
        if total_h != self.tabs_container.height():
            self.tabs_container.setMinimumHeight(total_h)
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
        new_name, ok = StyledDialog.get_text(self, 'Renomear nota', 'Nome da nota:', default=note['name'])
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
            name, ok = StyledDialog.get_text(self, 'Salvar projeto', 'Nome do novo projeto:')
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
            StyledDialog.show_info(self, 'Salvo ✓', 'Todas as notas foram salvas com sucesso.')
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
            choice = StyledDialog.ask_save_close(
                self, self.tr('exit_title'), self.tr('exit_msg')
            )
            if choice == 'cancel':
                event.ignore()
                return
            if choice == 'save':
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
