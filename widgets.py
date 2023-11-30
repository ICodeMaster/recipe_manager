import customtkinter

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
class TableWidget(customtkinter.CTkScrollableFrame):
    def __init__(self, *args,
                    width: int = 150,
                    height: int = 32,
                    table_data: list[list[str]],
                    table_headers: list[str] = None,
                    highlight_row_wrapper = None,
                    row_elements: list[object] = None,
                    row_class_list: list[object] = None,
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