from PIL import Image
import glob, os
import boto3
import config
import requests
from io import BytesIO
import botocore
from ImageML import get_colors

region = config.DEFAULT_CONFIG['region']
bucket_name = config.DEFAULT_CONFIG['bucket']
temp_path = config.DEFAULT_CONFIG['temp_path']

def create_tumbnail(path, imagen, width, height):
    try:
        size = int(width), int(height)
        file, ext = os.path.splitext(imagen)
        formato = obtener_formato(ext[1:])
        im = Image.open(open(path + "/" + imagen, 'rb'))
        im.thumbnail(size)
        im.save(path +"/"+ file +'_' + width + '_' + height + ext, formato)
    except IOError as ioe:
        print(ioe)
    except Exception as e:
        print(e)
    return file +'_' + width + '_' + height + ext

def resize(path, imagen, width, height):
    try:
        new_size = int(width), int(height)
        file, ext = os.path.splitext(imagen)
        formato = obtener_formato(ext[1:])
        im = Image.open(open(path + "/" + imagen, 'rb'))
        im.resize(new_size, Image.LANCZOS)
        im.save(path +"/"+ file +  "_resize." + ext, formato)
    except IOError as ioe:
        print(ioe)
    except Exception as e:
        print(e)
    return file +  "_resize." + ext

def resizeobj(path, imagen, obj, width, height):
    try:
        new_size = int(width), int(height)
        file, ext = os.path.splitext(imagen)
        formato = obtener_formato(ext[1:])
        obj.resize(new_size, Image.LANCZOS)
        obj.save(path +"/"+ file +  "_resize_"+ width +'x'+ height + ext, formato)
    except IOError as ioe:
        print(ioe)
    except Exception as e:
        print(e)
    return file +  "_resize_" + width +'x'+ height + ext

def resize_force(path, imagen, obj, width, height):
    try:
        new_size = int(width), int(height)
        file, ext = os.path.splitext(imagen)
        formato = obtener_formato(ext[1:])

        obj.thumbnail(new_size)
        obj.save(path +"/"+ file +  "_resize_"+ width +'x'+ height + ext, formato)
    except IOError as ioe:
        print(ioe)
    except Exception as e:
        print(e)
    return file +  "_resize_" + width +'x'+ height + ext

def transform(path, imagen):
    try:
        file, ext = os.path.splitext(imagen)
        formato = obtener_formato(ext[1:])
        im = Image.open(open(path +"/"+ imagen, 'rb'))

        rgb2xyz = (
        0.412453, 0.357580, 0.180423, 0,
        0.212671, 0.715160, 0.072169, 0,
        0.019334, 0.119193, 0.950227, 0 )
        out = im.convert("RGB", rgb2xyz)
        out.save(path +"/"+ file + "_trans"+ext, formato)
    except IOError as ioe:
        print(ioe)
    except Exception as e:
        print(e)

def obtener_formato(extension):
    if (extension.upper() in ['JPG','JPEG']):
        return 'JPEG'
    if (extension.upper() in ['PNG']):
        return 'PNG'

def put_object(path, file):
    session = boto3.Session(
        region_name = region
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    full_path = temp_path + path +'/'+ file
    s3_path = path +'/'+ file

    try:
        with open(full_path, 'rb') as data:
            bucket.put_object(Key=s3_path, Body=data)
            object_acl = s3.ObjectAcl(bucket_name,s3_path)
            object_acl.put(ACL='public-read-write')
            print(s3_path)
    except Exception as e:
        print(e)
    return s3_path

def get_object(path, file):

    s3 = boto3.resource('s3')
    obj = None
    try:
        obj = s3.Bucket(bucket_name).download_file(path+'/'+ file, temp_path + path +'/'+ file)
        rekognize(path+'/'+ file)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    return obj

def ejecutar_operaciones(tipo, url, carpeta, file, *params):
    url.split()
    #get_object(carpeta, file)
    img = ''
    new_url= ''

    if(tipo == "resize_bin"):
        img = resize(temp_path + carpeta, file, params[0], params[1])
        new_url =put_object(carpeta, img)
        print("resizing de imagen "+ file)
    elif(tipo == "resize"):
        obj = get_filename_from_url(url)
        img = resize_force(temp_path + carpeta, file, obj, params[0], params[1])

        new_url = put_object(carpeta, img)
    elif(tipo == "tumbnail"):
        img = create_tumbnail(temp_path + carpeta, file, params[0], params[1])
        put_object(carpeta, img)
        print("imagen tumbnail "+ file)
    elif(tipo == "transform"):
        transform(temp_path + carpeta, file)
        print("transformacion de imagen "+ file)
    elif(tipo == "getcolor"):
        obj = get_filename_from_url(url)
        file, ext = os.path.splitext(file)
        formato = obtener_formato(ext[1:])
        obj.save(temp_path +  carpeta +"/"+ file + ext, formato)
        img = get_colors(temp_path +  carpeta, file + ext, 9, True)
        new_url = put_object(carpeta, img)
    return new_url

def get_filename_from_url(url):
    if(is_downloadable(url)):
        r = requests.get(url, allow_redirects=True)
        return Image.open(BytesIO(r.content))

def is_downloadable(url):
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    if h.status_code in [204, 401, 403, 404, 500]:
        return False
    return True

def ImageToBytes(img):
    data = None
    with BytesIO() as output:
        img.save(output, 'BMP')
        data = output.getvalue()
    return data

def rekognize(fileName):
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':
    {'Bucket':bucket_name,'Name':fileName}})
    print('Detected labels for ' + fileName)

    for label in response['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))

def average_colour(image):

    colour_tuple = [None, None, None]
    for channel in range(3):
        # Get data for one channel at a time
        pixels = image.getdata(band=channel)
        values = []
        for pixel in pixels:
            values.append(pixel)
        colour_tuple[channel] = sum(values) / len(values)
    return tuple(colour_tuple)

def rgb2hex(pixels):
    r, g, b, a = pixels # just ignore the alpha channel
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)



'''
def most_frequent_colour(image):
    get_centered_image()
    get_dominant_color(image)
    w, h = image.size
    pixels = image.getcolors(w * h)
    black = (0,0,0, 255)
    white = (255,255,255,255)
    gray = (255,255,255,0)
    sum = i = 0.0

    for x in pixels:
        i += 1
        if x[1] in [black, white, gray]:
            pixels.remove(x)
        sum += x[0]

    promedio  = int(sum/i)
    most_frequent_pixel = second_frequent_pxl = third_frequent_pxl = fourth_frequent_pxl = (promedio,pixels[0][1])

    for count, colour in pixels:
        if colour not in [black,white,gray]:
            if count > most_frequent_pixel[0]:
                second_frequent_pxl = most_frequent_pixel
                most_frequent_pixel = (count, colour)
            elif count < third_frequent_pxl[0]:
                fourth_frequent_pxl = third_frequent_pxl
                third_frequent_pxl = (count, colour)

    return str(rgb2hex(most_frequent_pixel[1]))+ ',' + str(rgb2hex(second_frequent_pxl[1])) + ',' + str(rgb2hex(third_frequent_pxl[1])) + ',' + str(rgb2hex(fourth_frequent_pxl[1]))
'''