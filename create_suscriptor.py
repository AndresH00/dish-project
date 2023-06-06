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
        # Handle binary secrets if necessary
        secret = response['SecretBinary']
        return secret


def lambda_handler(event, context):
    """
    Función principal de la lambda para hacer un create de un suscriptor en la tabla suscriptores de la bd.

    Args:
        event (dict): Evento que contiene los datos del suscriptor.
        context (object): Objeto de contexto de la lambda.

    Returns:
        dict: Respuesta de la lambda.
    """
    print(event)
    body = json.loads(event['body'])
    # Extract data from the request body
    suscriptor = body['suscriptor'] if 'suscriptor' in body else None
    info_nombre = suscriptor['info_nombre'] if 'info_nombre' in suscriptor else None
    nombre = info_nombre['nombre'] if 'nombre' in info_nombre else None
    apellido_materno = info_nombre.get('apellido_materno', '')
    apellido_paterno = info_nombre.get('apellido_paterno', '')
    edad = suscriptor['edad'] if 'edad' in suscriptor else None
    telefono_celular = suscriptor['telefono_celular'] if 'telefono_celular' in suscriptor else None

    # Valida la informacion
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
        # Retrieve the password from the secret
        secret = get_secret(secret_arn)
        conn = mysql.connector.connect(
            host=secret['host'],
            user=secret['username'],
            password=secret['password'],
            database=os.environ['DB_DATABASE']
        )

        cursor = conn.cursor()

        # Execute the SQL query to insert the record
        sql = "INSERT INTO suscriptores (nombre, apellido_materno, apellido_paterno, edad, telefono_celular) VALUES (%s, %s, %s, %s, %s)"
        values = (nombre, apellido_materno,
                  apellido_paterno, edad, telefono_celular)
        cursor.execute(sql, values)

        # Confirm the changes in the database
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': 'Registro creado exitosamente.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
