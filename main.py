import customtkinter
import recipe_handler
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from sqlalchemy import select
from recipe_handler import Units
from widgets import AdvancedTableWidget, AdvancedTableWidgetFactory, DragableLabel
from context_handler import GuiContextHandler
from context_handler import GuiContext
from tkinter import dnd
import CTkToolTip as tooltips


context_handler = GuiContextHandler()

class RecipeListFrame (customtkinter.CTkFrame):
    recipe_frame_headers = ["Recipe Name", "Recipe Desc"]
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.master = master
        self.labels = []
        self.recipes = session.scalars(select(recipe_handler.Recipe).order_by(recipe_handler.Recipe.name)).all()
        recipe_table_data = []
        self.__recipe_association_table = {}
        for i, recipe in enumerate(self.recipes):
            recipe_data = [recipe.name]
            recipe_table_data.append(recipe_data)
            self.__recipe_association_table[i] = recipe
        table_widget_factory = AdvancedTableWidgetFactory()
        table_widget_factory.register_default_label(0)
        self.recipe_table_wig = AdvancedTableWidget(self, table_data=recipe_table_data, label_text="Recipes", highlight_row_wrapper=self.highlight_recipe, row_class_list=self.recipes, widget_factory=table_widget_factory)
        self.recipe_table_wig.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        self.rowconfigure(0,weight=1)
    def highlight_recipe(self, table_widget:AdvancedTableWidget.AdvancedRow, row):
        recipe_changed_to = None
        if table_widget.highlighted:
            recipe_changed_to = self.__recipe_association_table[row]
            context_handler.notify(self.master, GuiContext.inspect_recipe, recipe=recipe_changed_to)
        else:
            context_handler.notify(self.master, GuiContext.inspect_recipe, recipe=recipe_changed_to)

class IngredientListFrame (customtkinter.CTkFrame):
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.master = master
        self.labels = []
        self.ingredients: list[recipe_handler.Ingredient] = session.scalars(select(recipe_handler.Ingredient).order_by(recipe_handler.Ingredient.name)).all()
        widget_factory = AdvancedTableWidgetFactory()
        def create_selectable_label_widget(master) -> (DragableLabel, customtkinter.StringVar):
            data_var = customtkinter.StringVar(master=master,value="None")
            entry = customtkinter.CTkLabel(master=master, textvariable=data_var)
            return entry, data_var
        widget_factory.register_widget_function(0, create_selectable_label_widget, True)
        
        ingredient_table_data = []
        ingredient_table_header = ["Ingredients"]
        ingredient_tooltip_data = {}
        for ingredient in self.ingredients:
            row = [ingredient.name]
            ingredient_table_data.append(row)
            tooltip = ingredient.desc
            ingredient_tooltip_data[tuple(row)] = [tooltip]
        self.recipe_ingredients_list_element = AdvancedTableWidget(self, table_data=ingredient_table_data, table_tooltips=ingredient_tooltip_data,table_headers=ingredient_table_header, row_class_list=self.ingredients, widget_factory=widget_factory, highlight_row_wrapper=self.highlight_ingredient)
        self.recipe_ingredients_list_element.grid(row=0,column=0, sticky="ew", columnspan=2)
        self.rowconfigure(0,weight=1)
    def highlight_ingredient(self, row_widget:AdvancedTableWidget.AdvancedRow, row):
        context_handler.notify(self.master, GuiContext.edit_recipe, ingredient=row_widget.class_obj)

