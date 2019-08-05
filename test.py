from PIL import Image
from boto3.resources import response
import unittest
import funciones

obj = funciones.get_object('images/FotoProductoFondoBlancoWebRedes','200084505.png')
img = Image.open('c:/temp/images/FotoProductoFondoBlancoWebRedes/200084505.png')
class ApiTest(unittest.TestCase):

    def test_getImage(self):
        self.assertIsNone(obj,"Error no se devolvio una imagen")

    def test_getResponse(self):
        self.assertIs(obj, None, "error no hay una respuesta")

    def test_resizeImage(self):
        self.assertIs(Image.isImageType(img),True, "Error no es una imagen")

    def test_url_return(self):
        url= 'images/FotoProductoFondoBlancoWebRedes'
        self.assertFalse(url == None,"Error no devuelve una url valida")

if __name__ == '__main__':
    unittest.main()