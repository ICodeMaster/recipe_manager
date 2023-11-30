
import customtkinter
from enum import Enum

class GuiContext(Enum):
    empty = 0
    select_recipe = 1
    select_ingredient = 2
    inspect_recipe = 3
    edit_recipe = 4

class GuiContextHandler(object):
    def __init__(self) -> None:
        self.App: customtkinter.CTk
        self.frames: list[customtkinter.CTkFrame]
        self.contexts: dict[customtkinter.CTkFrame, GuiContext]
        self._listeners = []
        pass
    def define_app(self, app:customtkinter.CTk):
        self.App = app
    def register_frame(self, frame:customtkinter.CTkFrame):
        self.frames.append(frame)
    def switch_context (self, context: GuiContext, frame:customtkinter.CTkFrame):
        self.contexts[frame] = context
    def add_listener(self, listener):
        self._listeners.append(listener)
    def __iadd__(self, listener):
        self.add_listener(listener)
        return self
    def on(self, frame:customtkinter.CTkFrame, context: GuiContext, *args, **kwargs):
        for listener in self._listeners:
            listener(frame, context, *args, **kwargs)
    def notify(self, frame:customtkinter.CTkFrame, context: GuiContext, *args, **kwargs):
        self.on(frame, context, *args, **kwargs)
