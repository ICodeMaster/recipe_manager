import customtkinter
import recipe_handler
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from sqlalchemy import select
from recipe_handler import Units
from widgets import TableRowWidget, TableWidget
from context_handler import GuiContextHandler
from context_handler import GuiContext
from tkinter import dnd

context_handler = GuiContextHandler()

class RecipeListFrame (customtkinter.CTkFrame):
    recipe_frame_headers = ["Recipe Name", "Recipe Desc"]
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.master = master
        self.labels = []
        self.recipes = []
        self.recipes = session.scalars(select(recipe_handler.Recipe).order_by(recipe_handler.Recipe.name)).all()
        recipe_table_data = []
        self.__recipe_association_table = {}
        for i, recipe in enumerate(self.recipes):
            recipe_data = [recipe.name]
            recipe_table_data.append(recipe_data)
            self.__recipe_association_table[i] = recipe
        self.recipe_table_wig = TableWidget(self, table_data=recipe_table_data, label_text="Recipes", highlight_row_wrapper=self.highlight_recipe, row_class_list=self.recipes)
        self.recipe_table_wig.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        self.rowconfigure(0,weight=1)
    def highlight_recipe(self, table_widget:TableRowWidget, row):
        recipe_changed_to = None
        if table_widget.highlighted:
            recipe_changed_to = self.__recipe_association_table[row]
            context_handler.notify(self, GuiContext.inspect_recipe, recipe=recipe_changed_to)
        else:
            context_handler.notify(self, GuiContext.inspect_recipe, recipe=recipe_changed_to)
    def get_selected_recipe(self):
        pass

class RecipeIngredientEntry (customtkinter.CTkFrame):
    def __init__(self, master: 'RecipeInspectionFrame'):
        super().__init__(master)
        self.master = master
        self.entry_ingredient_name = customtkinter.CTkEntry(self)
        self.entry_ingredient_amount = customtkinter.CTkEntry(self)
        self.entry_ingredient_unit = customtkinter.CTkEntry(self)
        self.entry_ingredient_name.grid(row=0, column=0, sticky="ew")
        self.entry_ingredient_amount.grid(row=0, column=1, sticky="ew")
        self.entry_ingredient_unit.grid(row=0, column=2, sticky="ew")
        for column_num in range(self.grid_size()[0]):
            self.columnconfigure(column_num, weight=1)
#### Recipe Selector Frame
class RecipeInspectionFrame (customtkinter.CTkFrame):
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.session = session
        self.selected_recipe: recipe_handler.Recipe = None
        self.visible = True
        context_handler.add_listener(self.gui_context_update)
        self.recipe_ingredients_list_element = self.recipe_ingredients_list_element = TableWidget(self, table_data=[], table_headers=[])
        self.gui_string_recipe_name = customtkinter.StringVar(self)
        self.gui_string_recipe_name.set("No Recipe")
        self.gui_string_recipe_add_button = customtkinter.StringVar(self)
        self.gui_string_recipe_add_button.set("Edit")
        recipe_name_label = customtkinter.CTkLabel(self, textvariable=self.gui_string_recipe_name)
        recipe_name_label.grid(row=0, column=0, sticky="nw")
        self.recipe_add_ingredient = customtkinter.CTkButton(self, textvariable=self.gui_string_recipe_add_button, command=self.start_add_ingredient)
        self.recipe_add_ingredient.grid(row = 0, column = 1, sticky="nw")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
    def reveal_frame(self):
        self.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.visible = True
    def destroy_frame(self):
        self.grid_remove()
        self.visible = False
    def update_elements_with_recipe(self, recipe: recipe_handler.Recipe):
        self.gui_string_recipe_name.set(recipe.name)
    def update_ingredient_table(self):
        try:
            self.recipe_ingredients_list_element.grid_forget()
        except:
            pass
        ingredient_table_data = []
        ingredient_table_header = ["Ingredient", "Amount", "Unit"]
        for ingredient in self.selected_recipe.ingredients_list:
            row = [ingredient.ingrd.name, ingredient.amount, ingredient.unit]
            ingredient_table_data.append(row)
        self.recipe_ingredients_list_element = TableWidget(self, table_data=ingredient_table_data, table_headers=ingredient_table_header, row_class_list=self.selected_recipe.ingredients_list)
        self.recipe_ingredients_list_element.grid(row=1,column=0, sticky="ew", columnspan=2)
    def gui_context_update(self, frame, context, recipe, *args, **kwargs):
        if context == GuiContext.inspect_recipe:
            if recipe is not self.selected_recipe:
                self.update_selected_recipe(recipe)
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
    def start_add_ingredient(self):
        recipe_ingredient_entry = RecipeIngredientEntry(self)
        recipe_ingredient_entry.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.recipe_ingredients_list_element.grid(row=2)
        self.gui_string_recipe_add_button.set("Save")
        self.recipe_add_ingredient.configure(command=lambda :self.add_ingredient_to_recipe(recipe_ingredient_entry))
    def add_ingredient_to_recipe(self, entry_text:RecipeIngredientEntry):
        result = self.session.execute(select(recipe_handler.Ingredient).where(recipe_handler.Ingredient.name == entry_text.entry_ingredient_name.get()))
        unit = Units[entry_text.entry_ingredient_unit.get().lower()]
        component = recipe_handler.RecipeComponent(result.scalar(), entry_text.entry_ingredient_amount.get(), unit)
        self.selected_recipe.add_indgredient(component)
        print(f'added ingredient:{component}')
        self.session.commit()
        self.update_ingredient_table()
class RecipeEditorWindow (customtkinter.CTkFrame):
    def __init__(self, master: any, session:orm.Session):
        super().__init__(master)
        self.session = session
        self.side_selection_frame = RecipeListFrame(self, self.session)
        self.side_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        self.main_inspection_window = RecipeInspectionFrame(self, self.session)
        self.main_inspection_window.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
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

__Ingredient_Database = 'sqlite:///database/ingredient_db.db'
engine = sqla.create_engine(__Ingredient_Database, echo=True)
recipe_handler.Base.metadata.create_all(bind=engine)
Session = orm.sessionmaker(engine)
with Session() as session:
    app = App(session)
    context_handler.define_app(app)
    app.mainloop()