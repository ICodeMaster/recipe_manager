import customtkinter
import copy

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
        self.highlight_element_dict = {}
        self.master = None
    def register_widget_function(self, index, widget_func, highlightable=True):
        self.row_elemenet_dict[index] = widget_func
        self.highlight_element_dict[index] = highlightable
    def register_master(self, master):
        self.master = master
    def create_widget(self, index, master=None) -> (customtkinter.CTkBaseClass, customtkinter.StringVar):
        if master:
            widget_master = master
        else:
            widget_master = self.master
        widget, widget_data = self.row_elemenet_dict[index](master=widget_master)
        widget.is_highlightable = self.highlight_element_dict[index]
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
                    table_headers: list[str] = None,
                    highlight_row_wrapper = None,
                    row_class_list: list[object] = None,
                    widget_factory: AdvancedTableWidgetFactory,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(fg_color=("gray78", "gray21"))  # set frame color
        self.table_data = table_data
        ### Create empty array list until custom array added.
        self.__table_variables = [([None]*len(table_data[0])) for i in table_data]
        self.headers = table_headers
        self.highlight_row_wrapper = highlight_row_wrapper
        self.rows: list[TableRowWidget] = []
        self.highlighted_recipe = None
        self.widget_factory = widget_factory
        self.widget_factory.register_master(self)
        self.row_class_list = row_class_list
        header_offset = 0
        header_columns = 1
        self.columns = 0
        if self.headers is not None:
            header_offset += 1
            header_columns = 0
            for j, header in enumerate(self.headers):
                header_label = customtkinter.CTkLabel(self, text=header, fg_color="gray30", corner_radius=6)
                header_label.grid(row=0, column=j, padx=10, pady=10, sticky="ew")
                header_columns += 1
        ### Add this as a function
        for row in table_data:
            self.add_table_row(row)
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
    def remove_row(self, row:int):
        row_frame = self.rows.pop(row)
        row_frame.grid_forget()
    def highlight_row(self, e, row_element: TableRowWidget, row):
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
    def add_table_row(self, index, row_data):
        table_row_widget = TableRowWidget(self)
        table_row_widget.grid(row_data = index+header_offset,column=0, padx=10,pady=5, sticky="ew", columnspan=(header_columns))
        table_row_widget.bind("<Button-1>", lambda e, row_element=table_row_widget, row=index: self.highlight_row(e, row_element=row_element, row=row))
        self.rows.append(table_row_widget)
        table_row_widget.data = row_data
        try:
            table_row_widget.class_obj = self.row_class_list[index]
        except (IndexError, TypeError):
            pass
        columns = row_data.__len__()
        for j, text in enumerate(row_data):
            cell, data_var = self.widget_factory.create_widget(j, master=table_row_widget)
            table_row_widget.data_vars.append(data_var)
            data_var.set(text)
            cell.grid(row=0, column=j, padx=5, pady=0, sticky="ew")
            if cell.is_highlightable:
                cell.bind("<Button-1>", lambda e, row_element=table_row_widget, row=index: self.highlight_row(e, row_element=row_element, row=row))
        if columns > self.columns:
            self.columns = columns
        for column_num in range(table_row_widget.grid_size()[0]):
            table_row_widget.columnconfigure(column_num, weight=1)
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
class TableWidget(customtkinter.CTkScrollableFrame):
    def __init__(self, *args,
                    width: int = 150,
                    height: int = 32,
                    table_data: list[list[str]],
                    table_headers: list[str] = None,
                    highlight_row_wrapper = None,
                    row_elements: list[object] = None,
                    row_class_list: list[object] = None,
                    highlightable: bool = True,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(fg_color=("gray78", "gray21"))  # set frame color
        self.table_data = table_data
        ### Create empty array list until custom array added.
        self.__table_variables = [([None]*len(table_data[0])) for i in table_data]
        self.headers = table_headers
        self.highlight_row_wrapper = highlight_row_wrapper
        self.rows: list[TableRowWidget] = []
        self.highlighted_recipe = None
        header_offset = 0
        header_columns = 1
        self.columns = 0
        if self.headers is not None:
            header_offset += 1
            header_columns = 0
            for j, header in enumerate(self.headers):
                header_label = customtkinter.CTkLabel(self, text=header, fg_color="gray30", corner_radius=6)
                header_label.grid(row=0, column=j, padx=10, pady=10, sticky="ew")
                header_columns += 1
        for i, row in enumerate(table_data):
            table_row_widget = TableRowWidget(self)
            table_row_widget.grid(row = i+header_offset,column=0, padx=10,pady=5, sticky="ew", columnspan=(header_columns))
            table_row_widget.bind("<Button-1>", lambda e, row_element=table_row_widget, row=i: self.highlight_row(e, row_element=row_element, row=row))
            self.rows.append(table_row_widget)
            table_row_widget.data = row
            try:
                table_row_widget.class_obj = row_class_list[i]
            except (IndexError, TypeError):
                pass
            columns = row.__len__()
            for j, text in enumerate(row):
                cell_data = customtkinter.StringVar(table_row_widget, value=text)
                self.__table_variables[i][j] = cell_data
                cell_label: customtkinter.CTkLabel
                try:
                    cell_label = row_elements[j](master=table_row_widget, textvariable=cell_data)
                except TypeError:
                    cell_label = customtkinter.CTkLabel(master=table_row_widget, textvariable=cell_data)
                cell_label.grid(row=0, column=j, padx=5, pady=0, sticky="ew")
                if highlightable:
                    cell_label.bind("<Button-1>", lambda e, row_element=table_row_widget, row=i: self.highlight_row(e, row_element=row_element, row=row))
            if columns > self.columns:
                self.columns = columns
            for column_num in range(table_row_widget.grid_size()[0]):
                table_row_widget.columnconfigure(column_num, weight=1)
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
    def remove_row(self, row:int):
        row_frame = self.rows.pop(row)
        row_frame.grid_forget()
    def highlight_row(self, e, row_element: TableRowWidget, row):
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
    def return_table_variables(self):
        return self.__table_variables
class DragableLabel(customtkinter.CTkLabel):

    targets: dict[customtkinter.CTkLabel] = {}
    def __init__(self, *args,
                    width: int = 150,
                    height: int = 32,
                    **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.bind("<Button-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag)

    def on_drag_start(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    def on_drag(self, event):
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
    @classmethod
    def register_drag_target(cls, target, func):
        cls.targets[target] = func