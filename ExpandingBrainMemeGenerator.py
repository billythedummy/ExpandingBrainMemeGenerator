from PIL import Image, ImageDraw, ImageFont
import random
import math

ASPECT_RATIO = 2.86 #aspect ratio of a single cell
CELL_HEIGHT = 301
CELL_WIDTH = int(ASPECT_RATIO * CELL_HEIGHT)
N_BRAIN_IMAGES = 15 #number of images in collection sorted by ascending order of gayness

class Cell:
    #fields: brainImage, caption, outputImage
    def __init__(self, brainImage, caption):
        self.brainImage = brainImage #pillow image object of brain.png
        self.caption = caption

    def drawImg(self):
        self.drawBrainImg()
        self.drawText()
        return self.outputImage
        
    def drawBrainImg(self):
        background = Image.new('RGBA', (CELL_WIDTH, CELL_HEIGHT), (255, 255, 255, 255))
        img_w, img_h = self.brainImage.size
        bg_w, bg_h = background.size
        offset = (bg_w-img_w, 0)
        background.paste(self.brainImage, offset)
        self.outputImage = background
        draw = ImageDraw.Draw(self.outputImage)
        draw.line((0,CELL_HEIGHT, CELL_WIDTH,CELL_HEIGHT), fill = 0, width=3)

    def drawText(self):
        sidePadding = 5
        topPadding = 5
        textBoxWidth = int(CELL_WIDTH/2 - 2*sidePadding)
        textBoxHeight = int(CELL_HEIGHT/2 - 2*topPadding)
        fontSize = self.calculateFontSize(self.caption, textBoxWidth, textBoxHeight)
        charArray = list(self.caption)
        rowWidth = len(charArray)*fontSize
        heightOffset = 0
        lengthOffset = [(CELL_WIDTH/2-len(charArray)*fontSize/2)/2]
        if rowWidth > textBoxWidth:
            spaceIndices = []
            for i in range(0, len(charArray)):
                if charArray[i] == " ":
                    spaceIndices.append(i)
            if len(spaceIndices) == 0: #no spaces in caption
                fontSize = 24 #set fontSize to 24 and hope for the best
            print("spaceIndices", spaceIndices)
            breakIndices = self.bisectGetBreaks(len(charArray), spaceIndices, fontSize, textBoxWidth*2) #because ttf width is haalf of fontSize
            breakIndices.sort()
            print("breakIndices", breakIndices)
            lengthOffset.pop()
            index = 0
            for j in range(0, len(breakIndices)):
                if j == 0:
                    prevIndex=0
                else:
                    prevIndex=breakIndices[j-1]
                index = breakIndices[j]
                charArray[index] = "\n"
                lengthOffset.append((CELL_WIDTH/2-(index-prevIndex)*fontSize/2)/2) #ttf width is half of fontSize
            lengthOffset.append((CELL_WIDTH/2-(len(charArray)-index-1)*fontSize/2)/2)
            print("lengthOffset", lengthOffset)
            self.caption = "".join(charArray)
            heightOffset = len(breakIndices)*fontSize
            
        captionBroken = self.caption.split("\n")
        font = ImageFont.truetype("fonts/Calibri.ttf",fontSize)
        draw = ImageDraw.Draw(self.outputImage)
        for i in range(0, len(captionBroken)):
            draw.text((lengthOffset[i],(CELL_HEIGHT-heightOffset)/2+i*fontSize), captionBroken[i], (0,0,0),font=font)

    def bisectGetBreaks(self, charArrayLen, spaceIndices, fontSize, widthLimit):
        mid = int(len(spaceIndices)/2)
        if mid == 0:
            return []
        midSpace = spaceIndices[mid]
        res = [midSpace]
        if (midSpace)*fontSize > widthLimit:
            arr1 = self.bisectGetBreaks(midSpace, spaceIndices[:mid], fontSize, widthLimit)
            for index1 in arr1:
                res.append(index1)
        if (charArrayLen-midSpace)*fontSize > widthLimit:
            arr2 = self.bisectGetBreaks(charArrayLen-midSpace, spaceIndices[mid:], fontSize, widthLimit)
            for index2 in arr2:
                res.append(index2)
        return res
    
    def calculateFontSize(self, captionStr, textBoxWidth, textBoxHeight):
        #just a very rough gauge based on area for now
        effectiveArea = 2*textBoxWidth*textBoxHeight #ttf width half
        sizeGauge = math.sqrt(effectiveArea/len(captionStr))
        print("sizeGauge", sizeGauge)
        return int(0.5*sizeGauge) #arbitrary magic number 0.5 lol
        
    
class Generator:
    #fields: captions, brainImages
    def __init__(self, captions):
        self.captions = captions
        self.brainImages = self.getBrainImages(self.getRandomBrainIndices())
        
    def getRandomBrainIndices(self):
        res = []
        res.append(random.randint(0,1))#first brainimage is either 0 or 1
        quota = len(self.captions)
        for i in range(1, quota):
            previousIndex = res[i-1]
            endBuffer = quota-i
            res.append(random.randint(previousIndex+1, N_BRAIN_IMAGES-endBuffer)) 
        return res

    def getBrainImages(self, brainIndices):
        res = []
        for index in brainIndices:
            filename = str(index)+".png"
            filename = "brains/"+filename
            res.append(Image.open(filename))
        return res
    
    def drawImage(self):
        nCells = len(self.captions)
        background = Image.new('RGBA', (CELL_WIDTH, nCells*CELL_HEIGHT), (255, 255, 255, 255))
        heightOffset = 0
        for i in range(0, nCells):
            cell = Cell(self.brainImages[i], self.captions[i])
            offset = (0, heightOffset)
            background.paste(cell.drawImg(), offset)
            heightOffset += CELL_HEIGHT
        background.show()
        
    
if __name__ == "__main__":
    #breaks when input string is too long
    testGen = Generator(["cock", "penis", "Z y s p u r p l e s n a k e"])
    testGen.drawImage()
    #YOU'RE GONNA HAVE TO SAVE IT SOMEWHERE TO OUTPUT IT I SUPPOSE
