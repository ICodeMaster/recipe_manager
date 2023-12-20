import customtkinter
import recipe_handler
import sqlalchemy as sqla
import sqlalchemy.orm as orm
from sqlalchemy import select
from context_handler import GuiContextHandler
from recipe_editor import RecipeEditorWindow

context_handler = GuiContextHandler()

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