#### Recipe Selector Frame
class RecipeInspectionFrame (customtkinter.CTkFrame):
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.master = master
        self.session = session
        self.selected_recipe: recipe_handler.Recipe = None
        self.visible = True
        context_handler.add_listener(self.gui_context_update)
        self.gui_string_recipe_name = customtkinter.StringVar(self)
        self.gui_string_recipe_name.set("No Recipe")
        self.gui_string_recipe_add_button = customtkinter.StringVar(self)
        self.gui_string_recipe_add_button.set("Edit")
        recipe_name_label = customtkinter.CTkLabel(self, textvariable=self.gui_string_recipe_name)
        recipe_name_label.grid(row=0, column=0, sticky="nw")
        self.recipe_add_ingredient = customtkinter.CTkButton(self, textvariable=self.gui_string_recipe_add_button, command=self.begin_recipe_edit)
        self.recipe_add_ingredient.grid(row = 0, column = 1, sticky="nw")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.ingredient_table_widget = self.create_ingredient_table()
    def reveal_frame(self):
        self.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.visible = True
    def destroy_frame(self):
        self.grid_remove()
        self.visible = False
    def update_elements_with_recipe(self, recipe: recipe_handler.Recipe):
        self.gui_string_recipe_name.set(recipe.name)
    def create_ingredient_table(self)-> AdvancedTableWidget:
        widget_factory = self.define_default_widget_factory()
        ingredient_table_data = []
        ingredient_table_header = ["Ingredient", "Amount", "Unit"]
        recipe_ingredients_list_element = AdvancedTableWidget(self, table_data=ingredient_table_data, table_headers=ingredient_table_header, widget_factory=widget_factory)
        recipe_ingredients_list_element.grid(row=1,column=0, sticky="ew", columnspan=2)
        return recipe_ingredients_list_element
    def update_ingredient_table(self):
        ingredient_table_data = []
        for ingredient in self.selected_recipe.ingredients_list:
            row = [ingredient.ingrd.name, ingredient.amount, ingredient.unit]
            ingredient_table_data.append(row)
        self.ingredient_table_widget.update_table(ingredient_table_data, self.selected_recipe.ingredients_list)
    def gui_context_update(self, frame, context:GuiContextHandler.Context, recipe=None, ingredient=None, *args, **kwargs):
        if context.is_different():
            if context.context_to == GuiContext.edit_recipe and frame == self.master:
                self.update_save_button_state("Save")
                self.create_editable_ingredient_list()
        else:
            if context.context_to == GuiContext.inspect_recipe and frame == self.master:
                self.ingredient_table_widget.bind_widget_factory(self.define_default_widget_factory())
                self.update_selected_recipe(recipe)
                self.update_save_button_state("Edit")
            if context.context_to == GuiContext.edit_recipe and frame == self.master and ingredient:
                self.update_indgredient_editing_table(ingredient)
    def update_save_button_state(self, state):
        if state =="Edit":
            self.gui_string_recipe_add_button.set("Edit")
            self.recipe_add_ingredient.configure(command=self.begin_recipe_edit)
        if state == "Save":
            self.gui_string_recipe_add_button.set("Save")
            self.recipe_add_ingredient.configure(command=self.add_ingredient_to_recipe)
    def update_selected_recipe(self, recipe):
        if recipe:
            if not self.visible:
                self.reveal_frame()
            self.selected_recipe = recipe
            self.update_elements_with_recipe(recipe)
            self.update_ingredient_table()
        else:
            self.selected_recipe = None
            self.destroy_frame()
    def update_indgredient_editing_table(self, ingredient):
        for row in self.ingredient_table_widget.rows:
            cell = row.cell_widgets[0]
            cell.configure(bg_color="purple")
            cell.tooltip = tooltips.CTkToolTip(cell, message="Click to replace ingredient with selected ingredient")
            cell.bind(lambda ingredient=ingredient, row=row: self.edit_ingredient_in_row(ingredient, row))
    def edit_ingredient_in_row(self, ingredient:recipe_handler.Ingredient, row:AdvancedTableWidget.AdvancedRow):
        recipe_component: recipe_handler.RecipeComponent = row.class_obj
        recipe_component.ingrd = ingredient
        self.update_ingredient_table()
    def begin_recipe_edit(self):
        context_handler.notify(self.master, GuiContext.edit_recipe, recipe=self.selected_recipe)
    def define_default_widget_factory(self):
        widget_factory = AdvancedTableWidgetFactory()
        widget_factory.register_default_label(0)
        widget_factory.register_default_label(1)
        widget_factory.register_default_label(2)
        return widget_factory
    def create_editable_ingredient_list(self):
        widget_factory = AdvancedTableWidgetFactory()
        def create_dnd_target_widget(master) -> (customtkinter.CTkEntry, customtkinter.StringVar):
            data_var = customtkinter.StringVar(master=master,value="None")
            target_widget = customtkinter.CTkButton(master=master, textvariable=data_var)
            def row_widget_dnd_accept(self, source, event):
                print("targeted by dnd")
                return self
            master.dnd_accept = row_widget_dnd_accept
            return target_widget, data_var
        widget_factory.register_widget_function(0, create_dnd_target_widget, False)
        def create_entry_widget(master) -> (customtkinter.CTkEntry, customtkinter.StringVar):
            data_var = customtkinter.StringVar(master=master,value="None")
            entry = customtkinter.CTkEntry(master=master, textvariable=data_var)
            return entry, data_var
        widget_factory.register_widget_function(1, create_entry_widget, False)
        def create_dropdown_widget(master) -> (customtkinter.CTkComboBox, customtkinter.StringVar): 
            data_var = customtkinter.StringVar(master=master, value="None")
            combo_box = customtkinter.CTkComboBox(master=master, values=[e.name for e in Units], variable=data_var)
            return combo_box, data_var
        widget_factory.register_widget_function(2, create_dropdown_widget, False)
        ingredient_table_data = []
        for ingredient in self.selected_recipe.ingredients_list:
            row = [ingredient.ingrd.name, ingredient.amount, ingredient.unit]
            ingredient_table_data.append(row)
        self.ingredient_table_widget.bind_widget_factory(widget_factory)
        self.ingredient_table_widget.update_table(ingredient_table_data, self.selected_recipe.ingredients_list)

    def add_ingredient_to_recipe(self):
        for i, row in enumerate(self.ingredient_table_widget.rows):
            recipe_component: recipe_handler.RecipeComponent
            recipe_component = row.class_obj
            print(f"{recipe_component}, change to amount {row.data_vars[1].get()}, change unit to {Units[row.data_vars[2].get()]}")
            try:
                recipe_component.amount = float(row.data_vars[1].get())
            except:
                print("Unable to Save")
                return
            recipe_component.unit = Units[row.data_vars[2].get()]
        context_handler.notify(self.master, GuiContext.inspect_recipe, self.selected_recipe)
        self.session.commit()
