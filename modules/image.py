import struct
from image_formats.cmpr import CMPR

class Image:
    def __init__(self, header=False, data=False):
        if header != False: 
            self.loadHeader(header)
        if data != False: 
            self.loadImage(data)
    
    def loadHeader(self, header):
        self.processImageHeader(header)
        return {'offset': self.offset, 'size': self.size}

    def loadImage(self, data):
        if self.format == 'CMPR':
            self.image = CMPR(data, self.width, self.height)
            
    def getPixelArray(self):
        return self.image.imageArray
        
    def decodeFormat(self, fmat):
        fmat = struct.unpack('>I', fmat)[0]
        print str(fmat) + '!'
        
        if fmat == 0:
            return 'I4'
        if fmat == 1:
            return 'I8'
        if fmat == 2:
            return 'IA4'
        if fmat == 3:
            return 'IA8'
        if fmat == 4:
            return 'RGB565'
        if fmat == 5:
            return 'RGB5A3'
        if fmat == 6:
            return 'RGBA8'
        if fmat == 8:
            return 'CI4'
        if fmat == 9:
            return 'CI8'
        if fmat == 10:
            return 'CI14X2'
        if fmat == 14:
            return 'CMPR'
        
        return False
        
    def processImageHeader(self, data):
        self.height = struct.unpack('>H', data[:2])[0]
        self.width = struct.unpack('>H', data[2:4])[0]
        self.format = self.decodeFormat(data[4:8])
        self.offset = struct.unpack('>I', data[8:12])[0]
        self.size = (self.height * self.width) / 2