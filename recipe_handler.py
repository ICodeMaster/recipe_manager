from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from typing import List
import sqlalchemy as sqla
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship, composite
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

class Units(Enum):
    kgs  = 1
    lbs = 2
    g = 3
    oz = 4
    floz = 5
    tbsp = 6
    tsp = 7
    gal = 8
    #### Do some conversion math here in the enum
    
    def __str__(self) -> str:
        return str(self.name)

class CostComponent(object):

    def __init__(self, cost_per_unit:float, cost_unit:Units) -> None:
        self.cost_per_unit = cost_per_unit
        self.cost_unit = cost_unit

    def __composite_values__(self):
        return self.cost_per_unit, self.cost_unit
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, CostComponent) and __o.cost_per_unit == self.cost_per_unit
    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

class Ingredient(Base):
    __tablename__ = "ingredients_table"
    id: Mapped[int] = mapped_column( primary_key=True)
    name: Mapped[str]
    desc: Mapped[Optional[str]]
    type: Mapped[str]
    cost_per_unit: Mapped[float] = mapped_column(sqla.Float())
    cost_unit: Mapped[Units] = mapped_column(sqla.Enum(Units))

    cost = composite(CostComponent, cost_per_unit, cost_unit)

    __mapper_args__ = {
        "polymorphic_identity": "ingredient",
        "polymorphic_on": "type",
    }

    def __init__(self, name:str, desc:str=None):
        self.name = name
        self.desc = desc
        self.cost = CostComponent(0, "g")
    def __repr__(self) -> str:
        return f"ingr:({self.name})"
    def to_recipe_component(self, amount, unit, session):
        component = RecipeComponent(self, amount, unit)
        session.add(component)
        return component


    def set_cost(self, cost:float, unit_size:float, unit:Units):
        cost_per_unit = cost/unit_size
        self.cost = CostComponent(cost_per_unit, unit)

class Recipe(Ingredient):
    __tablename__ = "recipes_table"
    id = mapped_column(ForeignKey("ingredients_table.id"), primary_key=True)
    recipeName: Mapped[Optional[str]]
    ingredients_list = relationship("RecipeComponent", back_populates="recipe")

    __mapper_args__ = {
        "polymorphic_identity": "recipe",
    }
    def __init__(self, name:str, ingredients_list:list[RecipeComponent]=None ):
        super().__init__(name)
        self.ingredients_list = ingredients_list
    def add_indgredient(self, ingrd:RecipeComponent):
        """add ingredient to a recipe

        Args:
            ingredient (Ingredient): ingredient or recipe class
            amount (float): amount in grams
        """
        self.ingredients_list.append(ingrd)
    def remove_ingredient(self, ingrd:RecipeComponent):
        self.ingredients_list.remove(ingrd)

class RecipeComponent(Base):
    __tablename__ = "recipe_components_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    ingrd_id: Mapped[int] = mapped_column(ForeignKey("ingredients_table.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes_table.id"))
    amount: Mapped[float]
    unit: Mapped[Units] = mapped_column(sqla.Enum(Units))

    ingrd = relationship("Ingredient",foreign_keys=[ingrd_id])
    recipe = relationship("Recipe", back_populates="ingredients_list", foreign_keys=[recipe_id])
    def __init__(self, ingrd:Ingredient, amount:float, unit:Units):
        self.ingrd = ingrd
        self.amount = amount
        self.unit = unit
    def __repr__(self) -> str:
        return f"ingr:({self.ingrd}, amount: {self.amount}, unit :{self.unit.name})"