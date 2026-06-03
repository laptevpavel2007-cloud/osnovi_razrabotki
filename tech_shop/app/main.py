import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.csv_loader import CSVLoader
from packages.core.product import ProductService
from packages.core.cart import ShoppingCart
from packages.core.receipt import ReceiptService
from packages.core.warehouse import WarehouseService
from packages.core.returns import ReturnsService
from packages.core.pc_builder import PCBuilderService
from packages.core.statistics import StatisticsService
from app.config import DB_PATH, DATA_DIR, DEFAULT_CASHIER_ID

class TechShopApp:
    def __init__(self):
        self.db = Database(DB_PATH)
        self.db.init_schema()
        
        loader = CSVLoader(self.db)
        loader.load_all(DATA_DIR)
        
        self.product_service = ProductService(self.db)
        self.receipt_service = ReceiptService(self.db)
        self.warehouse_service = WarehouseService(self.product_service)
        self.returns_service = ReturnsService(self.db, self.product_service)
        self.pc_builder_service = PCBuilderService(self.db, self.product_service)
        self.statistics_service = StatisticsService(self.db)
        self.cart = ShoppingCart()
        
        self.root = tk.Tk()
        self.root.geometry("970x400")
        self.root.title("Магазин техники")
        self.root.configure(bg="#f0f0f0")
        
        self.basket_window = None
        self.catalog_window = None
        self.basket_labels = []
        self.scrollable_frame = None
        self.total_lbl = None
        
        self._create_main_ui()
    
    def _create_main_ui(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg="#f0f0f0", padx=15, pady=15)
        top_frame.pack(fill='x')
        
        input_frame = tk.Frame(top_frame, bg="#f0f0f0")
        input_frame.pack(fill='x', pady=5)
        
        tk.Label(input_frame, text="Название товара:", font="Arial 14", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
        self.name_entry = tk.Entry(input_frame, font="Arial 14", width=30, relief="solid", bd=1)
        self.name_entry.pack(side='left', padx=5)
        
        tk.Label(input_frame, text="Кол-во:", font="Arial 14", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
        self.qty_entry = tk.Entry(input_frame, font="Arial 14", width=6, relief="solid", bd=1)
        self.qty_entry.pack(side='left', padx=5)
        
        self.status_label = tk.Label(top_frame, text=" ", font="Arial 14", bg="#f0f0f0")
        self.status_label.pack(pady=5)
        
        tk.Button(top_frame, text="Добавить в корзину", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=self._add_to_cart).pack(pady=5)
        
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        bottom_frame.pack(side='bottom', fill='x')
        
        tk.Button(bottom_frame, text="Добавить на склад", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=self._open_warehouse).pack(side='left', padx=10, expand=True)
        
        tk.Button(bottom_frame, text="Вернуть товар", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=self._open_returns).pack(side='left', padx=10, expand=True)
        
        tk.Button(bottom_frame, text="Собрать ПК", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=self._open_pc_builder).pack(side='left', padx=10, expand=True)
        
        tk.Button(bottom_frame, text="Корзина", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=self._open_basket).pack(side='left', padx=10, expand=True)
        
        tk.Button(bottom_frame, text="Каталог", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=self._open_catalog).pack(side='left', padx=10, expand=True)
        
        tk.Button(bottom_frame, text="Статистика", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5,command=self._open_statistics).pack(side='left', padx=10, expand=True)
    
    def _add_to_cart(self):
        self._open_basket()
        name = self.name_entry.get().strip()
        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            self.status_label.config(text="Введите числовое значение!", fg="red")
            return
        
        if qty <= 0:
            self.status_label.config(text="Количество должно быть > 0!", fg="red")
            return
        
        product = self.product_service.get_by_name(name)
        if not product:
            self.status_label.config(text="Товар не найден!", fg="red")
            return
        
        try:
            product.reduce_stock(qty)
            self.cart.add_item(product, qty)
            self.product_service.update_stock(product.id, product.quantity)
            
            lbl = tk.Label(self.scrollable_frame, text=f"{product.name} x {qty} = {product.price * qty:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
            lbl.pack(anchor='w', pady=2)
            self.basket_labels.append(lbl)
            
            self.total_lbl.config(text=f"Итоговая сумма: {self.cart.total_sum:.2f} руб.")
            self.status_label.config(text=" ", fg="green")
        except ValueError as e:
            self.status_label.config(text=str(e), fg="red")
    
    def _open_basket(self):
        if self.basket_window and self.basket_window.winfo_exists():
            self.basket_window.lift()
            return
        
        self.basket_window = tk.Toplevel(self.root)
        self.basket_window.geometry("500x550")
        self.basket_window.title("Корзина")
        self.basket_window.configure(bg="#f0f0f0")
        self.basket_window.protocol("WM_DELETE_WINDOW", self._close_basket)
        
        basket_frame = tk.Frame(self.basket_window, bg="#f0f0f0", padx=15, pady=15)
        basket_frame.pack(fill='both', expand=True)
        
        tk.Label(basket_frame, text="Корзина", font="Arial 18 bold", bg="#f0f0f0", fg="#2c6e9e").pack()
        
        items_container = tk.Frame(basket_frame, bg="#f0f0f0")
        items_container.pack(fill='both', expand=True, pady=10)
        
        canvas = tk.Canvas(items_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(items_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        self.scrollable_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        bottom_panel = tk.Frame(basket_frame, bg="#f0f0f0")
        bottom_panel.pack(fill='x', pady=10)
        
        self.total_lbl = tk.Label(bottom_panel, text=f"Итоговая сумма: {self.cart.total_sum:.2f} руб.", font="Arial 16 bold", bg="#f0f0f0", fg="#2c6e9e")
        self.total_lbl.pack(side='left', padx=10)
        
        tk.Button(bottom_panel, text="Купить", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=15, pady=5, command=self._buy).pack(side='right', padx=10)
    
    def _close_basket(self):
        if self.basket_window:
            self.basket_window.destroy()
            self.basket_window = None
    
    def _buy(self):
        if self.cart.is_empty:
            messagebox.showinfo("Корзина", "Корзина пуста!")
            return
        
        items = self.cart.get_tuples()
        receipt = self.receipt_service.create_receipt(DEFAULT_CASHIER_ID, items)
        
        self._show_receipt(receipt)
        
        self.cart.clear()
        for lbl in self.basket_labels:
            lbl.destroy()
        self.basket_labels.clear()
        self.total_lbl.config(text="Итоговая сумма: 0.00 руб.")
        
        if self.basket_window:
            self.basket_window.destroy()
            self.basket_window = None
    
    def _show_receipt(self, receipt):
        win = tk.Toplevel(self.root)
        win.title(f"Чек №{receipt['id']}")
        win.geometry("480x500")
        win.configure(bg="#f0f0f0")
        
        frame = tk.Frame(win, bg="#f0f0f0", padx=15, pady=15)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text=f"ЧЕК №{receipt['id']}", font="Arial 16 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=5)
        tk.Label(frame, text=receipt['date'], font="Arial 10", bg="#f0f0f0", fg="#555555").pack(pady=2)
        tk.Label(frame, text="-" * 40, font="Arial 10", bg="#f0f0f0").pack()
        
        items_frame = tk.Frame(frame, bg="#f0f0f0")
        items_frame.pack(fill='both', expand=True, pady=5)
        
        tk.Label(items_frame, text="Товар", width=25, anchor='w', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=0, sticky='w')
        tk.Label(items_frame, text="Кол-во", width=6, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=1, padx=5)
        tk.Label(items_frame, text="Цена", width=8, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        tk.Label(items_frame, text="Сумма", width=8, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=3, padx=5)
        
        for i, (_, name, qty, price, total) in enumerate(receipt['items'], start=1):
            tk.Label(items_frame, text=name[:25], width=25, anchor='w', font="Arial 10", bg="#f0f0f0").grid(row=i, column=0, sticky='w')
            tk.Label(items_frame, text=str(qty), width=6, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=1, padx=5)
            tk.Label(items_frame, text=f"{price:.2f}", width=8, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=2, padx=5)
            tk.Label(items_frame, text=f"{total:.2f}", width=8, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=3, padx=5)
        
        tk.Label(frame, text="-" * 40, font="Arial 10", bg="#f0f0f0").pack(pady=5)
        tk.Label(frame, text=f"ИТОГО: {receipt['total']:.2f} руб.", font="Arial 14 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=5)
        tk.Button(frame, text="Закрыть", font="Arial 12", bg="#2c6e9e", fg="white", command=win.destroy).pack(pady=10)
    
    def _open_catalog(self):
        if self.catalog_window and self.catalog_window.winfo_exists():
            self.catalog_window.lift()
            return
        
        self.catalog_window = tk.Toplevel(self.root)
        self.catalog_window.geometry("500x750")
        self.catalog_window.title("Каталог товаров")
        self.catalog_window.configure(bg="#f0f0f0")
        
        frame = tk.Frame(self.catalog_window, bg="#f0f0f0", padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="Каталог товаров", font="Arial 18 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=10)
        
        canvas = tk.Canvas(frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#f0f0f0")
        scrollable.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        products = self.product_service.get_all()
        for p in products:
            tk.Label(scrollable, text=f"{p.name} — {p.price:.2f} руб.", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=2, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _open_warehouse(self):
        win = tk.Toplevel(self.root)
        win.geometry("550x300")
        win.title("Склад")
        win.configure(bg="#f0f0f0")
        
        frame = tk.Frame(win, bg="#f0f0f0", padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        input_frame = tk.Frame(frame, bg="#f0f0f0")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Название товара:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(side='left', padx=(0, 5))
        name_entry = tk.Entry(input_frame, font="Arial 12", width=20, relief="solid", bd=1)
        name_entry.pack(side='left', padx=(0, 15))
        
        tk.Label(input_frame, text="Количество:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(side='left', padx=(0, 5))
        qty_entry = tk.Entry(input_frame, font="Arial 12", width=8, relief="solid", bd=1)
        qty_entry.pack(side='left')
        
        status = tk.Label(frame, text=" ", font="Arial 12", bg="#f0f0f0")
        status.pack(pady=10)
        
        def add():
            name = name_entry.get().strip()
            try:
                qty = float(qty_entry.get())
            except ValueError:
                status.config(text="Введите число!", fg="red")
                return
            
            result = self.warehouse_service.add_to_warehouse(name, qty)
            status.config(text=result['message'], fg="green" if result['success'] else "red")
        
        tk.Button(frame, text="Добавить на склад", font="Arial 12", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=add).pack(pady=10)
    
    def _open_returns(self):
        win = tk.Toplevel(self.root)
        win.geometry("600x600")
        win.title("Возврат товара")
        win.configure(bg="#f0f0f0")
        
        frame = tk.Frame(win, bg="#f0f0f0", padx=15, pady=15)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="Номер чека:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0, 5))
        check_entry = tk.Entry(frame, font="Arial 12", width=20, relief="solid", bd=1)
        check_entry.pack(anchor='w', pady=(0, 10))
        
        products_data = {}
        
        def load_check():
            check_id_str = check_entry.get().strip()
            if not check_id_str.isdigit():
                status.config(text="Введите корректный номер чека", fg="red")
                return
            
            check_id = int(check_id_str)
            items = self.returns_service.get_available_for_return(check_id)
            
            listbox.delete(0, tk.END)
            products_data.clear()
            
            if not items:
                status.config(text=f"Чек №{check_id} не найден или пуст", fg="red")
                return
            
            for item in items:
                display = (f"{item['name']} (доступно: {item['available']} шт., "f"цена: {item['price']} руб.)")
                listbox.insert(tk.END, display)
                products_data[display] = item
            
            status.config(text=f"Найдено {len(items)} позиций", fg="green")
        
        tk.Button(frame, text="Загрузить товары", font="Arial 12", bg="#e0e0e0", relief="raised", command=load_check).pack(pady=5)
        
        tk.Label(frame, text="Товары:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(10, 5))
        listbox = tk.Listbox(frame, font="Arial 12", height=8, bg="white", fg="#333333", relief="solid", bd=1)
        listbox.pack(fill='x', pady=(0, 10))
        
        tk.Label(frame, text="Количество:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0, 5))
        qty_entry = tk.Entry(frame, font="Arial 12", width=10, relief="solid", bd=1)
        qty_entry.pack(anchor='w', pady=(0, 10))
        
        tk.Label(frame, text="Причина:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0, 5))
        reason_var = tk.StringVar(value="Не подошёл")
        reasons = ["Не подошёл", "Брак", "Передумал", "Другое"]
        reason_menu = ttk.Combobox(frame, textvariable=reason_var, values=reasons, state="readonly", font="Arial 12")
        reason_menu.pack(anchor='w', pady=(0, 10))
        
        status = tk.Label(frame, text=" ", font="Arial 12", bg="#f0f0f0")
        status.pack(pady=5)
        
        def do_return():
            sel = listbox.curselection()
            if not sel:
                status.config(text="Выберите товар", fg="red")
                return
            
            item = products_data.get(listbox.get(sel[0]))
            if not item:
                status.config(text="Товар не найден", fg="red")
                return
            
            try:
                qty = float(qty_entry.get())
            except ValueError:
                status.config(text="Введите число", fg="red")
                return
            
            result = self.returns_service.process_return(item['sale_id'], qty, reason_var.get())

            status.config(text=result['message'], fg="green" if result['success'] else "red")
            
            if result['success']:
                load_check()
                qty_entry.delete(0, tk.END)
        
        tk.Button(frame, text="Вернуть товар", font="Arial 12", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=do_return).pack(pady=10)
    
    def _open_pc_builder(self):
        win = tk.Toplevel(self.root)
        win.geometry("700x450")
        win.title("Сборка ПК")
        win.configure(bg="#f0f0f0")
        
        frame = tk.Frame(win, bg="#f0f0f0", padx=15, pady=15)
        frame.pack(fill='both', expand=True)
        
        status = tk.Label(frame, text=" ", font="Arial 12", bg="#f0f0f0", fg="red")
        status.pack(pady=5)
        
        comboboxes = {}
        for comp_name in PCBuilderService.COMPONENTS.keys():
            f = tk.Frame(frame, bg="#f0f0f0")
            f.pack(fill='x', pady=6)
            
            tk.Label(f, text=comp_name + ":", width=20, anchor='e', font="Arial 12", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
            
            items = self.pc_builder_service.get_components(comp_name)
            values = [f"{p[1]} - {p[2]} руб. (остаток {p[3]})" for p in items]
            cb = ttk.Combobox(f, values=values, width=45, state="readonly", font="Arial 12")
            cb.pack(side='left', padx=5)
            if values:
                cb.current(0)
            comboboxes[comp_name] = (cb, items)
        
        def add_pc():
            selected = {}
            for name, (cb, items) in comboboxes.items():
                sel = cb.get()
                if not sel:
                    status.config(text=f"Выберите {name.lower()}!", fg="red")
                    return
                for p in items:
                    if f"{p[1]} - {p[2]} руб. (остаток {p[3]})" == sel:
                        selected[name] = p[0]
                        break
            
            need_help = messagebox.askyesno("Помощь в сборке", "Нужна помощь в сборке? (+2000 руб.)")
            
            result = self.pc_builder_service.build_pc(selected, need_help)
            status.config(text=result['message'], fg="green" if result['success'] else "red")
            
            if result['success']:
                self._open_basket()

                for prod_id, name, price, qty in result['items']:
                    product = self.product_service.get_by_id(prod_id)

                    if product:
                        from packages.core.cart import CartItem
                        item = CartItem(prod_id, name, qty, price, price * qty)
                        self.cart.items.append(item)
                        
                        lbl = tk.Label(self.scrollable_frame, text=f"{name} x {qty} = {price * qty:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
                        lbl.pack(anchor='w', pady=2)
                        self.basket_labels.append(lbl)
                
                self.total_lbl.config(text=f"Итоговая сумма: {self.cart.total_sum:.2f} руб.")
                win.after(2000, win.destroy)
        
        tk.Button(frame, text="Добавить ПК в корзину", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=add_pc).pack(pady=20)
    
    def _open_statistics(self):
        win = tk.Toplevel(self.root)
        win.geometry("500x400")
        win.title("Статистика")
        win.configure(bg="#f0f0f0")
        
        frame = tk.Frame(win, bg="#f0f0f0", padx=15, pady=15)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(pady=(0, 5))
        date_entry = tk.Entry(frame, font="Arial 12", width=30, relief="solid", bd=1)
        date_entry.pack(pady=(0, 10))
        
        result_label = tk.Label(frame, text=" ", font="Arial 12", bg="#f0f0f0")
        result_label.pack(pady=5)
        
        def show():
            date_str = date_entry.get().strip()
            try:
                result = self.statistics_service.get_best_seller(date_str)
                if result:
                    name, qty = result
                    result_label.config(
                        text=f"Самый продаваемый: {name}\nПродано: {qty:.0f} шт.", fg="green")
                else:
                    result_label.config(text=f"За {date_str} продаж нет", fg="red")
            except ValueError as e:
                result_label.config(text=str(e), fg="red")
        
        tk.Button(frame, text="Показать", font="Arial 12", bg="#2c6e9e", fg="white", command=show).pack(pady=10)
    
    def run(self):
        self.root.mainloop()
        self.db.close()

if __name__ == "__main__":
    app = TechShopApp()
    app.run()