import typing
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cv2 import cv2
import json


class EditableRow(tk.LabelFrame):
    def __init__(self, master, key, value, *args, **kwargs):
        kwargs['text'] = key
        super().__init__(master, *args, **kwargs)
        family = 'Helvetica'

        self.is_correct = tk.BooleanVar(self, value=0)
        self.checkbutton = ttk.Checkbutton(self, text=':', variable=self.is_correct)
        self.text = tk.Text(self, width=10, height=1, wrap=tk.WORD, font=(family, 14))

        self._bind_text_widget(value)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)

        self.checkbutton.pack(side='left', padx=5)
        self.text.pack(side='right')

    def update_size(self, *args):
        widget = self.text

        width = max((len(line) for line in widget.get("1.0", tk.END).splitlines()))
        height = float(widget.index(tk.END))

        widget.config(width=width + 1, height=height - 1)

    def _bind_text_widget(self, value):
        text = self.text

        text.bind("<Key>", self.update_size)
        # todo: value is list
        text.insert('1.0', json.dumps(value, ensure_ascii=0))
        self.update_size()

    def get_result(self):
        if not self.is_correct.get():
            return None
        value = self.text.get('1.0', 'end').strip('\n')
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        return self['text'], value


class Viewer(tk.Tk):
    def __init__(self, data, image, text, name=None, correct_data=None):
        super().__init__()

        self.left = tk.Frame(self)
        self.right = tk.Frame(self)
        self.destroy_btn = ttk.Button(self.left, text='END', command=self.destroy)

        self.rows: typing.List[EditableRow] = []
        self._result = None
        self._image = None

        self.pack_right(text, image)
        self.pack_left(data, correct_data)

        self.title(name)
        create_style()
        self.bind("<Escape>", self.destroy)
        self.eval('tk::PlaceWindow . center')

    def pack_right(self, text, image):
        tk.Label(self.right, text=text).pack(side='top')
        if image is not None:
            self._image = make_tk_image(image, new_width=900, master=self)
            image = self._image

            canvas = tk.Canvas(self.right, width=image.width(), height=image.height())
            canvas.create_image(0, 0, anchor="nw", image=image)
            canvas.pack(side='top')

        self.right.pack(side='right')

    def pack_left(self, data, correct_data):
        for key, value in data.items():
            correct_value = correct_data.get(key, None)
            bg = None if correct_value is None else 'green' if correct_value == json.loads(json.dumps(value)) else 'red'

            row = EditableRow(self.left, key, value, bg=bg)
            self.rows.append(row)

            row.pack(side='top', fill='x', pady=4)

        self.destroy_btn.pack(side='bottom', expand=True, fill='x', pady=20)
        self.left.pack(side='left', fill='x')

    def wait_response(self):
        self.mainloop()

        try:
            return self._get_result()
        except tk.TclError:
            return self._result

    def _get_result(self):
        data = (r.get_result() for r in self.rows)
        
        data = {d[0]: d[1] for d in data if d}
        return data

    def destroy(self, *args):
        self._result = self._get_result()
        super().destroy()


def create_style():
    style = ttk.Style()
    style.configure('TButton', font=('calibri', 20, 'bold'), borderwidth='4')
    style.map('TButton', foreground=[('active', '!disabled', 'green')],
              background=[('active', 'black')])


def make_tk_image(image, new_width, master=None):
    height, width = image.shape[:2]
    scale = new_width / width

    image = cv2.resize(image, None, fx=scale, fy=scale)
    image = ImageTk.PhotoImage(master=master, image=Image.fromarray(image))

    return image


def check_data(data: dict,
               save_path=None,
               name=None,
               image=None,
               text=None,
               # todo: skip_correct
               ):
    need_save = save_path is not None
    correct_data = {}
    if need_save:
        path = save_path + name + '.json'
        correct_data = _read_data(path)

    root = Viewer(data=data,
                  correct_data=correct_data,
                  image=image,
                  name=name,
                  text=text)
    new_data = root.wait_response()

    if need_save:
        _write_data(path, correct_data, new_data)


def _read_data(path):
    try:
        with open(path, mode='r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def _write_data(path, data, new_data):
    data = data.copy()
    data.update(new_data)
    with open(path, mode='w') as file:
        json.dump(data, file)
    return data


def main():
    name = '20.jpg'
    path = '/home/arkady_big/Repositories/ReciveTextDetector/cropped/'
    raw_path = '/home/arkady_big/Repositories/ReciveTextDetector/rawChecks/check/check/'
    import os
    from parser import parse
    names = os.listdir(path)
    names.sort(key=lambda x: int(x.split('.')[0]))
    # names.sort(key=lambda x: int(x.split('.')[0].split('_')[-1]))
    names = [i for i in names if '.json' not in i]
    hapoalims = [21, 18, 19, 20, 21, 22, 23, 24, 25, 39] # 18 23 25
    disconts = [5, 6, 7, 8, 45] # 6 8
    masads = (12, 13, 44) # 44
    otsearahoyats = [26, 42] # 
    leumi = [30, 31, 32, 33, 34, 35, 37]
    
    import numpy as np
    from Crop.crop_cheques import crop

    
    for i, name in enumerate([46]):
        # i *= 5
        if not isinstance(name, str):
            i = name
            name = str(name) + '.jpg'
        img = cv2.imread(f'/home/arkady_big/Repositories/ReciveTextDetector/chequeProgram/cheques_to_test/5.jpg', 0)
        img = crop(img)
        data = parse(img, True)
        check_data(data,
                save_path=path,
                name=str(i) + '.jpg',
                image=img)


if __name__ == '__main__':
    main()