class RecipeEditorWindow (customtkinter.CTkFrame):
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.session = session
        self.side_selection_frame = RecipeListFrame(self, self.session)
        self.side_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        self.side_ingredient_frame = IngredientListFrame(self, self.session)
        self.main_inspection_window = RecipeInspectionFrame(self, self.session)
        self.main_inspection_window.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        context_handler.add_listener(self.gui_context_update)
        context_handler.notify(self, GuiContext.inspect_recipe)
    def gui_context_update(self, frame, context:GuiContextHandler.Context, *args, **kwargs):
        if context.context_to == GuiContext.edit_recipe and context.is_different() and frame == self:
            self.side_selection_frame.grid_remove()
            self.side_ingredient_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        if context.context_to == GuiContext.inspect_recipe and context.is_different() and frame == self:
            self.side_ingredient_frame.grid_remove()
            self.side_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
class App (customtkinter.CTk):
    """Main app body

    Args:
        customtkinter (_type_): _description_
    """
    def __init__(self, session: orm.Session):
        super().__init__()
        self.title("Recipe Tool")
        self.geometry("400x150")
        self.session = session
        self.recipe_editor_window = RecipeEditorWindow(self, session=session)
        self.recipe_editor_window.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.state("zoomed")

__Ingredient_Database = 'sqlite:///recipe_manager/database/ingredient_db.db'
engine = sqla.create_engine(__Ingredient_Database, echo=True)
recipe_handler.Base.metadata.create_all(bind=engine)
Session = orm.sessionmaker(engine)
with Session() as session:
    app = App(session)
    context_handler.define_app(app)
    app.mainloop()