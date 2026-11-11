from pathlib import Path

from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget


class ItemCard(QWidget):

    def __init__(self, product, parent=None):
        super().__init__(parent)

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "item_card.ui"

        uic.loadUi(str(ui_path), self)

        self.product = product
        self.load_item_data()


    def load_item_data(self):
        self.manufacturAndNameLabel.setText(f"{self.product["name"]} | {self.product["manufacture"]}")
        self.categoryLabel.setText(self.product["category"])
        self.countLabel.setText("Много" if self.product["stock"] > 5 else "Мало")
        self.compositionLabel.setText(self.product["composition"])
        self.priceLabel.setText(f"{self.product["price"]} руб.")

        self.load_item_image()

        if self.product["stock"] <= 3:
            self.setStyleSheet(
                "QWidget#ItemCard { background-color: #FCE4E4; }"
            )


    def load_item_image(self):
        base_path = Path(__file__).resolve().parent.parent

        placeholder_path = (
                base_path / "resources" / "placeholder.png"
        )

        image_name = self.product.get("image")

        if image_name:
            image_path = base_path / "resources" / "images" / image_name
        else:
            image_path = placeholder_path

        if image_path.is_file():
            pixmap = QPixmap(str(image_path))
        else:
            pixmap = QPixmap(str(placeholder_path))

        self.ItemImage.setPixmap(pixmap)
