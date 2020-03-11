import base64
import sys
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QTextEdit, QPushButton, QSpinBox, \
    QHBoxLayout, QLabel, QSizePolicy, QErrorMessage, QVBoxLayout, QGroupBox, QGridLayout

import shamir


def make_readonly(text_field):
    noneditable_palette = text_field.palette()
    color = noneditable_palette.color(QPalette.Window)
    noneditable_palette.setColor(QPalette.Base, color)
    noneditable_palette.setColor(QPalette.WindowText, Qt.black)
    text_field.setReadOnly(True)
    text_field.setPalette(noneditable_palette)


def int_to_b64(i: int):
    i_as_bytes = i.to_bytes((i.bit_length() + 7) // 8, 'big')
    encoded_i = base64.b64encode(i_as_bytes)
    return encoded_i


def b64_to_int(b: bytes):
    raw_bytes = base64.b64decode(b)
    decoded_integer = int.from_bytes(raw_bytes, 'big')
    return decoded_integer


class Splitter(QWidget):
    def __init__(self, field_order):
        super().__init__()

        self.field_order = field_order

        self.edit_secret = QLineEdit(self)
        self.edit_n = QSpinBox(self)
        self.edit_k = QSpinBox(self)
        self.edit_shares = QTextEdit(self)

        self.edit_k.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_n.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.edit_n.setRange(1, 100)
        self.edit_k.setRange(1, 100)
        self.edit_n.setValue(5)
        self.edit_k.setValue(2)

        button = QPushButton('podziel sekret')
        button.clicked.connect(self.calc_shares)

        make_readonly(self.edit_shares)

        self.edit_secret.setPlaceholderText('wprowadź sekret')

        grid = QGridLayout(self)
        grid.addWidget(QLabel('sekret'), 0, 0)
        grid.addWidget(self.edit_secret, 0, 1)
        grid.addWidget(QLabel('całkowita liczba\nfragmentów'), 1, 0)
        grid.addWidget(self.edit_n, 1, 1)
        grid.addWidget(QLabel('minimalna liczba\nfragmentów'), 2, 0)
        grid.addWidget(self.edit_k, 2, 1)
        grid.addWidget(button, 3, 1)
        grid.addWidget(QLabel('wygenerowane\nfragmenty'), 4, 0)
        grid.addWidget(self.edit_shares, 4, 1)
        self.setLayout(grid)

    def reset(self):
        self.edit_secret.setText('')
        self.edit_shares.setText('')

    @staticmethod
    def shares_to_string(shares: List[shamir.Point]) -> str:
        shares_string = ''
        for x, y in shares:
            shares_string += '{}---{}\n'.format(hex(x), int_to_b64(y).decode())
            shares_string += '\n'
        return shares_string

    def calc_shares(self):
        try:
            secret = self.edit_secret.text()
            n = int(self.edit_n.text())
            k = int(self.edit_k.text())
            if k > n:
                error_message = QErrorMessage(self)
                error_message.showMessage('minimalna liczba fragmentów nie może być większa niż '
                                          'całkowita liczba fragmentów')
                return

            int_secret = shamir.str_to_int(secret)
            if int_secret >= self.field_order:
                error_message = QErrorMessage(self)
                error_message.showMessage('podany sekret jest zbyt długi')
                return
            shares = shamir.encode(int_secret, k=k, n=n, p=self.field_order)
        except ValueError:
            print('wrong values')
            return

        shares_string = self.shares_to_string(shares)
        self.edit_shares.setText(shares_string)


class Combiner(QWidget):
    def __init__(self, field_order):
        super().__init__()

        self.field_order = field_order

        self.edit_secret = QLineEdit(self)
        self.edit_k = QSpinBox(self)
        self.edit_shares = QTextEdit(self)

        make_readonly(self.edit_secret)

        self.edit_k.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_k.setRange(1, 10)
        self.edit_k.setValue(2)

        self.edit_k.valueChanged.connect(self.set_edit_shares_text)
        self.set_edit_shares_text()

        button = QPushButton('odtwórz sekret')
        button.clicked.connect(self.decode_secret)

        grid = QGridLayout(self)
        grid.addWidget(QLabel('minimalna liczba\nfragmentów'), 0, 0)
        grid.addWidget(self.edit_k, 0, 1)
        grid.addWidget(QLabel('fragmenty do\npołączenia'), 1, 0)
        grid.addWidget(self.edit_shares, 1, 1)
        grid.addWidget(button, 2, 1)
        grid.addWidget(QLabel('odtworzony\nsekret'), 3, 0)
        grid.addWidget(self.edit_secret, 3, 1)
        self.setLayout(grid)

    def reset(self):
        self.edit_shares.setText('')
        self.edit_secret.setText('')

    def set_edit_shares_text(self):
        self.edit_shares.setPlaceholderText(
            'wprowadź wygenerowane wcześniej fragmenty\n'
            '(co najmniej {})'.format(self.edit_k.value()))

    @staticmethod
    def string_to_shares(text: str) -> List[shamir.Point]:
        lines = [s for s in text.splitlines() if s.strip()]
        string_pairs = [line.split('---') for line in lines]
        shares = [(int(x, 16), b64_to_int(y.encode())) for x, y in string_pairs]
        return shares

    def decode_secret(self):
        k = int(self.edit_k.text())
        try:
            shares = self.string_to_shares(self.edit_shares.toPlainText())
            supplied_shares = len(shares)
            if supplied_shares < k:
                error_message = QErrorMessage(self)
                error_message.showMessage(
                    'zbyt mało fragmentów<br>'
                    'podano: {}<br>'
                    'wymagane: co najmniej {}'.format(supplied_shares, k))
                return
            secret = shamir.decode(shares, k=k, p=self.field_order)
            self.edit_secret.setText(shamir.int_to_str(secret))
        except Exception as e:
            print('exception:')
            print(e)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.field_order = 2 ** 521 - 1

        self.splitter = Splitter(field_order=self.field_order)
        splitter_box = QGroupBox('dzielenie sekretu')
        splitter_layout = QHBoxLayout()
        splitter_layout.addWidget(self.splitter)
        splitter_box.setLayout(splitter_layout)

        self.combiner = Combiner(field_order=self.field_order)
        combiner_box = QGroupBox('odtwarzanie sekretu')
        combiner_layout = QHBoxLayout()
        combiner_layout.addWidget(self.combiner)
        combiner_box.setLayout(combiner_layout)

        clear_button = QPushButton('wyczyść wszystko')
        clear_button.clicked.connect(self.reset)
        v_box = QVBoxLayout()
        v_box.addWidget(splitter_box)
        v_box.addWidget(combiner_box)
        v_box.addWidget(clear_button, alignment=Qt.AlignHCenter)

        self.setLayout(v_box)
        self.setWindowTitle('Shamir\'s secret sharing')
        self.show()

    def reset(self):
        self.splitter.reset()
        self.combiner.reset()


if __name__ == '__main__':
    app = QApplication([])
    font = app.font()
    current_size = font.pointSize()
    new_size = int(current_size * 1.5)
    font.setPointSize(new_size)
    app.setFont(font)
    main_window = MainWindow()
    sys.exit(app.exec_())
