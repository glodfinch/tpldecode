import StringIO
import struct
from imageformat import ImageFormat

class IA8(ImageFormat):
    def loadImage(self, data):
        self.createImageArray(self.width, self.height)
        self.decodeIA8(data)
        
    def decodeIA8(self, data):
        s = StringIO.StringIO(data)
    
        for j in range(0, self.height/8):
            for i in range(0, self.width/8):
                block = s.read(32)
                decodedBlock = self.decodeIA8Block(block)
                self.imageArray = self.listCopy2d(self.imageArray, decodedBlock, i*8, j*8)
        
        s.close()
        
    def decodeIA8Block(self, block):
        bl = []
        s = StringIO.StringIO(block)
        
        for j in range(0, 4):
            bl.append([])
            for i in range(0, 4):
                col = struct.unpack('>B', s.read(1))[0]
                alpha = struct.unpack('>B', s.read(1))[0]
                bl[j].append((col, col, col, alpha))
                
        return bl
                