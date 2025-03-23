import functools
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os


currentlySelectedImagePath = None
currentImage = None

### OKLAB <-> RGB conversions
# converted from: https://gist.github.com/earthbound19/e7fe15fdf8ca3ef814750a61bc75b5ce

def gammaToLinear(c):
    if c > 0.04045:
        return pow((c + 0.055) / 1.055, 2.4)
    else:
        return c / 12.92

def linearToGamma(c):
    if c >= 0.0031308:
        return 1.055 * pow(c, 1 / 2.4) - 0.055
    else:
        12.92 * c

def cubeRoot(x):
    return x ** (1. / 3)
def rgbToOklab(rgbData):
    r, g, b = rgbData

    r = gammaToLinear(r/255.0)
    g = gammaToLinear(g/255.0)
    b = gammaToLinear(b/255.0)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l = cubeRoot(l)
    m = cubeRoot(m)
    s = cubeRoot(s)

    resultOKLAB = (
        l * +0.2104542553 + m * +0.7936177850 + s * -0.0040720468,
        l * +1.9779984951 + m * -2.4285922050 + s * +0.4505937099,
        l * +0.0259040371 + m * +0.7827717662 + s * -0.8086757660
    )

    return resultOKLAB

def oklabToRgb(oklabData):
    L, a, b = oklabData

    l = L + a * +0.3963377774 + b * +0.2158037573
    m = L + a * -0.1055613458 + b * -0.0638541728
    s = L + a * -0.0894841775 + b * -1.2914855480

    l = l**3
    m = m**3
    s = s**3

    r = l * +4.0767416621 + m * -3.3077115913 + s * +0.2309699292
    g = l * -1.2684380046 + m * +2.6097574011 + s * -0.3413193965
    b = l * -0.0041195378 + m * -0.7034439666 + s * +1.7072885337

    r = 255 * linearToGamma(r)
    g = 255 * linearToGamma(g)
    b = 255 * linearToGamma(b)

    r = round(r)
    g = round(g)
    b = round(b)

    return (r,g,b)


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
    height, width = currentImage.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = image[y,x]

            if a != 0:
                colorData = r,g,b

                uniqueColors.add(colorData)

    return uniqueColors

def oklabDistance(colorData1, colorData2):
    a, b, c = colorData1['oklab']
    x, y, z = colorData2['oklab']

    diffSum = (a-x)**2 + (b-y)**2 + (c-z)**2


    return diffSum

def sortColors(originalList):
    colorData = []
    for rgb in originalList:
        colorData.append({
            "rgb": rgb,
            "oklab": rgbToOklab(rgb)
        })

    sortedColorData = [colorData[0]]
    del colorData[0]

    while len(colorData) > 0:
        lastColor = sortedColorData[-1]

        closestColorIndex = 0
        closestDist = oklabDistance(colorData[closestColorIndex], lastColor)

        for i in range(len(colorData)):
            dist = oklabDistance(colorData[i], lastColor)

            if dist < closestDist:
                closestColorIndex = i
                closestDist = dist


        sortedColorData.append(colorData[closestColorIndex])
        del colorData[closestColorIndex]


    sortedColors = []
    for thisColorData in sortedColorData:
        sortedColors.append(thisColorData['rgb'])



    return sortedColors

def generatePalette():
    global currentlySelectedImagePath

    if currentlySelectedImagePath is None:
        tk.messagebox.showerror(message="No input image provided")

        return

    allColors = getAllUniqueColors()
    colorList = list(allColors)
    colorList = sortColors(colorList)

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