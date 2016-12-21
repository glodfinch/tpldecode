import StringIO
import struct
from bitstring import BitArray
from imageformat import ImageFormat

class CMPR(ImageFormat):
    def __init__(self, data, width, height):
        self.width = width
        self.height = height
        self.loadImage(data)
        
    def loadImage(self, data):
        self.createImageArray(self.width, self.height)
        self.decodeCMPR(data)
        
    def decodeCMPR(self, data):
        s = StringIO.StringIO(data)
    
        for j in range(0, self.height/8):
            for i in range(0, self.width/8):
                block = s.read(32)
                decodedBlock = self.decodeCMPRBlock(block)
                self.imageArray = self.listCopy2d(self.imageArray, decodedBlock, i*8, j*8)
        
        s.close()
        
    def decodeCMPRBlock(self, block):
        bm = [[0 for i in range(8)] for j in range(8)]
        bm = self.listCopy2d(bm, self.decodeCMPRSubblock(block[:8]), 0, 0)
        bm = self.listCopy2d(bm, self.decodeCMPRSubblock(block[8:16]), 4, 0)
        bm = self.listCopy2d(bm, self.decodeCMPRSubblock(block[16:24]), 0, 4)
        bm = self.listCopy2d(bm, self.decodeCMPRSubblock(block[24:32]), 4, 4)
        return bm
        
    def decodeCMPRSubblock(self, sblock):
        pall = self.decodeCMPPalette(sblock[:4])
        pix = BitArray(uint=struct.unpack('>I', sblock[-4:])[0], length=32)
        j = 0
        k = 0
        sb = []
    
        for j in range(0, 4):
            sb.append([])
            for i in range(0, 4):
                c = pix[k * 2:(k + 1) * 2].uint
                sb[j].append(pall[c])
                k += 1
            
        return sb
        
    def decodeCMPPalette(self, pdata):
        #Decode the 2 byte pallette data for a CMP subblock and interpolate the additional colours
        #TODO: check interpolation accuracy
        cone = struct.unpack('>H', pdata[:2])[0]
        ctwo = struct.unpack('>H', pdata[2:4])[0]
        cthree = 0
        cfour = 0
    
        if cone > ctwo:
            cthree = self.interpolate565Colours(cone, ctwo, 1/float(3))
            cfour = self.interpolate565Colours(cone, ctwo, 2/float(3))
        else:
            cthree = self.interpolate565Colours(cone, ctwo, 0.5)
            cfour = (0, 0, 0, 0)
        
        cone = self.c565to888(cone)
        ctwo = self.c565to888(ctwo)
        ret = {0: cone, 1: ctwo, 2: cthree, 3: cfour}
        return ret

    def interpolate565Colours(self, one, two, amount):
        #Interpolate between two RGB565 colours
        one = self.c565to888(one)
        two = self.c565to888(two)
        return self.interpolateColours(one, two, amount)

    def interpolateColours(self, one, two, amount):
        #Interpolate between two RGB888 colours
        cdiffr = one[0] - two[0]
        cdiffg = one[1] - two[1]
        cdiffb = one[2] - two[2]
        cthr = int(float(one[0]) - (cdiffr * amount))
        cthg = int(float(one[1]) - (cdiffg * amount))
        cthb = int(float(one[2]) - (cdiffb * amount))
        return (cthr, cthg, cthb, 255)
        
    def c565to888(self, col):
        #Convert RGB565 to RGB888
        if col == -1:
            return -1
    
        ba = BitArray(uint=int(col), length=16)
        r = int(round(float(ba[:5].uint) * (255 / float(32))))
        g = int(round(float(ba[5:11].uint) * (255 / float(64))))
        b = int(round(float(ba[11:16].uint) * (255 / float(32))))
        return (r, g, b, 255)