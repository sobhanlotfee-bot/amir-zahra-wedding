
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse

Window.clearcolor = (0, 0, 0, 1)


class CircleButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(1, 0.38, 0.16, 1)
            self.circle = Ellipse()

        self.bind(pos=self.update_circle,
                  size=self.update_circle)

    def update_circle(self, *args):
        diameter = min(self.width, self.height) * 0.82

        self.circle.size = (diameter, diameter)

        self.circle.pos = (
            self.center_x - diameter / 2,
            self.center_y - diameter / 2
        )


class MyApp(App):

    def build(self):
        self.expression = ""

        main = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=5
        )

        self.display = Label(
            text="0",
            font_name="Roboto",
            font_size=95,
            color=(0.95, 0.95, 0.97, 1),
            halign="right",
            valign="bottom",
            size_hint_y=0.5
        )

        self.display.bind(
            size=self.display.setter("text_size")
        )

        main.add_widget(self.display)

        layout = GridLayout(
            cols=4,
            rows=5,
            spacing=0,
            padding=0,
            size_hint_y=0.5
        )

        buttons = [
            "AC", "⌫", "%", "÷",
            "7", "8", "9", "×",
            "4", "5", "6", "−",
            "1", "2", "3", "+",
            "±", "00", "0", "="
        ]

        symbols = [
            "AC", "⌫", "%", "÷",
            "×", "−", "+", "±"
        ]

        for item in buttons:

            if item == "=":
                btn = CircleButton(
                    text=item,
                    font_name="Roboto",
                    font_size=56,
                    bold=True,
                    color=(1, 1, 1, 1),
                    background_normal="",
                    background_color=(0, 0, 0, 0)
                )

            else:
                if item in symbols:
                    color = (1, 0.38, 0.16, 1)
                    size = 48
                else:
                    color = (0.94, 0.94, 0.96, 1)
                    size = 56

                btn = Button(
                    text=item,
                    font_name="Roboto",
                    font_size=size,
                    bold=True,
                    background_normal="",
                    background_color=(0, 0, 0, 0),
                    color=color
                )

            btn.bind(on_press=self.click)
            layout.add_widget(btn)

        main.add_widget(layout)
        return main

    def click(self, instance):
        import re
        value = instance.text

        if value == "AC":
            self.expression = ""
            self.display.text = "0"
            return

        elif value == "⌫":
            self.expression = self.expression[:-1]

        elif value == "=":
            try:
                result = eval(self.expression)
                self.display.text = str(result)
                self.expression = str(result)
            except:
                self.display.text = "Error"
            return

        elif value == "±":
            match = re.search(
                r'(\d+\.?\d*)$', self.expression
            )

            if match:
                number = match.group(1)
                start = match.start()
                before = self.expression[:start]

                if before.endswith("-"):
                    before = before[:-1]
                else:
                    before += "-"

                self.expression = before + number

        elif value == "%":
            self.expression += "/100"

        else:
            operations = {
                "×": "*",
                "÷": "/",
                "−": "-"
            }

            self.expression += operations.get(value, value)

        if not self.expression:
            self.display.text = "0"
            return

        try:
            result = eval(self.expression)
            self.display.text = str(result)
        except:
            self.display.text = self.expression


MyApp().run()
