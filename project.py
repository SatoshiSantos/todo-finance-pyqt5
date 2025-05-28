import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
    QFormLayout,
    QGroupBox,
    QGridLayout,
    QColorDialog,
    QInputDialog,
    QCheckBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor


def format_currency(amount):
    """Format a float amount as a dollar string."""
    return f"${amount:,.2f}"


def calculate_credit_usage(balance, limit):
    """Return usage percentage of credit as float."""
    if limit == 0:
        return 0.0
    return (balance / limit) * 100


def validate_float(value):
    """Try converting value to float; return None if invalid."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# File to store data
data_file = "data.json"
if not os.path.exists(data_file):
    with open(data_file, "w") as f:
        json.dump(
            {
                "todos": [],
                "credit_cards": [],
                "categories": [
                    {"name": "Personal", "color": "#FF5733"},
                    {"name": "Home", "color": "#33FF57"},
                    {"name": "Education", "color": "#3357FF"},
                    {"name": "Business", "color": "#F033FF"},
                ],
                "properties": [],
                "accounts": [],
                "bills": [],
            },
            f,
        )

with open(data_file, "r") as f:
    data = json.load(f)


def save_data():
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)


class ToDoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Table for displaying todos
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Status", "Completed", "Task", "Category", "Due Date", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 150)
        content_layout.addWidget(self.table)

        # Form for adding new todos (collapsible)
        self.form_group = QGroupBox("Add New Task (Click to Expand)")
        self.form_group.setCheckable(True)
        self.form_group.setChecked(False)
        form_layout = QFormLayout()

        self.task_input = QLineEdit()
        self.category_combo = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItems(
            ["Not Started", "In Progress", "On Hold", "Completed"]
        )
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("YYYY-MM-DD (optional)")

        form_layout.addRow("Task", self.task_input)
        form_layout.addRow("Category", self.category_combo)
        form_layout.addRow("Status", self.status_combo)
        form_layout.addRow("Due Date", self.due_date_input)

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_todo)
        form_layout.addRow(self.add_button)

        self.form_group.setLayout(form_layout)
        content_layout.addWidget(self.form_group)

        # Category management (collapsible)
        self.cat_group = QGroupBox("Manage Categories (Click to Expand)")
        self.cat_group.setCheckable(True)
        self.cat_group.setChecked(False)
        cat_layout = QHBoxLayout()

        self.new_cat_input = QLineEdit()
        self.new_cat_input.setPlaceholderText("Category name")
        self.cat_color_button = QPushButton("Choose Color")
        self.cat_color_button.clicked.connect(self.choose_color)
        self.cat_color_preview = QLabel()
        self.cat_color_preview.setFixedSize(20, 20)
        self.cat_color_preview.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid black"
        )
        self.current_color = "#FFFFFF"

        self.add_cat_button = QPushButton("Add Category")
        self.add_cat_button.clicked.connect(self.add_category)

        cat_layout.addWidget(self.new_cat_input)
        cat_layout.addWidget(self.cat_color_button)
        cat_layout.addWidget(self.cat_color_preview)
        cat_layout.addWidget(self.add_cat_button)

        self.cat_group.setLayout(cat_layout)
        content_layout.addWidget(self.cat_group)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.load_categories()
        self.load_todos()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()
            self.cat_color_preview.setStyleSheet(
                f"background-color: {self.current_color}; border: 1px solid black"
            )

    def add_category(self):
        name = self.new_cat_input.text()
        if not name:
            return

        for cat in data["categories"]:
            if cat["name"].lower() == name.lower():
                return

        data["categories"].append({"name": name, "color": self.current_color})
        save_data()
        self.load_categories()
        self.new_cat_input.clear()

    def load_categories(self):
        self.category_combo.clear()
        for category in data["categories"]:
            if isinstance(category, dict):
                self.category_combo.addItem(category["name"])
            else:
                self.category_combo.addItem(category)

    def add_todo(self):
        task = self.task_input.text()
        if not task:
            return

        category = self.category_combo.currentText()
        status = self.status_combo.currentText()
        due_date = self.due_date_input.text()

        if due_date:
            try:
                QDate.fromString(due_date, "yyyy-MM-dd")
            except:
                due_date = ""

        data["todos"].append(
            {
                "task": task,
                "category": category,
                "status": status,
                "due_date": due_date,
                "completed": False,
            }
        )
        save_data()
        self.load_todos()
        self.task_input.clear()
        self.due_date_input.clear()

    def load_todos(self):
        self.table.setRowCount(0)
        for i, todo in enumerate(data["todos"]):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Status
            status_item = QTableWidgetItem(todo.get("status", "Not Started"))
            status_item.setFlags(status_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 0, status_item)

            # Completed checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(todo["completed"])
            checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_completed(idx, state)
            )
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 1, cell_widget)

            # Task
            task_item = QTableWidgetItem(todo["task"])
            task_item.setFlags(task_item.flags() ^ Qt.ItemIsEditable)
            if todo["completed"]:
                task_item.setForeground(QColor(150, 150, 150))
                font = task_item.font()
                font.setStrikeOut(True)
                task_item.setFont(font)
            self.table.setItem(row, 2, task_item)

            # Category with color
            category_item = QTableWidgetItem(todo["category"])
            category_item.setFlags(category_item.flags() ^ Qt.ItemIsEditable)

            for cat in data["categories"]:
                if isinstance(cat, dict) and cat["name"] == todo["category"]:
                    category_item.setForeground(QColor(cat["color"]))
                    break
                elif cat == todo["category"]:
                    category_item.setForeground(QColor("#000000"))
                    break

            self.table.setItem(row, 3, category_item)

            # Due date
            due_date = todo["due_date"] if todo["due_date"] else "No due date"
            due_item = QTableWidgetItem(due_date)
            due_item.setFlags(due_item.flags() ^ Qt.ItemIsEditable)

            if todo["due_date"] and not todo["completed"]:
                due_date = QDate.fromString(todo["due_date"], "yyyy-MM-dd")
                if due_date < QDate.currentDate():
                    due_item.setForeground(QColor(255, 0, 0))

            self.table.setItem(row, 4, due_item)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_todo(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, idx=i: self.delete_todo(idx))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(row, 5, action_widget)

    def toggle_completed(self, index, state):
        data["todos"][index]["completed"] = state == Qt.Checked
        save_data()
        self.load_todos()

    def edit_todo(self, index):
        todo = data["todos"][index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Task")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        task_edit = QLineEdit(todo["task"])
        category_combo = QComboBox()
        for category in data["categories"]:
            if isinstance(category, dict):
                category_combo.addItem(category["name"])
            else:
                category_combo.addItem(category)
        category_combo.setCurrentText(todo["category"])

        status_combo = QComboBox()
        status_combo.addItems(["Not Started", "In Progress", "On Hold", "Completed"])
        status_combo.setCurrentText(todo.get("status", "Not Started"))

        due_date_edit = QLineEdit(todo["due_date"])
        due_date_edit.setPlaceholderText("YYYY-MM-DD")

        layout.addRow("Task", task_edit)
        layout.addRow("Category", category_combo)
        layout.addRow("Status", status_combo)
        layout.addRow("Due Date", due_date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.save_todo_edit(
                index,
                task_edit.text(),
                category_combo.currentText(),
                status_combo.currentText(),
                due_date_edit.text(),
                dialog,
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def save_todo_edit(self, index, task, category, status, due_date, dialog):
        if not task:
            QMessageBox.warning(self, "Error", "Task cannot be empty")
            return

        if due_date:
            try:
                QDate.fromString(due_date, "yyyy-MM-dd")
            except:
                due_date = ""

        data["todos"][index] = {
            "task": task,
            "category": category,
            "status": status,
            "due_date": due_date,
            "completed": data["todos"][index]["completed"],
        }
        save_data()
        self.load_todos()
        dialog.accept()

    def delete_todo(self, index):
        reply = QMessageBox.question(
            self,
            "Delete Task",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            data["todos"].pop(index)
            save_data()
            self.load_todos()


class FinancialTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Credit Card Section (Collapsible)
        self.cc_group = QGroupBox("Credit Cards (Click to Expand)")
        self.cc_group.setCheckable(True)
        self.cc_group.setChecked(False)
        cc_layout = QVBoxLayout()

        # Add Credit Card Button
        self.add_cc_button = QPushButton("➕ Add New Credit Card")
        self.add_cc_button.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.add_cc_button.clicked.connect(self.show_add_credit_card_dialog)
        cc_layout.addWidget(self.add_cc_button)

        # Credit Card Table
        self.cc_table = QTableWidget(0, 4)
        self.cc_table.setHorizontalHeaderLabels(
            ["Owner", "Card Name", "Balance", "Actions"]
        )
        self.cc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cc_layout.addWidget(self.cc_table)

        self.cc_summary = QLabel()
        cc_layout.addWidget(self.cc_summary)

        self.cc_group.setLayout(cc_layout)
        content_layout.addWidget(self.cc_group)

        # Property Equity Section (Collapsible)
        self.prop_group = QGroupBox("Property Equity (Click to Expand)")
        self.prop_group.setCheckable(True)
        self.prop_group.setChecked(False)
        prop_layout = QVBoxLayout()

        # Add Property Button
        self.add_prop_button = QPushButton("➕ Add New Property")
        self.add_prop_button.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.add_prop_button.clicked.connect(self.show_add_property_dialog)
        prop_layout.addWidget(self.add_prop_button)

        # Property Table
        self.prop_table = QTableWidget(0, 5)
        self.prop_table.setHorizontalHeaderLabels(
            ["Address", "Estimated Value", "Loan Balance", "Equity ($)", "Equity (%)"]
        )
        self.prop_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        prop_layout.addWidget(self.prop_table)

        self.prop_summary = QLabel()
        prop_layout.addWidget(self.prop_summary)

        self.prop_group.setLayout(prop_layout)
        content_layout.addWidget(self.prop_group)

        # Accounts Section (Collapsible)
        self.acc_group = QGroupBox("Liquid Accounts (Click to Expand)")
        self.acc_group.setCheckable(True)
        self.acc_group.setChecked(False)
        acc_layout = QVBoxLayout()

        # Add Account Button
        self.add_acc_button = QPushButton("➕ Add New Account")
        self.add_acc_button.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.add_acc_button.clicked.connect(self.show_add_account_dialog)
        acc_layout.addWidget(self.add_acc_button)

        # Accounts Table
        self.acc_table = QTableWidget(0, 4)
        self.acc_table.setHorizontalHeaderLabels(
            ["Account Name", "Type", "Institution", "Balance"]
        )
        self.acc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        acc_layout.addWidget(self.acc_table)

        self.acc_summary = QLabel()
        acc_layout.addWidget(self.acc_summary)

        self.acc_group.setLayout(acc_layout)
        content_layout.addWidget(self.acc_group)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.load_credit_cards()
        self.load_properties()
        self.load_accounts()

    def show_add_credit_card_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Credit Card")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        owner_edit = QLineEdit()
        name_edit = QLineEdit()
        limit_edit = QLineEdit()
        balance_edit = QLineEdit()
        payment_edit = QLineEdit()
        due_edit = QLineEdit()

        layout.addRow("Owner:", owner_edit)
        layout.addRow("Card Name:", name_edit)
        layout.addRow("Credit Limit:", limit_edit)
        layout.addRow("Current Balance:", balance_edit)
        layout.addRow("Minimum Payment:", payment_edit)
        layout.addRow("Due Date:", due_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.add_credit_card_from_dialog(
                owner_edit.text(),
                name_edit.text(),
                limit_edit.text(),
                balance_edit.text(),
                payment_edit.text(),
                due_edit.text(),
                dialog,
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def add_credit_card_from_dialog(
        self, owner, name, limit, balance, payment, due, dialog
    ):
        try:
            limit = float(limit)
            balance = float(balance)
            payment = float(payment)
        except ValueError:
            QMessageBox.warning(
                self,
                "Error",
                "Please enter valid numbers for limit, balance and payment",
            )
            return

        if not owner or not name:
            QMessageBox.warning(self, "Error", "Owner and Card Name are required")
            return

        available = limit - balance

        card = {
            "owner": owner,
            "card_name": name,
            "limit": limit,
            "available": available,
            "balance": balance,
            "payment": payment,
            "due_date": due,
        }
        data["credit_cards"].append(card)
        save_data()
        self.load_credit_cards()
        dialog.accept()

    def load_credit_cards(self):
        self.cc_table.setRowCount(0)
        total_usage_amount = 0
        total_limit = 0
        owner_debts = {}

        for i, card in enumerate(data["credit_cards"]):
            row = self.cc_table.rowCount()
            self.cc_table.insertRow(row)

            self.cc_table.setItem(row, 0, QTableWidgetItem(card["owner"]))
            self.cc_table.setItem(row, 1, QTableWidgetItem(card["card_name"]))
            self.cc_table.setItem(row, 2, QTableWidgetItem(f"${card['balance']:,.2f}"))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_credit_card(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, idx=i: self.delete_credit_card(idx))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            self.cc_table.setCellWidget(row, 3, action_widget)

            total_limit += card["limit"]
            total_usage_amount += card["balance"]
            owner = card["owner"]
            if owner not in owner_debts:
                owner_debts[owner] = 0
            owner_debts[owner] += card["balance"]

        total_usage_pct = calculate_credit_usage(total_usage_amount, total_limit)
        total_debt = sum(owner_debts.values())

        summary = [
            f"<b>Credit Card Summary:</b>",
            f"Total Credit Limit: ${total_limit:,.2f}",
            f"Total Used: ${total_usage_amount:,.2f}",
            f"Total Usage: {total_usage_pct:.2f}%",
            f"Total Credit Card Debt: ${total_debt:,.2f}",
        ]
        for owner, debt in owner_debts.items():
            summary.append(f"{owner}'s Debt: ${debt:,.2f}")

        self.cc_summary.setText("<br>".join(summary))

    def edit_credit_card(self, index):
        card = data["credit_cards"][index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Credit Card")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        owner_edit = QLineEdit(card["owner"])
        name_edit = QLineEdit(card["card_name"])
        limit_edit = QLineEdit(str(card["limit"]))
        balance_edit = QLineEdit(str(card["balance"]))
        payment_edit = QLineEdit(str(card["payment"]))
        due_edit = QLineEdit(card["due_date"])

        layout.addRow("Owner:", owner_edit)
        layout.addRow("Card Name:", name_edit)
        layout.addRow("Credit Limit:", limit_edit)
        layout.addRow("Current Balance:", balance_edit)
        layout.addRow("Minimum Payment:", payment_edit)
        layout.addRow("Due Date:", due_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.save_credit_card_edit(
                index,
                owner_edit.text(),
                name_edit.text(),
                limit_edit.text(),
                balance_edit.text(),
                payment_edit.text(),
                due_edit.text(),
                dialog,
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def save_credit_card_edit(
        self, index, owner, name, limit, balance, payment, due, dialog
    ):
        limit = validate_float(self.cc_limit_input.text())
        available = validate_float(self.cc_available_input.text())
        balance = validate_float(self.cc_balance_input.text())
        payment = validate_float(self.cc_payment_input.text())

        if None in [limit, available, balance, payment]:
            return

        if not owner or not name:
            QMessageBox.warning(self, "Error", "Owner and Card Name are required")
            return

        available = limit - balance

        data["credit_cards"][index] = {
            "owner": owner,
            "card_name": name,
            "limit": limit,
            "available": available,
            "balance": balance,
            "payment": payment,
            "due_date": due,
        }
        save_data()
        self.load_credit_cards()
        dialog.accept()

    def delete_credit_card(self, index):
        reply = QMessageBox.question(
            self,
            "Delete Credit Card",
            "Are you sure you want to delete this credit card?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            data["credit_cards"].pop(index)
            save_data()
            self.load_credit_cards()

    def show_add_property_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Property")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        address_edit = QLineEdit()
        value_edit = QLineEdit()
        loan_edit = QLineEdit()

        layout.addRow("Address:", address_edit)
        layout.addRow("Estimated Value:", value_edit)
        layout.addRow("Loan Balance:", loan_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.add_property_from_dialog(
                address_edit.text(), value_edit.text(), loan_edit.text(), dialog
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def add_property_from_dialog(self, address, value, loan, dialog):
        try:
            value = float(value)
            loan = float(loan)
        except ValueError:
            QMessageBox.warning(
                self, "Error", "Please enter valid numbers for value and loan balance"
            )
            return

        if not address:
            QMessageBox.warning(self, "Error", "Address is required")
            return

        equity = value - loan
        equity_pct = (equity / value * 100) if value else 0

        data["properties"].append(
            {
                "address": address,
                "value": value,
                "loan": loan,
                "equity": equity,
                "equity_pct": equity_pct,
            }
        )
        save_data()
        self.load_properties()
        dialog.accept()

    def load_properties(self):
        self.prop_table.setRowCount(0)
        total_equity = 0
        total_value = 0

        for i, prop in enumerate(data["properties"]):
            row = self.prop_table.rowCount()
            self.prop_table.insertRow(row)

            self.prop_table.setItem(row, 0, QTableWidgetItem(prop["address"]))
            self.prop_table.setItem(row, 1, QTableWidgetItem(f"${prop['value']:,.2f}"))
            self.prop_table.setItem(row, 2, QTableWidgetItem(f"${prop['loan']:,.2f}"))
            self.prop_table.setItem(row, 3, QTableWidgetItem(f"${prop['equity']:,.2f}"))
            self.prop_table.setItem(
                row, 4, QTableWidgetItem(f"{prop['equity_pct']:.2f}%")
            )

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_property(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, idx=i: self.delete_property(idx))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            self.prop_table.setCellWidget(row, 5, action_widget)

            total_equity += prop["equity"]
            total_value += prop["value"]

        if data["properties"]:
            total_equity_pct = (total_equity / total_value * 100) if total_value else 0
            summary = [
                f"<b>Property Summary:</b>",
                f"Total Properties: {len(data['properties'])}",
                f"Total Estimated Value: ${total_value:,.2f}",
                f"Total Equity: ${total_equity:,.2f}",
                f"Total Equity Percentage: {total_equity_pct:.2f}%",
            ]
            self.prop_summary.setText("<br>".join(summary))
        else:
            self.prop_summary.setText("<b>No properties added yet</b>")

    def edit_property(self, index):
        prop = data["properties"][index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Property")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        address_edit = QLineEdit(prop["address"])
        value_edit = QLineEdit(str(prop["value"]))
        loan_edit = QLineEdit(str(prop["loan"]))

        layout.addRow("Address:", address_edit)
        layout.addRow("Estimated Value:", value_edit)
        layout.addRow("Loan Balance:", loan_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.save_property_edit(
                index, address_edit.text(), value_edit.text(), loan_edit.text(), dialog
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def save_property_edit(self, index, address, value, loan, dialog):
        if not address:
            QMessageBox.warning(self, "Error", "Address cannot be empty")
            return

        try:
            value = float(value)
            loan = float(loan)
        except ValueError:
            QMessageBox.warning(
                self, "Error", "Please enter valid numbers for value and loan balance"
            )
            return

        equity = value - loan
        equity_pct = (equity / value * 100) if value else 0

        data["properties"][index] = {
            "address": address,
            "value": value,
            "loan": loan,
            "equity": equity,
            "equity_pct": equity_pct,
        }
        save_data()
        self.load_properties()
        dialog.accept()

    def delete_property(self, index):
        reply = QMessageBox.question(
            self,
            "Delete Property",
            "Are you sure you want to delete this property?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            data["properties"].pop(index)
            save_data()
            self.load_properties()

    def show_add_account_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Account")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        name_edit = QLineEdit()
        type_combo = QComboBox()
        type_combo.addItems(
            ["Checking", "Savings", "Retirement", "Investment", "Business"]
        )
        institution_edit = QLineEdit()
        balance_edit = QLineEdit()

        layout.addRow("Account Name:", name_edit)
        layout.addRow("Account Type:", type_combo)
        layout.addRow("Institution:", institution_edit)
        layout.addRow("Balance:", balance_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.add_account_from_dialog(
                name_edit.text(),
                type_combo.currentText(),
                institution_edit.text(),
                balance_edit.text(),
                dialog,
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def add_account_from_dialog(self, name, acc_type, institution, balance, dialog):
        try:
            balance = float(balance)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid balance")
            return

        if not name:
            QMessageBox.warning(self, "Error", "Account name is required")
            return

        data["accounts"].append(
            {
                "name": name,
                "type": acc_type,
                "institution": institution,
                "balance": balance,
            }
        )
        save_data()
        self.load_accounts()
        dialog.accept()

    def load_accounts(self):
        self.acc_table.setRowCount(0)
        total_balance = 0

        for i, acc in enumerate(data["accounts"]):
            row = self.acc_table.rowCount()
            self.acc_table.insertRow(row)

            self.acc_table.setItem(row, 0, QTableWidgetItem(acc["name"]))
            self.acc_table.setItem(row, 1, QTableWidgetItem(acc["type"]))
            self.acc_table.setItem(row, 2, QTableWidgetItem(acc["institution"]))
            self.acc_table.setItem(row, 3, QTableWidgetItem(f"${acc['balance']:,.2f}"))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_account(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, idx=i: self.delete_account(idx))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            self.acc_table.setCellWidget(row, 4, action_widget)

            total_balance += acc["balance"]

        if data["accounts"]:
            summary = [
                f"<b>Account Summary:</b>",
                f"Total Accounts: {len(data['accounts'])}",
                f"Total Balance: ${total_balance:,.2f}",
            ]
            self.acc_summary.setText("<br>".join(summary))
        else:
            self.acc_summary.setText("<b>No accounts added yet</b>")

    def edit_account(self, index):
        acc = data["accounts"][index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Account")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        name_edit = QLineEdit(acc["name"])
        type_combo = QComboBox()
        type_combo.addItems(
            ["Checking", "Savings", "Retirement", "Investment", "Business"]
        )
        type_combo.setCurrentText(acc["type"])
        institution_edit = QLineEdit(acc["institution"])
        balance_edit = QLineEdit(str(acc["balance"]))

        layout.addRow("Account Name:", name_edit)
        layout.addRow("Account Type:", type_combo)
        layout.addRow("Institution:", institution_edit)
        layout.addRow("Balance:", balance_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.save_account_edit(
                index,
                name_edit.text(),
                type_combo.currentText(),
                institution_edit.text(),
                balance_edit.text(),
                dialog,
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def save_account_edit(self, index, name, acc_type, institution, balance, dialog):
        if not name:
            QMessageBox.warning(self, "Error", "Account name cannot be empty")
            return

        try:
            balance = float(balance)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid balance")
            return

        data["accounts"][index] = {
            "name": name,
            "type": acc_type,
            "institution": institution,
            "balance": balance,
        }
        save_data()
        self.load_accounts()
        dialog.close()

    def delete_account(self, index):
        reply = QMessageBox.question(
            self,
            "Delete Account",
            "Are you sure you want to delete this account?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            data["accounts"].pop(index)
            save_data()
            self.load_accounts()


class BillsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Bills Table
        self.bills_table = QTableWidget(0, 5)
        self.bills_table.setHorizontalHeaderLabels(
            ["Bill Name", "Amount", "Due Date", "Paid", "Actions"]
        )
        self.bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        content_layout.addWidget(self.bills_table)

        # Add Bill Button
        self.add_bill_button = QPushButton("➕ Add New Bill")
        self.add_bill_button.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.add_bill_button.clicked.connect(self.show_add_bill_dialog)
        content_layout.addWidget(self.add_bill_button)

        # Monthly Total
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        content_layout.addWidget(self.total_label)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.load_bills()

    def show_add_bill_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Bill")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        name_edit = QLineEdit()
        amount_edit = QLineEdit()
        due_edit = QLineEdit()
        due_edit.setPlaceholderText("YYYY-MM-DD")

        layout.addRow("Bill Name:", name_edit)
        layout.addRow("Amount:", amount_edit)
        layout.addRow("Due Date:", due_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.add_bill_from_dialog(
                name_edit.text(), amount_edit.text(), due_edit.text(), dialog
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def add_bill_from_dialog(self, name, amount, due_date, dialog):
        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount")
            return

        if not name:
            QMessageBox.warning(self, "Error", "Bill name is required")
            return

        # Validate date format
        if due_date:
            try:
                QDate.fromString(due_date, "yyyy-MM-dd")
            except:
                due_date = ""

        data["bills"].append(
            {"name": name, "amount": amount, "due_date": due_date, "paid": False}
        )
        save_data()
        self.load_bills()
        dialog.accept()

    def load_bills(self):
        self.bills_table.setRowCount(0)
        total_amount = 0

        for i, bill in enumerate(data["bills"]):
            row = self.bills_table.rowCount()
            self.bills_table.insertRow(row)

            # Bill Name
            name_item = QTableWidgetItem(bill["name"])
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            self.bills_table.setItem(row, 0, name_item)

            # Amount
            amount_item = QTableWidgetItem(f"${bill['amount']:,.2f}")
            amount_item.setFlags(amount_item.flags() ^ Qt.ItemIsEditable)
            self.bills_table.setItem(row, 1, amount_item)

            # Due Date
            due_date = bill["due_date"] if bill["due_date"] else "No due date"
            due_item = QTableWidgetItem(due_date)
            due_item.setFlags(due_item.flags() ^ Qt.ItemIsEditable)

            # Highlight overdue bills in red
            if bill["due_date"] and not bill["paid"]:
                due_date = QDate.fromString(bill["due_date"], "yyyy-MM-dd")
                if due_date < QDate.currentDate():
                    due_item.setForeground(QColor(255, 0, 0))

            self.bills_table.setItem(row, 2, due_item)

            # Paid checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(bill["paid"])
            checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_paid(idx, state)
            )
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.bills_table.setCellWidget(row, 3, cell_widget)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, idx=i: self.edit_bill(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, idx=i: self.delete_bill(idx))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)

            self.bills_table.setCellWidget(row, 4, action_widget)

            if not bill["paid"]:
                total_amount += bill["amount"]

        self.total_label.setText(f"<b>Monthly Total: ${total_amount:,.2f}</b>")

    def toggle_paid(self, index, state):
        data["bills"][index]["paid"] = state == Qt.Checked
        save_data()
        self.load_bills()

    def edit_bill(self, index):
        bill = data["bills"][index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Bill")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        name_edit = QLineEdit(bill["name"])
        amount_edit = QLineEdit(str(bill["amount"]))
        due_edit = QLineEdit(bill["due_date"])
        due_edit.setPlaceholderText("YYYY-MM-DD")

        layout.addRow("Bill Name:", name_edit)
        layout.addRow("Amount:", amount_edit)
        layout.addRow("Due Date:", due_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(
            lambda: self.save_bill_edit(
                index, name_edit.text(), amount_edit.text(), due_edit.text(), dialog
            )
        )
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.exec_()

    def save_bill_edit(self, index, name, amount, due_date, dialog):
        if not name:
            QMessageBox.warning(self, "Error", "Bill name cannot be empty")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount")
            return

        # Validate date format
        if due_date:
            try:
                QDate.fromString(due_date, "yyyy-MM-dd")
            except:
                due_date = ""

        data["bills"][index] = {
            "name": name,
            "amount": amount,
            "due_date": due_date,
            "paid": data["bills"][index]["paid"],
        }
        save_data()
        self.load_bills()
        dialog.accept()

    def delete_bill(self, index):
        reply = QMessageBox.question(
            self,
            "Delete Bill",
            "Are you sure you want to delete this bill?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            data["bills"].pop(index)
            save_data()
            self.load_bills()


class MainApp(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Family Finance Manager")
        self.resize(1200, 800)

        self.todo_tab = ToDoTab()
        self.finance_tab = FinancialTab()
        self.bills_tab = BillsTab()

        self.addTab(self.todo_tab, "To-Do List")
        self.addTab(self.finance_tab, "Financial Snapshot")
        self.addTab(self.bills_tab, "Monthly Bills")


def main():
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
