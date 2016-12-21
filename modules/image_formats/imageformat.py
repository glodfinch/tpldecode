class ImageFormat:
    def createImageArray(self, width, height):
        self.imageArray = [[0 for i in range(width)] for j in range(height)]
                            
    def listCopy2d(self, inp, cop, x, y): 
        ox = x
        for row in cop:
            for pix in row:
                inp[y][x] = pix
                x += 1
            y += 1
            x = ox
        
        return inp
        
    def flatten(listOfLists):
        return chain.from_iterable(listOfLists)