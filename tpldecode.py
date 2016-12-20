import pprint
import StringIO
import math
import binascii
from bitstring import BitArray

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

def decodeFormat(f):
    #Find the format for image data from the format code
    if stoi(f) == 0:
        return 'I4'
    if stoi(f) == 1:
        return 'I8'
    if stoi(f) == 2:
        return 'IA4'
    if stoi(f) == 3:
        return 'IA8'
    if stoi(f) == 4:
        return 'RGB565'
    if stoi(f) == 5:
        return 'RGB5A3'
    if stoi(f) == 6:
        return 'RGBA8'
    if stoi(f) == 8:
        return 'CI4'
    if stoi(f) == 9:
        return 'CI8'
    if stoi(f) == 10:
        return 'CI14X2'
    if stoi(f) == 14:
        return 'CMP'

    return False

def processImageHeader(data):
    #Extract data from an image's header
    ret = {}
    s = StringIO.StringIO(data)
    ret['height'] = hexDec(s.read(2))
    ret['width'] = hexDec(s.read(2))
    ret['format'] = decodeFormat(s.read(4))
    ret['offset'] = hexDec(s.read(4))
    ret['size'] = (ret['height'] * ret['width']) / 2
    s.close()
    return ret

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
    #Create a valid header for a bitmap file using width, height, and file size of pixels
    width = padToEight(iToBE(width))
    height = padToEight(iToBE(height))
    sizeraw = padToEight(iToBE(size))
    size = padToEight(iToBE(size + 54))
    header = '424D' + size + '000000003600000028000000' + width + height + '0100180000000000' + sizeraw + '130B0000130B00000000000000000000'
    return bytearray.fromhex(header)

def c565to888(col):
    #Convert RGB565 to RGB888 using lookup tables
    if col == -1:
        return -1

    table5 = [0, 8, 16, 25, 33, 41, 49,  58, 66, 74, 82, 90, 99, 107, 115, 123, 132, 140, 148, 156, 165, 173, 181, 189, 197, 206, 214, 222, 230, 239, 247, 255]
    table6 = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101,  105, 109, 113, 117, 121, 125, 130, 134, 138, 142, 146, 150, 154, 158, 162, 166, 170, 174, 178, 182, 186, 190, 194, 198, 202, 206, 210, 215, 219, 223, 227, 231,  235, 239, 243, 247, 251, 255]
    ba = BitArray(uint=int(col), length=16)
    ret = {}
    ret['r'] = table5[ba[:5].uint]
    ret['g'] = table6[ba[5:11].uint]
    ret['b'] = table5[ba[11:16].uint]
    return ret

def interpolateColours(one, two, amount):
    #Interpolate between two RGB888 colours
    cdiffr = one['r'] - two['r']
    cdiffg = one['g'] - two['g']
    cdiffb = one['b'] - two['b']
    cthr = int(one['r'] - (cdiffr * amount))
    cthg = int(one['g'] - (cdiffg * amount))
    cthb = int(one['b'] - (cdiffb * amount))
    return {'r': cthr, 'g': cthg, 'b': cthg}

def interpolate565Colours(one, two, amount):
    #Interpolate between two RGB565 colours
    return interpolateColours(c565to888(one), c565to888(two), amount)

def decodeCMPPalette(pdata):
    #Decode the 2 byte pallette data for a CMP subblock and interpolate the additional colours
    #TODO: check interpolation accuracy
    cone = hexDec(pdata[:2])
    ctwo = hexDec(pdata[-2:])
    cthree = 0
    cfour = 0

    if cone > ctwo:
        cthree = interpolate565Colours(cone, ctwo, 1/3)
        cfour = interpolate565Colours(cone, ctwo, 2/3)
    else:
        cthree = interpolate565Colours(cone, ctwo, 1/2)
        cfour = -1
    
    cone = c565to888(cone)
    ctwo = c565to888(ctwo)
    ret = {0: cone, 1: ctwo, 2: cthree, 3: cfour}
    return ret        

def decodeCMPSubblock(sbdata):
    #Decode a CMP subblock into pallette and pixel data, then return rgb pixels
    pall = decodeCMPPalette(sbdata[:4])
    pix = BitArray(uint=int(hexDec(sbdata[-4:])), length=32)
    j = 0
    k = 0
    sb = []

    while j < 4:
        sb.append([])
        i = 0
        while i < 4:
            c = pix[k * 2:(k + 1) * 2].uint
            if pall[c] != -1:
                sb[j].append(pall[c])
            else:
                sb[j].append({'r': 0, 'g': 0, 'b': 0})
            k += 1
            i += 1
        j += 1
        
    return sb

def decodeCMPBlock(bdata):
    #Decode the four subblocks that make up a CMP block
    bm = [[], []]
    s = StringIO.StringIO(bdata)
    bm[0].append(decodeCMPSubblock(s.read(8)))
    bm[0].append(decodeCMPSubblock(s.read(8)))
    bm[1].append(decodeCMPSubblock(s.read(8)))
    bm[1].append(decodeCMPSubblock(s.read(8)))
    s.close()
    return bm

def arrayToPixels(ar):
    #Convert the complicated block/subblock array into a linear set of pixels for bitmap
    ret = ''
    blockwidth = len(ar[0])
    phc = 0
    j = len(ar) - 1
    print str(j) + ' ' + str(blockwidth)
    while j >= 0:
        sbh = 1
        while sbh >= 0:
            ph = 3
            while ph >= 0:
                phc += 1
                k = 0
                while k < blockwidth:
                    sbw = 0
                    while sbw < 2:
                        pw = 0
                        while pw < 4:
                            cpix = ar[j][k][sbh][sbw][ph][pw]
                            px = padToTwo(hex(cpix['b'])[2:])
                            px += padToTwo(hex(cpix['g'])[2:])
                            px += padToTwo(hex(cpix['r'])[2:])
                            ret += px
                            pw += 1
                        sbw += 1
                    k += 1
                ph -= 1
            sbh -= 1
        j -= 1

    print len(ret)
    return bytearray.fromhex(ret)

def decodeCMP(imdata, width, height):
    #Decode a CMP encoded image into bitmap
    s = StringIO.StringIO(imdata)
    j = 0
    bm = []

    while j < height / 8:
        bm.append([])
        i = 0
        while i < width / 8:
            bm[j].append(decodeCMPBlock(s.read(32)))
            i += 1
        j += 1
    
    s.close()
    bm = {'header': makeBitmapHeader(width, height, len(bm)), 'pixels': arrayToPixels(bm)}
    return bm

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
        while i < count:
            imoff = hexDec(f.read(4))
            paoff = hexDec(f.read(4))
            cuoff = f.tell()
            f.seek(imoff)
            imheader = f.read(35)
            imheader = processImageHeader(imheader)
            pprint.pprint(imheader)

            #TODO: support more image formats
            if imheader['format'] == 'CMP':
                f.seek(imheader['offset'])
                imdata = f.read(imheader['size'])
                bitmap = decodeCMP(imdata, imheader['width'], imheader['height'])
                bm = open('C:/output/' + str(i) + '.bmp', 'wb')
                bm.write(bitmap['header'])
                bm.write(bitmap['pixels'])
                bm.close()
        
            f.seek(cuoff)  
            i += 1
        
finally:
    f.close()
