import pprint
from modules.image import Image

def stoi(s):
    #Sums a string of ascii chatacters as byte values
    return sum(bytearray(s))

def toHex(i):
    #Converts an int to uppercase hex
    return i.encode('hex').upper()

def hexDec(h):
    #Converts hex to dec
    l = list(h)
    s = ''
    
    for char in l:
        s += toHex(char)
        
    return int(s, 16)

def checkIdent(i):
    #Check the magic ident at the start of a TPL file
    data = list(i)

    if toHex(data[0]) != '00':
        return False
    if toHex(data[1]) != '20':
        return False
    if toHex(data[2]) != 'AF':
        return False
    if toHex(data[3]) != '30':
        return False

    return True

def hex2(n):
    #Int to hex alternative
    x = '%x' % (n,)
    return ('0' * (len(x) % 2)) + x

def iToBE(i):
    #Int to big endian hex
    return hex2(i).decode('hex')[::-1].encode('hex')

def padToEight(s):
    #Pad a hex string to eight characters with zeroes
    if len(s) < 8:
        s += ('0' * int(8 - len(s)))
        
    return s

def padToTwo(s):
    #Pad a hex string to two characters with zeroes
    #TODO: generic padding function
    if len(s) == 1:
        s = '0' + s

    return s

def makeBitmapHeader(width, height, size):
    #Create a valid header for a bitmap file using width, height, and 
    #file size of pixels
    width = padToEight(iToBE(width))
    height = padToEight(iToBE(height))
    sizeraw = padToEight(iToBE(size))
    size = padToEight(iToBE(size + 54))
    header = '424D' + size + '000000003600000028000000' + width + height + '0100180000000000' + sizeraw + '130B0000130B00000000000000000000'
    return bytearray.fromhex(header)    

def arrayToPixels(ar):
    #Convert a pixel array into a linear set of pixels for bitmap
    ret = ''
    width = len(ar[0])
    h = len(ar) - 1

    while h >= 0:
        w = 0
        while w < width:
            cpix = ar[h][w]
            px = padToTwo(hex(cpix[2])[2:])
            px += padToTwo(hex(cpix[1])[2:])
            px += padToTwo(hex(cpix[0])[2:])
            ret += px
            w += 1
        h -= 1

    print len(ret)
    return bytearray.fromhex(ret)

file = raw_input('file: ')
f = open(file, 'rb')

try:
    ident = f.read(4)
    if checkIdent(ident):
        print 'TPL identifier found'
        count = stoi(f.read(4))
        print 'Image count: ' + str(count)
        itoff = hexDec(f.read(4))
        print 'Image offset table byte: ' + str(itoff)
        f.seek(itoff)
        i = 0
        for i in range(0, count):
            imoff = hexDec(f.read(4))
            paoff = hexDec(f.read(4))
            cuoff = f.tell()
            f.seek(imoff)
            imheader = f.read(35)
            image = Image(imheader)
            print image.format
            #TODO: support more image formats
            if image.format == 'CMPR':
                f.seek(image.offset)
                imdata = f.read(image.size)
                image.loadImage(imdata)
                bitmapPixels = arrayToPixels(image.getPixelArray())
                bitmapHeader = makeBitmapHeader(image.width, image.height, image.size)
                bm = open('C:/output/' + str(i) + '.bmp', 'wb')
                bm.write(bitmapHeader)
                bm.write(bitmapPixels)
                bm.close()
        
            f.seek(cuoff)          
finally:
    f.close()
