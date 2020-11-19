from kivy.config import Config
## CONFIGURATION FOR DEVELOPMENT ONLY
# Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '650')
#######################################

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton



class Application(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		with open('main.kv', encoding='utf-8') as f:
			self.INTERFACE = Builder.load_string(f.read())
		menu_items = [{"text":"Ile de france"}, {"text":"France"}]
		self.menu_ville = MDDropdownMenu(
            caller=self.INTERFACE.ids.ville,
            items=menu_items,
            position="center",
            width_mult=8,
        )
		self.menu_ville.bind(on_release=self.set_item)

		self.menu_compte = MDDropdownMenu(
            caller=self.INTERFACE.ids.compte,
            items=[
            	{'text':'gaetan.jonathan.bakary@esti.mg'},
            	{'text':'emc324@gmail.com'},
            	{'text': 'bailti75008@gmail.com'}
            ],
            position="center",
            width_mult=8,
        )
		self.menu_compte.bind(on_release=self.set_item_)


	def build(self):
		self.theme_cls.primary_palette = "Teal"
		self.items = [f"test {i}" for i in range(5)]

		return self.INTERFACE


	def set_item(self, instance_menu, instance_menu_item):
 		def set_item(interval):
 			self.INTERFACE.ids.ville.text = instance_menu_item.text
 			instance_menu.dismiss()
 		Clock.schedule_once(set_item, 0.5)
	

	def set_item_(self, instance_menu, instance_menu_item):
 		def set_item(interval):
 			self.INTERFACE.ids.compte.text = instance_menu_item.text
 			instance_menu.dismiss()
 		Clock.schedule_once(set_item, 0.5)



if __name__ == '__main__':
	Application().run()