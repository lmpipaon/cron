import jwt
import datetime as dt
import requests
import warnings
import pytz

warnings.simplefilter("ignore")

WRITE_APY_KEY_Thingspeak=os.getenv('WRITE_KEY')

PRIVATE_KEY = os.getenv('MY_PRIVATE_KEY')

def _create_token():
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    payload = {"aud": "met01.apikey", "iss": "AMVISA_APP", "exp": now + 3600, "version": "1.0.0", "iat": now - 30, "email": "lpipaon@amvisa.onl"}
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

def utc_to_local(hora_str_utc, fecha_base_utc):
    tz_local = pytz.timezone('Europe/Madrid')
    h_inicio = hora_str_utc.split(' - ')[0]
    h, m = map(int, h_inicio.split(':'))
    dt_utc = fecha_base_utc.replace(hour=h, minute=m, second=0, microsecond=0)
    # Convertimos de aware UTC a aware Local
    return dt_utc.astimezone(tz_local).strftime('%H:%M')

def enviar_thingspeak(api_key, **fields):
    """
    Envía hasta 8 campos a ThingSpeak.
    Uso: enviar_thingspeak("TU_KEY", field1=10.5, field2=20, field8=44.2)
    """
    url = "https://api.thingspeak.com/update"
    
    # Preparamos los datos con la API Key
    payload = {'api_key': api_key}
    
    # Añadimos solo los fields que pases como argumento (field1...field8)
    payload.update(fields)
    
    try:
        response = requests.get(url, params=payload)
        if response.status_code == 200 and response.text != '0':
            print(f"Éxito. Entrada ID: {response.text}")
        else:
            print(f"Fallo. Respuesta: {response.text} (Si es 0, espera 15s)")
    except Exception as e:
        print(f"Error de conexión: {e}")

def main():
    token = _create_token()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    ahora_utc = dt.datetime.now(dt.timezone.utc)
    
    data = None
    fecha_ref = None

    # Intentamos la hora actual y las dos anteriores
    for i in range(3):
        objetivo = ahora_utc - dt.timedelta(hours=i)
        url = f"https://api.euskadi.eus/euskalmet/readings/forStation/C056/RM02/measures/measuresForWater/sheet_level_1/at/{objetivo.year}/{objetivo.month:02d}/{objetivo.day:02d}/{objetivo.hour:02d}"
        res = requests.get(url, headers=headers, verify=False)
        if res.status_code == 200:
            data = res.json()
            fecha_ref = objetivo
            break

    if not data:
        print("No hay datos disponibles.")
        return

    values = data.get('values', [])
    slots = data.get('slots', [])

    # Buscar la última lectura que no sea None
    for i in range(len(values)-1, -1, -1):
        if values[i] is not None:
            hora_local = utc_to_local(slots[i]['rangeDesc'], fecha_ref)
            nivel = float(values[i])
            caudal = round(1.85 * (nivel ** 1.6), 3)
            
            print(f"\nESTACIÓN ALEGRÍA (C056)")
            print(f"ÚLTIMA VÁLIDA (LOCAL): {hora_local}")
            print(f"NIVEL:  {nivel:.2f} m")
            print(f"CAUDAL: {caudal:.3f} m³/s")

            enviar_thingspeak(  WRITE_APY_KEY_Thingspeak, field1=nivel, field2=caudal )


            return

    print("Datos recibidos pero todos son nulos.")

if __name__ == "__main__":
    main()
