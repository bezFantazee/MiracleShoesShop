import sys

import psycopg2
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui

from db.config import DB
from db.import_data import *
from widgets.item_card import ItemCard


def apply_style(app):
    app.setFont(QtGui.QFont("Calibri", 10))
    with open("ui/style.qss", encoding="utf-8") as f:
        app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    apply_style(app)

    window = uic.loadUi("ui/main_window.ui")

    window.logoLabel.setPixmap(QPixmap("resources/logo.png"))

    products = [
        {
            "category": "Женская обувь",
            "name": "Кроссовки модель 1",
            "manufacture": "Meracle",
            "composition": "Натуральная кожа",
            "price": 4500.00,
            "stock": 3,
            "image": None
        },
        {
            "category": "Мужская обувь",
            "name": "Ботинки модель 2",
            "manufacture": "Meracle",
            "composition": "Кожа, текстиль",
            "price": 6200.00,
            "stock": 12,
            "image": None
        },
        {
            "category": "Мужская обувь",
            "name": "Ботинки модель 2",
            "manufacture": "Meracle",
            "composition": "Кожа, текстиль",
            "price": 6200.00,
            "stock": 12,
            "image": None
        }
    ]

    for product in products:
        card = ItemCard(product)

        window.catalogContainer.layout().addWidget(card)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
