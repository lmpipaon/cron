import jwt
import datetime as dt
import requests
import warnings
import pytz

warnings.simplefilter("ignore")

WRITE_APY_KEY_Thingspeak="GKIUIBEY6P95P7U7"

PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCWNlPFKrxpjVP5
x0nTsb/jRdV4/VFIoqYuO3evdDunwFc9r0RkzDqv2KAvJNLPLbbeLhxWe3asTWwK
3LBPhsO7zZc0KPIXMB1uZcragNTM1HlmAH/2ADBIgeG6YRqJ2yrZrNACZOFeEogV
s8d4186hEIvy6L9hfgz4+vLcIi4Xhi2RbbkDcRPUojDEyOAmVBeCZawRO4K3GxkF
IIUjqwwg8anJI6G9tPu9+qjANv9WhBsZP0odRUlZdaAPklrmbt0umh97MthGhRec
VXTas0AK2OIUv/qYbpkMgQ+cj3tKk3snzMb/p8r2sO04jQNWMgIyb8nLCgvyGbjz
aTfOlDXRAgMBAAECggEAQHFGNwxCkLYFFN+emKdlP0eycZmbyaGd0a/JhQhEn48w
3lHW8bd8Zfx1nEQb/K4MCf2WQrPtEbaVZ4OOUE/soSFugP4f/jqyJa6d/GfQ4580
BcKpIwypqjGueZs3G3VfSMuO4bgNx6IDp+vc48cR6p+Cqs+Xa2f8gMSIdFBlnclW
Fx2OgPEsh8S+sRHlEM6Cbh9EaFli1Iso+Ck+2AoBtANzi1qr6gV6sOg/PaXIgNSf
HIvwZRqjRZ1YqEFkB6QKlBXhZoxc0Sanm8NB5zSKxqVM7wCrgwJkfoOs7kbFcGMa
LqQqdZq0u23yi46bsnSGcB+3N/OWInYdoRzCrDK/0QKBgQC3TTNoeMwvisiD76CX
inpimNKs5tyIuhBDUEicBnmpmPNX+RHg496wubYR5iFsW6kzscIbhizZtGwJdzrr
fwPktgtNxfxoIcSd182Od0wx8LjTI8X2ko8YcbrafEWwzH1ZJOo5kRSFYTyiM0CI
JY1SadyOOCzN5XIDnmhh6Sj6TwKBgQDRyYe63eeHJw6bss60wNI2BHk5cR6qUbOz
/Lemq9gs1DYMCrkAzJE7ssS3I8DzGzkD394WpwUhOpxqSwnbWFbPUIcMTfsUDwN7
h8FbPUjO2NKPLN+yevKgrs3TEHKxn/0yo7uuhafBW5gTky7E0pp7E7o+vsxcVSqH
tEH1GY9l3wKBgBbMNEOfGo4jLbMzH38ZiwUuSq2UfQNIWPN2TcGSEJmmW0Wqxa15
yd2jC2EIhUmr0MyMJD82Hefpx7IZsStO/dX5SkifAjiVUpXrHDbG4aQoc2RXQ6za
J4/7vSilYimOFVz7+WG1iJ7aLCdkRndobD4+yl6p3/Cvw9FtZ0AeNqmDAoGBAIi7
nK6sEUqipz/N5DIldx1j/wr0crM5+zF1ptGIMabOTce9eWVO794EH3jqYclR1fBz
ihIjnBFTXT1eWTdQtYv8BXl8nggt3Ow3yEvKftjqsxpEeiyfO+KE7HwDvW2ORH4r
/5i5XmSFaXJgvNvmFG/hpMNeol4P2F+ImnDAzxjrAoGAT2Zp49C9MzTs01Z9FfOV
ser1koLRNHJMFV0QpRGQQb0CBEnJRcuE+PSZ/YP7JruRpRku3Icg/E0MJfeaEAnI
W7wjXDDso668ktwACXKNo43Tz9Fhkn1iPWRCh7SSMD42b3pXodR6fq9jje6HUKdR
j6PB5tLx6T+TsNUoeRgGy6Y=
-----END PRIVATE KEY-----"""

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
            
            print(f"\n📍 ESTACIÓN ALEGRÍA (C056)")
            print(f"ÚLTIMA VÁLIDA (LOCAL): {hora_local}")
            print(f"NIVEL:  {nivel:.2f} m")
            print(f"CAUDAL: {caudal:.3f} m³/s")

            enviar_thingspeak(  WRITE_APY_KEY_Thingspeak, field1=nivel, field2=caudal )


            return

    print("Datos recibidos pero todos son nulos.")

if __name__ == "__main__":
    main()