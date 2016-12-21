import StringIO
import struct
from bitstring import BitArray
from imageformat import ImageFormat

class RGB5A3(ImageFormat):
    def __init__(self, data, width, height):
        self.blockWidth = 4
        self.blockHeight = 4
        self.blockSize = 32
        ImageFormat.__init__(self, data, width, height)
        
    def decodeBlock(self, block):
        bl = []
        s = StringIO.StringIO(block)
        
        for j in range(0, 4):
            bl.append([])
            for i in range(0, 4):
                pix = BitArray(uint=struct.unpack('>H', s.read(2))[0], length=16)
                alphaFlag = pix[:1].uint

                if alphaFlag == 1:
                    a = 255
                    r = pix[1:6].uint * 8
                    g = pix[6:11].uint * 8
                    b = pix[11:16].uint * 8
                else:
                    a = pix[1:4].uint * 32
                    r = pix[4:8].uint * 17
                    g = pix[8:12].uint * 17
                    b = pix[12:16].uint * 17

                bl[j].append((r, g, b, a))
                
        return bl