import customtkinter
import CTkToolTip as tooltips
from tkinter import dnd

class TableRowWidget(customtkinter.CTkFrame):
    def __init__(self, *args,
                    width: int = 100,
                    height: int = 32,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(fg_color=("gray78", "gray25"))  # set frame color
        self.highlighted = False
        self.data = []
        self.class_obj = None
        self.data_vars: list[customtkinter.StringVar] = []
class AdvancedTableWidgetFactory(object):
    def __init__(self) -> None:
        self.row_elemenet_dict = {}
        self.highlight_element_list = []
        self.master = None
    def register_widget_function(self, index, widget_func, highlightable=True):
        self.row_elemenet_dict[index] = widget_func
        if highlightable:
            self.highlight_element_list.append(index)
    def register_master(self, master):
        self.master = master
    def create_widget(self, index, master=None) -> (customtkinter.CTkBaseClass, customtkinter.StringVar):
        if master:
            widget_master = master
        else:
            widget_master = self.master
        widget, widget_data = self.row_elemenet_dict[index](master=widget_master)
        widget.is_highlightable = bool(index in self.highlight_element_list)
        return widget, widget_data
    def register_default_label(self, index):
        def create_label_widget(master) -> (customtkinter.CTkEntry, customtkinter.StringVar):
            data_var = customtkinter.StringVar(master=master, value="None")
            entry = customtkinter.CTkLabel(master=master, textvariable=data_var)
            return entry, data_var
        self.register_widget_function(index, create_label_widget, True)

class AdvancedTableWidget (customtkinter.CTkScrollableFrame):
        
    def __init__(self, *args,
                    width: int = 150,
                    height: int = 32,
                    table_data: list[list[str]],
                    table_tooltips: dict = {},
                    table_headers: list[str] = None,
                    highlight_row_wrapper = None,
                    row_class_list: list[object] = None,
                    widget_factory: AdvancedTableWidgetFactory,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(fg_color=("gray78", "gray21"))  # set frame color
        self.headers = table_headers
        self.highlight_row_wrapper = highlight_row_wrapper
        self.rows: list[AdvancedTableWidget.AdvancedRow] = []
        self.bind_widget_factory(widget_factory)
        header_offset = 0
        self.columns = 0
        if self.headers is not None:
            header_offset += 1
            for j, header in enumerate(self.headers):
                header_label = customtkinter.CTkLabel(self, text=header, fg_color="gray30", corner_radius=6)
                header_label.grid(row=0, column=j, padx=10, pady=10, sticky="ew")
        
        if row_class_list:
            for row, class_to_add in zip(table_data, row_class_list):
                self.add_table_row(row, class_to_add, row_tooltips=table_tooltips.get(tuple(row), []))
        else:
            for row in table_data:
                self.add_table_row(row, None)
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
        ### Tooltips

    def bind_widget_factory(self, widget_factory: AdvancedTableWidgetFactory):
        self.widget_factory = widget_factory
        self.widget_factory.register_master(self)
    class AdvancedRow (customtkinter.CTkFrame):
        def __init__(self, *args,
                    width: int = 100,
                    height: int = 32,
                    **kwargs):
            super().__init__(*args, width=width, height=height, **kwargs)
            self.configure(fg_color=("gray78", "gray25"))  # set frame color
            self.highlighted = False
            self.data = []
            self.class_obj = None
            self.data_vars: list[customtkinter.StringVar] = []
            self.cell_widgets: list[customtkinter.CTkBaseClass] = []
        def bind_class(self, class_object):
            self.class_obj = class_object
    def remove_row_index(self, row:int):
        row_frame = self.rows.pop(row)
        row_frame.grid_forget()
        self.update_rows_positions()
    def remove_row(self, row:AdvancedRow):
        row.grid_remove()
        self.rows.remove(row)
        self.update_rows_positions()
    def remove_row_by_class(self, row_class):
        row_to_remove = None
        for row in self.rows:
            if row.class_obj == row_class:
                row_to_remove = row
        if row_to_remove:
            self.rows.remove(row_to_remove)
            row_to_remove.grid_forget()
        else:
            raise(KeyError)
    def update_rows_positions(self):
        for i, row in enumerate(self.rows):
            row.grid(row=i+bool(self.headers))
    def get_row_class_list(self):
        return [row.class_obj for row in self.rows]
    def highlight_row(self, e, row_element: AdvancedRow, row):
        row_element.configure(fg_color="red")
        if row_element.highlighted:
            row_element.configure(fg_color="gray25")
            row_element.highlighted = False
        else:
            for row_list_element in self.rows:
                if row_list_element.highlighted:
                    row_list_element.configure(fg_color="gray25")
                    row_list_element.highlighted = False
            row_element.configure(fg_color="red")
            row_element.highlighted = True
        if self.highlight_row_wrapper is not None:
            self.highlight_row_wrapper(row_element, row)
    def add_table_row(self, row_data, class_to_add, row_tooltips: list[str]=[]):
        index = len(self.rows)
        if self.headers:
            headers = True
        else:
            headers = False
        table_row_widget = self.AdvancedRow(self)
        table_row_widget.grid(row = index+headers,column=0, padx=10,pady=5, sticky="ew", columnspan=(len(row_data)))
        table_row_widget.bind("<Button-1>", lambda e, row_element=table_row_widget, row=index: self.highlight_row(e, row_element=row_element, row=row))
        self.rows.append(table_row_widget)
        table_row_widget.data = row_data
        table_row_widget.bind_class(class_to_add)
        columns = len(row_data)
        for j, text in enumerate(row_data):
            cell: customtkinter.CTkBaseClass
            cell, data_var = self.widget_factory.create_widget(j, master=table_row_widget)
            table_row_widget.data_vars.append(data_var)
            table_row_widget.cell_widgets.append(cell)
            data_var.set(text)
            try:
                cell.tooltip = self.add_tooltip_to_cell(cell, row_tooltips[j])
            except IndexError:
                pass
            cell.grid(row=0, column=j, padx=5, pady=0, sticky="ew", in_=table_row_widget)
            if cell.is_highlightable:
                cell.bind("<Button-1>", lambda e, row_element=table_row_widget, row=index: self.highlight_row(e, row_element=row_element, row=row))
        if columns > self.columns:
            self.columns = columns
        for column_num in range(table_row_widget.grid_size()[0]):
            table_row_widget.columnconfigure(column_num, weight=1)
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
        
        
    def update_table(self, data, class_list:list):
        #### Need to slice into new list to not have bad results!
        for row in self.rows[:]:
            self.remove_row(row)
        for row, class_to_add in zip(data, class_list):
            self.add_table_row(row, class_to_add)

    def add_tooltip_to_cell(self, widget, message):
        tooltip = tooltips.CTkToolTip(widget, message, delay=0.5)
        return tooltip
    
### Refactor, remove class
class DragableLabel(customtkinter.CTkLabel):

    def __init__(self, *args,
                    width: int = 150,
                    height: int = 32,
                    root_widget: customtkinter.CTk,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.root_widget = root_widget
        self.bind("<Button-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag)
        

    def on_drag_start(self, event):
        if dnd.dnd_start(self, event):
            self.lift()
        self._drag_start_x = self.winfo_pointerx()
        self._drag_start_y = self.winfo_pointery()
        print(f"{self.winfo_rootx()}, {self.winfo_rootx()}")
            
    def on_drag(self, event):
        dx = self.winfo_pointerx() - self._drag_start_x
        dy = self.winfo_pointery() - self._drag_start_y
        x = self.winfo_x() + dx
        y = self.winfo_y() + dy
        self.place(x=x, y=y)
        print(f"({x}, {y}): ({dx}, {dy})")
        self._drag_start_x, self._drag_start_y = self.winfo_pointerxy()
    def dnd_end(self, target, event):
        pass

def main():
    root = customtkinter.CTk()
    root.geometry("900x650")
    label = DragableLabel(master = root, text="Label!", root_widget=root)
    label.pack()
    root.mainloop()

if __name__ == "__main__":
    main()