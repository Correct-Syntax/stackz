
import copy
import cv2
import numpy as np
import OpenImageIO as oiio
import dearpygui.dearpygui as dpg


class MainApplication(object):
    def __init__(self):
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080
        self.SIDEBAR_WIDTH = 350

        self.curr_window = None

        self.drawlist = None

        self.main_window = None
        self.controls_panel = None
        self.viewport_window = None

        self.blurslider = dpg.generate_uuid()
        self.rotationslider = dpg.generate_uuid()
        self.infotext = dpg.generate_uuid()

        path = "test.jpeg"

        img_input = oiio.ImageInput.open(path)
        if img_input is None:
            print("IO ERROR: ", oiio.geterror())
        image = img_input.read_image(format=oiio.FLOAT)

        if image.shape[2] == 3:
            self.img_data = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        else:
            self.img_data = image

        self.__init_window()

    def viewport_config(self):
        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_viewport_title("Stackz Image Editor")
        dpg.set_viewport_width(self.WINDOW_WIDTH)
        dpg.set_viewport_height(self.WINDOW_HEIGHT)
        dpg.maximize_viewport()

    def __init_window(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Styles
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 6, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 2, 24, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, 2, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)

                # Colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 35), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (48, 48, 48), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200), category=dpg.mvThemeCat_Core)

        with dpg.theme() as disabled_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (100, 100, 100), category=dpg.mvThemeCat_Core)

        with dpg.font_registry() as main_font_registry:
            regular_font = dpg.add_font('resources/fonts/Inter-Regular.ttf', 19)

        with dpg.texture_registry():
            dpg.add_raw_texture(1920, 1080, self.img_data, 
                                format=dpg.mvFormat_Float_rgba, 
                                tag="viewport_image")

        with dpg.window(label="Editor", width=1920, height=1080) as self.main_window:
            with dpg.child_window(label="Controls_Info", width=self.SIDEBAR_WIDTH, pos=[10, 10], border=False, no_scrollbar=True):
                with dpg.collapsing_header(label="Controls", default_open=True) as self.controls_panel:
                    self.infotext = dpg.add_text("Image editing", wrap=300)

                    self.rotationslider = dpg.add_drag_float(label="Rotation", min_value=0, max_value=360, callback=self.rotation_change)
                    self.blurslider = dpg.add_drag_float(label="Blur", min_value=0, max_value=400, callback=self.blur_change)


            with dpg.child_window(label="Viewport", height=1080, width=1920, border=False, no_scrollbar=True, pos=[self.SIDEBAR_WIDTH+20, 10]) as viewport_window:
                self.viewport_window = viewport_window

                self.drawlist = dpg.add_drawlist(parent=self.viewport_window,
                                                 width=1920, height=1080, show=True)

                dpg.draw_image("viewport_image", (0, 0), (1920, 1080), uv_min=(0, 0), uv_max=(1, 1), parent=self.drawlist)

        dpg.bind_font(regular_font)
        dpg.bind_theme(global_theme)
        dpg.set_primary_window(self.main_window, True)


    def rotate(self, image, angle, center=None, scale=1.0):
        (h, w) = image.shape[:2]
        if center is None:
            center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(image, M, (w, h))

        return rotated

    def rotation_change(self, sender, app_data, user_data):
        rotation_value = dpg.get_value(sender)

        img = self.img_data

        img_data = self.rotate(img, rotation_value)
        dpg.set_value("viewport_image", img_data)

    def blur_change(self, sender, app_data, user_data):
        blur_value = dpg.get_value(sender)

        img = self.img_data
        kernel_x = int(blur_value)
        kernel_y = int(blur_value)

        img_data = cv2.boxFilter(img, -1, (kernel_x, kernel_y))

        dpg.set_value("viewport_image", img_data)
