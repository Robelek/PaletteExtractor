import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os


currentlySelectedImagePath = None
currentImage = None
def browseImages():
    global currentlySelectedImagePath
    global currentImage
    global imageNameLabelText



    currentlySelectedImagePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")], initialdir=".")
    if currentlySelectedImagePath:
        currentImage = Image.open(currentlySelectedImagePath)

        imageNameLabelText.set(currentlySelectedImagePath)



def getAllUniqueColors():
    global currentImage

    uniqueColors = set()
    image = currentImage.load()
    width, height = currentImage.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = image[y,x]

            if a != 0:
                colorData = r,g,b
                uniqueColors.add(colorData)

    return uniqueColors

def generatePalette():
    global currentlySelectedImagePath

    if currentlySelectedImagePath is None:
        tk.messagebox.showerror(message="No input image provided")

        return

    allColors = getAllUniqueColors()
    colorList = list(allColors)


    palette = Image.new("RGB", (len(colorList),1))

    for i in range(len(colorList)):
        palette.putpixel((i, 0), colorList[i])

    originalFileName = os.path.splitext(os.path.basename(currentlySelectedImagePath))[0]
    palettePath = f"Palettes/{originalFileName}_palette.png"
    palette.save(palettePath)

    tk.messagebox.showinfo(message=f"File saved successfully to: {palettePath}")


root = tk.Tk()
root.title("Palette Extractor")
root.minsize(400, 30)

browseImagesButton = tk.Button(root, text="Browse images", command=browseImages, pady=5)
browseImagesButton.pack(pady=10)

imageNameLabelText = tk.StringVar()
imageNameLabelText.set("Currently selected image: none")
imageNameLabel = tk.Label(root, textvariable=imageNameLabelText, pady=10)
imageNameLabel.pack()

browseImagesButton = tk.Button(root, text="Generate palette", command=generatePalette, pady=5)
browseImagesButton.pack(pady=10)

root.mainloop()