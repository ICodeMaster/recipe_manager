from __future__ import annotations
import recipe_handler

import sqlalchemy as sqla
import sqlalchemy.orm as orm
from recipe_handler import Units


__Ingredient_Database = 'sqlite:///database/ingredient_db.db'
engine = sqla.create_engine(__Ingredient_Database, echo=True)
recipe_handler.Base.metadata.create_all(bind=engine)
Session = orm.sessionmaker(engine)
with Session() as session:
    apple = recipe_handler.Ingredient(name="apple", desc="an apple")
    apple.set_cost(30, 10, Units.lbs)
    pear = recipe_handler.Ingredient(name = "pear", desc="a pear")
    pear.set_cost(15.0, 10.0, Units.kgs)
    session.add(pear)
    session.add(apple)
    apple_pear = recipe_handler.Recipe("apple, pear", [apple.to_recipe_component(3, Units.kgs, session), pear.to_recipe_component(5, Units.kgs, session)])
    apple_pear.add_indgredient(apple.to_recipe_component(30, Units.oz, session))
    session.add(apple_pear)
    session.commit()
    print(apple)

