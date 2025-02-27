import json
import queue
from collections import namedtuple

MenuItemTuple = namedtuple("MenuItemTuple", ["name", "price", "category", "extra", "descuento"])

class MenuItem:
    def __init__(self, name, price, descuento=0):
        self._name = name
        self._price = price
        self._descuento = descuento

    def compute_price(self):
        return self._price - (self._price * self._descuento / 100)

    def to_dict(self):
        return {"name": self._name, "price": self._price, "descuento": self._descuento}

class Beverage(MenuItem):
    def __init__(self, name, price, size, descuento=0):
        super().__init__(name, price, descuento)
        self._size = size

    def to_dict(self):
        data = super().to_dict()
        data["size"] = self._size
        return data

class Appetizer(MenuItem):
    def __init__(self, name, price, vegetarian=False, descuento=0):
        super().__init__(name, price, descuento)
        self._vegetarian = vegetarian

    def to_dict(self):
        data = super().to_dict()
        data["vegetarian"] = self._vegetarian
        return data

class MainCourse(MenuItem):
    def __init__(self, name, price, country_food, descuento=0):
        super().__init__(name, price, descuento)
        self._country_food = country_food

    def to_dict(self):
        data = super().to_dict()
        data["country_food"] = self._country_food
        return data

class MenuManager:
    def __init__(self, file_path="menu.json"):
        self.file_path = file_path
        self.menu = self.load_menu()

    def load_menu(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError):
            return {}

    def save_menu(self):
        with open(self.file_path, "w") as f:
            json.dump(self.menu, f, indent=4)

    def add_item(self, item: MenuItem, category: str):
        if category not in self.menu:
            self.menu[category] = []
        self.menu[category].append(item.to_dict())
        self.save_menu()

    def update_item(self, category, item_name, new_data):
        if category in self.menu:
            for item in self.menu[category]:
                if item["name"] == item_name:
                    item.update(new_data)
                    self.save_menu()
                    return True
        return False

    def delete_item(self, category, item_name):
        if category in self.menu:
            self.menu[category] = [item for item in self.menu[category] if item["name"] != item_name]
            self.save_menu()

class OrderIterator:
    def __init__(self, items):
        self._items = items
        self._index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index < len(self._items):
            item = self._items[self._index]
            self._index += 1
            return item
        raise StopIteration

class Order:
    def __init__(self):
        self.items = []

    def append_item(self, item: MenuItem):
        self.items.append(item)

    def calculate_total_price(self):
        total = sum(item.compute_price() for item in self.items)
        has_main_course = any(isinstance(item, MainCourse) for item in self.items)
        if has_main_course:
            for item in self.items:
                if isinstance(item, Beverage):
                    total -= item.compute_price() * 0.10
        return total
    
    def __iter__(self):
        return OrderIterator(self.items)

class OrderManager:
    def __init__(self):
        self.orders = queue.Queue()

    def add_order(self, order: Order):
        self.orders.put(order)

    def process_next_order(self):
        if not self.orders.empty():
            return self.orders.get()
        return None

menu_manager = MenuManager()
beverage = Beverage("Coca Cola", 5, "Mediano", descuento=5)
menu_manager.add_item(beverage, "Beverages")

pedido1 = Order()
pedido1.append_item(beverage)
order_manager = OrderManager()
order_manager.add_order(pedido1)

print(f"Total del pedido con descuentos: ${pedido1.calculate_total_price():.2f}")

print("Items en el pedido:")
for item in pedido1:
    print(vars(item))
