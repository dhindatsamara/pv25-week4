from PyQt5 import QtWidgets, uic
import re
import sys

class POSApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('pv25-week4/kasir.ui', self)

        self.products = {}
        for i in range(1, self.productList.count()):  
            item_text = self.productList.itemText(i)

            match = re.search(r'\(Rp([\d\.]+)\)', item_text)  
            if match:
                price = int(match.group(1).replace('.', ''))  
                product_name = item_text.split(' (')[0]  
                self.products[product_name] = price
            else:
                print(f"Warning: Tidak bisa membaca harga untuk '{item_text}'")

        self.add.clicked.connect(self.add_to_cart)
        self.clear.clicked.connect(self.clear_cart)
        self.remove.clicked.connect(self.remove_selected_item)
        self.uang.textChanged.connect(self.calculate_change)  
        self.total_price = 0

    def add_to_cart(self):
        product_full_text = self.productList.currentText()
        product = product_full_text.split(' (')[0]

        if product not in self.products:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Silakan pilih produk yang valid!")
            return

        quantity = self.qtySpin.value()
        discount_text = self.discList.currentText()
        discount = int(discount_text.replace('%', '')) / 100

        if quantity <= 0:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Jumlah harus lebih dari 0!")
            return

        price_per_item = self.products[product]
        price = price_per_item * quantity
        discount_amount = price * discount
        final_price = price - discount_amount

        price_str = f"{price_per_item:,}".replace(",", ".")
        final_price_str = f"{final_price:,.0f}".replace(",", ".")

        item_text = f"{product} - {quantity} x Rp{price_str} (disc {discount_text}) = Rp{final_price_str}"
        item = QtWidgets.QListWidgetItem(item_text)
        
        item.setData(32, final_price)  
        item.setData(33, f"{product} (Rp{price_str})")  

        self.result.addItem(item)

        self.total_price += final_price
        self.total.setText(f"Total: Rp{self.total_price:,.0f}".replace(",", "."))
        self.calculate_change()

        self.qtySpin.setValue(1)
        self.discList.setCurrentIndex(0)
        self.productList.setCurrentIndex(0)

    def remove_selected_item(self):
        selected_item = self.result.currentItem()
        if selected_item:
            product_info = selected_item.data(33)

            response = QtWidgets.QMessageBox.question(
                self, "Konfirmasi", f"Apakah Anda yakin ingin menghapus item ini?\n\n{product_info}",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
            )
            if response == QtWidgets.QMessageBox.Yes:
                final_price = selected_item.data(32)
                self.total_price -= final_price
                self.total.setText(f"Total: Rp{self.total_price:,.0f}".replace(",", "."))
                self.calculate_change()  
                self.result.takeItem(self.result.row(selected_item))

    def clear_cart(self):
        response = QtWidgets.QMessageBox.question(
            self, "Konfirmasi", "Apakah Anda yakin ingin menghapus semua item dalam keranjang?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )

        if response == QtWidgets.QMessageBox.Yes:
            self.result.clear()
            self.total_price = 0
            self.total.setText("Total: Rp0")
            self.kembalian.setText("Kembalian: Rp0") 
            self.uang.clear()  
            self.qtySpin.setValue(1)
            self.discList.setCurrentIndex(0)
            self.productList.setCurrentIndex(0)


    def calculate_change(self):
        uang_text = self.uang.text().replace(".", "")  
        if uang_text.isdigit():
            uang_user = int(uang_text)
            kembalian = uang_user - self.total_price
            kembalian_str = f"Kembalian: Rp{kembalian:,.0f}".replace(",", ".")
            self.kembalian.setText(kembalian_str if kembalian >= 0 else "Kembalian: Rp0")  
        else:
            self.kembalian.setText("Kembalian: Rp0")  

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = POSApp()
    window.show()
    sys.exit(app.exec_())
