from funciones import is_downloadable, ejecutar_operaciones

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
                    x , y = size.split(',')
                    s3_url += ejecutar_operaciones("resize", new_url, carpeta, file, x, y)

                elif(op_type == 'getcolor'):
                    s3_url += ejecutar_operaciones("getcolor", new_url, carpeta, file, "","")
            else:
                return {'msg':'No se encontró el archivo o no tiene permisos'}, 404
        return {'url_s3' : s3_url} ,200
    except Exception as ex:
        return {'msg':str(ex)}, 500

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