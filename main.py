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
        
        for i in range(0, count):
            imoff = hexDec(f.read(4))
            paoff = hexDec(f.read(4))
            cuoff = f.tell()
            f.seek(imoff)
            imheader = f.read(35)
            image = Image(imheader)
            print str(i) + ': ' + image.format

            if image.format == 'CMPR':
                f.seek(image.offset)
                imdata = f.read(image.size)
                image.loadImage(imdata)
                image.saveImage('C:/output/' + str(i) + '.png')
        
            f.seek(cuoff)          
finally:
    f.close()
