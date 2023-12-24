
import customtkinter
from enum import Enum

class GuiContext(Enum):
    empty = 0
    select_recipe = 1
    select_ingredient = 2
    inspect_recipe = 3
    edit_recipe = 4

    def __str__(self) -> str:
        return str(self.name)

class GuiContextHandler(object):

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(GuiContextHandler, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance
    class Context(object):
        def __init__(self, context_to, context_from, frame) -> None:
            self.context_to = context_to
            self.context_from = context_from
            self.frame = frame
        def is_different(self):
            if self.context_to != self.context_from:
                return True
            else:
                return False
        def __str__(self) -> str:
            return str(f"(to: {self.context_to}, from: {self.context_from})")
    def __init__(self) -> None:
        self.app = None
        self.frames: list[customtkinter.CTkFrame]
        self.contexts: dict[customtkinter.CTkFrame, GuiContext] = {}
        self._listeners = []
    def define_app(self, app):
        self.app = app
    def __switch_context (self, context: GuiContext, frame:customtkinter.CTkFrame):
        context_from = self.contexts.get(frame)
        context_to = context
        self.contexts[frame] = context
        context_obj = self.Context(context_to, context_from, frame)
        return context_obj
    def remove_context_frame(self, frame):
        try:
            self.notify(frame, GuiContext.empty)
            del self.contexts[frame]
        #### Try to remove context from frame
        except KeyError:
            pass
    def add_listener(self, listener):
        self._listeners.append(listener)
    def remove_listener(self, listener):
        try:
            self._listeners.remove(listener)
        except KeyError:
            pass
    def __iadd__(self, listener):
        self.add_listener(listener)
        return self
    def on(self, frame:customtkinter.CTkFrame, context: GuiContext, *args, **kwargs):
        context_obj = self.__switch_context(context, frame)
        print(f"Switching Context: {frame} frame, {context_obj}")
        for listener in self._listeners:
            listener(frame, context_obj, *args, **kwargs)
    def notify(self, frame:customtkinter.CTkFrame, context: GuiContext, *args, **kwargs):
        self.on(frame, context, *args, **kwargs)



