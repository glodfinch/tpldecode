import struct
import PIL
from image_formats.cmpr import CMPR
from image_formats.ia8 import IA8
from image_formats.rgb5a3 import RGB5A3
from image_formats.rgb565 import RGB565
from image_formats.i4 import I4
from image_formats.rgba8 import RGBA8

class Image:
    def __init__(self, header=False, data=False):
        self.size = 0
        
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
        if self.format == 'IA8':
            self.image = IA8(data, self.width, self.height)
        if self.format == 'RGB5A3':
            self.image = RGB5A3(data, self.width, self.height)
        if self.format == 'RGB565':
            self.image = RGB565(data, self.width, self.height)
        if self.format == 'I4':
            self.image = I4(data, self.width, self.height)
        if self.format == 'RGBA8':
            self.image = RGBA8(data, self.width, self.height)
        
            
    def saveImage(self, filename):
        img = PIL.Image.new('RGBA', (self.width, self.height))
        img.putdata(self.image.getPixels())
        img.save(filename)
        
    def decodeFormat(self, fmat):
        fmat = struct.unpack('>I', fmat)[0]
        
        if fmat == 0:
            self.size = (self.height * self.width) / 2
            return 'I4'
        if fmat == 1:
            return 'I8'
        if fmat == 2:
            return 'IA4'
        if fmat == 3:
            self.size = self.height * self.width * 2
            return 'IA8'
        if fmat == 4:
            self.size = self.height * self.width * 2
            return 'RGB565'
        if fmat == 5:
            self.size = self.height * self.width * 2
            return 'RGB5A3'
        if fmat == 6:
            self.size = self.height * self.width * 4
            return 'RGBA8'
        if fmat == 8:
            return 'CI4'
        if fmat == 9:
            return 'CI8'
        if fmat == 10:
            return 'CI14X2'
        if fmat == 14:
            self.size = (self.height * self.width) / 2
            return 'CMPR'
        
        return False
        
    def processImageHeader(self, data):
        self.height = struct.unpack('>H', data[:2])[0]
        self.width = struct.unpack('>H', data[2:4])[0]
        self.format = self.decodeFormat(data[4:8])
        self.offset = struct.unpack('>I', data[8:12])[0]