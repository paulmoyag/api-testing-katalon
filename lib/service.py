from flask_restful import Resource, Api
import json
from json import dumps
from flask_jsonpify import jsonify
from funciones import is_downloadable, ejecutar_operaciones
app = Flask(__name__)
api = Api(app)

class Imagen(Resource):
    def get(self):
        s3_url, url, op_type,size  = ''
        try:
            if(request.args.get('url') == None):
                return 'invocacion incorrecta', 403
            else:
                url = request.args.get('url')

            if(request.args.get('op_type') == None):
                return 'invocacion incorrecta', 403
            else:
                op_type = request.args.get('op_type')

            if(request.args.get('size')!=None):
                size = request.args.get('size')

                if( is_downloadable(new_url)):

                    paths = url.split('&')
                    file = paths[len(paths)-1]
                    carpeta = paths[len(paths)-3] + '/' + paths[len(paths)-2]
                    s3_url += 'https://'+ paths[0] + '/'

                    if (op_type == 'resize'):
                        #if(size !=None):
                        x , y = size.split(',')
                        s3_url += ejecutar_operaciones("resize", new_url, carpeta, file, x, y)
                        #else:
                            #s3_url += ejecutar_operaciones("resize", new_url, carpeta, file, "","")

                    elif(op_type == 'getcolor'):
                        s3_url += ejecutar_operaciones("getcolor", new_url, carpeta, file, "","")
                    #else:
                        #return {'msg':'Opcion no encontrada'},404
                else:
                    return {'msg':'No se encontró el archivo o no tiene permisos'}, 404
            return {'url_s3' : s3_url} ,200
        except Exception as ex:
            return {'msg':str(ex)}, 500

class Tracks(Resource):
    def get(self):
        result = {'data': ''}
        return jsonify(result)

class Imagen_Name(Resource):
    def get(self, Imagen_id):
        result = {'data': ''}
        return jsonify(result)

#api.add_resource(Imagen, '/resizeImage/<string:url>') # Route_1
api.add_resource(Imagen, '/resizeImage') # Route_1
api.add_resource(Tracks, '/tracks') # Route_2
api.add_resource(Imagen_Name, '/Imagen/<Imagen_id>') # Route_3

def main(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return {"statusCode": 200}