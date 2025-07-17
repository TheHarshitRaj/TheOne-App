from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast
from kivymd.uix.snackbar import MDSnackbar
from kivy.core.clipboard import Clipboard
from random import randint, choice
from datetime import datetime
import requests
import os
import webbrowser

Window.size = (300,500)

class HomeScreen(Screen):
    pass

class ProductivityScreen(Screen):
    def get_file_path(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_name = "Tasks List"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return os.path.join(folder_name, f"{date_str}.txt")

    def saveTasksToFile(self):
        file_path = self.get_file_path()
        tasks = []
        for item in self.ids.tasks_list.children[::-1]:  # reversed to preserve order
            if isinstance(item, OneLineAvatarIconListItem):
                tasks.append(item.text.strip())

        with open(file_path, 'w') as f:
            f.write('\n'.join(tasks))

    def loadTasksFromFile(self):
        file_path = self.get_file_path()
        self.ids.tasks_list.clear_widgets()

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                self.addTask(line.strip())

    def createTask(self):
        self.task_input = MDTextField(
        hint_text="Enter task",
        mode="rectangle",
        size_hint_x=1
        )

        self.dialog= MDDialog(
            title='Add new Task',
            type='custom',
            content_cls=self.task_input,
            buttons=[
                MDFlatButton(
                    text='Close',
                    on_release=lambda x: self.dialog.dismiss()
                    ),
                MDFlatButton(
                    text='Add',
                    on_release= lambda x: (
                        self.addTask(self.task_input.text),
                        self.dialog.dismiss()
                    )
                )
            ]
        )
        self.dialog.open()

    def addTask(self, text):
        item = OneLineAvatarIconListItem(text=text)
        item._no_ripple_effect= True
        checkbox = MDCheckbox(size_hint=(None, None), size=("32dp", "32dp"), pos_hint={'center_y':0.5})
        delete_btn = IconRightWidget(icon='delete')
        delete_btn.on_release = lambda *args: (self.ids.tasks_list.remove_widget(item), self.saveTasksToFile())
        item.add_widget(checkbox)
        item.add_widget(delete_btn)
        self.ids.tasks_list.add_widget(item)
        self.saveTasksToFile()
    
    def on_enter(self):
        self.loadTasksFromFile()

class ExtrasScreen(Screen):
    pass

class SettingsScreen(Screen):
    def on_kv_post(self, base_widget):
        self.ids.panel_container.add_widget(
            MDExpansionPanel(
                icon="tools",
                content=GeneralSettings(),
                panel_cls=MDExpansionPanelOneLine(text="General", font_style='H6')
            )
        )
        self.ids.panel_container.add_widget(
            MDExpansionPanel(
                icon="information",
                content=About(),
                panel_cls=MDExpansionPanelOneLine(text="About Us", font_style='H6')
            )
        )


class QuickNoteScreen(Screen):
    def cleartext(self):
        self.ids.quick_note_field.text = ''

    def copyText(self):
        Clipboard.copy(self.ids.quick_note_field.text)
    
    def saveContent(self):      # Currently only for Desktop
        folder_name = "Quick Notes"
        file_name = f"note_{datetime.now().strftime('%Y-%m-%d_%H%M')}.txt"
        
        # Create folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Full path to file
        file_path = os.path.join(folder_name, file_name)

        content = self.ids.quick_note_field.text
        with open(file_path, 'w') as f:
            f.write(content)
        
        MDSnackbar(
            MDLabel(text='File Saved')
        ).open()

class RandomNumScreen(Screen):
    randomNum= NumericProperty()

    def RandomNumGen(self, rangeStart, rangeEnd):
        if rangeStart and rangeEnd:

            rangeStart = int(rangeStart)
            rangeEnd = int(rangeEnd)

            if rangeStart > rangeEnd:
                dialog=MDDialog(title='Error',
                                text='Enter a valid range.',
                                buttons=[
                                    MDFlatButton(
                                        text='Close',
                                        on_release= lambda _: dialog.dismiss()
                                    )
                                ])
                dialog.open()
            else:
                self.randomNum = randint(rangeStart,rangeEnd)

        else:
            dialog=MDDialog(title='Error',
                                text='Fill in.',
                                buttons=[
                                    MDFlatButton(
                                        text='Close',
                                        on_release= lambda _: dialog.dismiss()
                                    )
                                ])
            dialog.open()

class ShortenUrlScreen(Screen):
    short_url = StringProperty('Your URL appears here...')

    def shorten_url(self, long_url):

        response = requests.get(
        "https://tinyurl.com/api-create.php",
        params={"url": long_url}
        )
        if response.status_code == 200:
            self.short_url = response.text
        else:
            self.short_url = f'{response.status_code}: Error shortening the url. Please try again later.'

class TossCoinScreen(Screen):
    coin=StringProperty('Flip the Coin')

    def coinToss(self):
        self.coin=choice(['Heads','Tails'])
        toast(f'You got {self.coin}')

class YTVideoDownloadScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass


class AccountSettings(MDBoxLayout):
    pass

class GeneralSettings(MDBoxLayout):
    def on_kv_post(self, base_widget):
        items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Light",
                "on_release": lambda x="Light": self.set_theme(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Dark",
                "on_release": lambda x="Dark": self.set_theme(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.theme_dropdown,
            items=items,
            width_mult=4,
            max_height=dp(200),
        )

    def set_theme(self, choice):
        self.menu.dismiss()
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = choice
        self.ids.theme_dropdown.set_item(choice)

class About(MDBoxLayout):
    def openRepo(self):
        webbrowser.open('https://github.com/TheHarshitRaj/TheOne-App')


class TheOne(MDApp):
    def build(self):
        self.theme_cls.theme_style='Dark'
        self.theme_cls.primary_palette='DeepPurple'
        self.theme_cls.theme_style_switch_animation=True
        return Builder.load_file('app.kv')
    
    def quotes(self):
        response=requests.get('https://zenquotes.io/api/random')
        if response.status_code == 200:
            data=response.json()[0]
            quote = data['q'] + '\n\n- ' + data['a'] + '\n'
        elif response.status_code == 404:
            quote = 'Error connecting to the server. Try again later.'
        elif response.status_code == 429:
            quote = 'Too many requests. Please try again after a while.' + '\n\n- ' + 'TheOne' + '\n'
        else:
            quote = f"Unexpected status code: {response.status_code}. Please try again later."

        return quote

if __name__=='__main__':
    TheOne().run()