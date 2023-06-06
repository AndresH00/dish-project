import os
import json
import mysql.connector
import boto3


def get_secret(secret_arn):
    """
    Obtiene el valor del secreto almacenado en AWS Secrets Manager.

    Args:
        secret_arn (str): ARN del secreto.

    Returns:
        dict: Diccionario con el valor del secreto.
    """
    
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_arn)
    if 'SecretString' in response:
        secret = json.loads(response['SecretString'])
        return secret
    else:
        secret = response['SecretBinary']
        return secret


def lambda_handler(event, context):
    """
    Función principal de la lambda para hacer el update en la tabla suscriptores de la bd.

    Args:
        event (dict): Evento que contiene los datos del suscriptor.
        context (object): Objeto de contexto de la lambda.

    Returns:
        dict: Respuesta de la lambda.
    """
    print(event)
    body = json.loads(event['body'])
    suscriptor = body['suscriptor'] if 'suscriptor' in body else None
    info_nombre = suscriptor['info_nombre'] if 'info_nombre' in suscriptor else None
    nombre = info_nombre['nombre'] if 'nombre' in info_nombre else None
    apellido_materno = info_nombre.get('apellido_materno', '')
    apellido_paterno = info_nombre.get('apellido_paterno', '')
    edad = suscriptor['edad'] if 'edad' in suscriptor else None
    telefono_celular = suscriptor['telefono_celular'] if 'telefono_celular' in suscriptor else None

    if suscriptor == None:
        return {
            'statusCode': 400,
            'body': 'La informacion del suscriptor es obligatoria.'
        }
    if nombre == None or telefono_celular == None:
        return {
            'statusCode': 400,
            'body': 'El nombre y el teléfono celular son obligatorios.'
        }
    if not isinstance(edad, int) or edad < 0:
        return {
            'statusCode': 400,
            'body': 'La edad debe ser un número entero positivo.'
        }
    if not isinstance(telefono_celular, str) or len(telefono_celular) != 10:
        return {
            'statusCode': 400,
            'body': 'El teléfono celular debe ser una cadena de 10 dígitos.'
        }
    secret_arn = os.environ['SECRET_ARN']

    try:
        # Retorna el valor del secreto que contiene la password, host y usuario
        secret = get_secret(secret_arn)

        conn = mysql.connector.connect(
            host=secret['host'],
            user=secret['username'],
            password=secret['password'],
            database=os.environ['DB_DATABASE']
        )
        cursor = conn.cursor()

        # Executar query para actualizar el registro
        sql = "UPDATE suscriptores SET nombre = %s, apellido_materno = %s, apellido_paterno = %s, edad = %s WHERE telefono_celular = %s"
        values = (nombre, apellido_materno,
                  apellido_paterno, edad, telefono_celular)
        cursor.execute(sql, values)

        # Confirmar cambios en la base de datos
        conn.commit()

        # Cerrar la conexion de la base de datos
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': 'Registro actualizado exitosamente.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
