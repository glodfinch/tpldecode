import struct
from modules.image import Image

def checkIdent(i):
    #Check the magic ident at the start of a TPL file
    data = list(i)

    if struct.unpack('>B', data[0])[0] != 0:
        return False
    if struct.unpack('>B', data[1])[0] != 32:
        return False
    if struct.unpack('>B', data[2])[0] != 175:
        return False
    if struct.unpack('>B', data[3])[0] != 48:
        return False

    return True

file = raw_input('file: ')
f = open(file, 'rb')

try:
    ident = f.read(4)
    if checkIdent(ident):
        print 'TPL identifier found'
        count = struct.unpack('>I', f.read(4))[0]
        print 'Image count: ' + str(count)
        itoff = struct.unpack('>I', f.read(4))[0]
        print 'Image offset table byte: ' + str(itoff)
        f.seek(itoff)
        
        for i in range(0, count):
            imoff = struct.unpack('>I', f.read(4))[0]
            paoff = struct.unpack('>I', f.read(4))[0]
            cuoff = f.tell()
            f.seek(imoff)
            imheader = f.read(35)
            image = Image(imheader)
            print str(i) + ': ' + image.format + ' ' + str(image.size) + ' bytes'

            if image.format == 'CMPR' or image.format == 'IA8':
                f.seek(image.offset)
                imdata = f.read(image.size)
                image.loadImage(imdata)
                image.saveImage('C:/output/' + str(i) + '.png')
        
            f.seek(cuoff)          
finally:
    f.close()
