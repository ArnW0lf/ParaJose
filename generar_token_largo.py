import requests

print("--- GENERADOR DE TOKEN DE LARGA DURACIÓN (60 DÍAS) ---")

# 1. PEGA AQUÍ TUS DATOS (Saca esto de developers.facebook.com -> Configuración -> Básica)
APP_ID = "770545109342743" 
APP_SECRET = "3e699e2cf01e641ec2ffc07d8488f54a"

# 2. PEGA AQUÍ EL TOKEN DE USUARIO CORTO (Del Graph API Explorer)
SHORT_TOKEN = "EAAK8zoOGmhcBPZBfRk3xuPU7ZBO2N19hjPkkSi9KybeYdYurBoFUteZAUWfc1JuADUCeb6Qq2fcajrLNparHvm7MuYf5V7Gg4pigA2GbNWckiYz7PFnLFdsB2gclZBuIZCpTTwvrT1OmALtZBIF03myAOlZBPrzO8RJQQpqfdroYmN1ozaH0n1Rr1IrbG7ZAEcMGZBDif5tlUEcTbzn6Xuj3HF1OAUEgz79b5Y0pWZA5kyiTkv9kdQVH50prfIvDIiZCcpEJFHF1KMwaZCtw3IQS"

# 3. TU ID DE PÁGINA (El que tienes en el .env)
PAGE_ID = "818138381393500" 

def obtener_token_largo():
    # PASO A: Canjear Token Corto de Usuario -> Token Largo de Usuario
    url_exchange = "https://graph.facebook.com/v19.0/oauth/access_token"
    params_exchange = {
        'grant_type': 'fb_exchange_token',
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'fb_exchange_token': SHORT_TOKEN
    }
    
    print("\n1. Solicitando Token de Usuario de Larga Duración...")
    resp = requests.get(url_exchange, params=params_exchange)
    data = resp.json()
    
    if 'access_token' not in data:
        print("❌ Error en Paso 1:", data)
        return

    long_user_token = data['access_token']
    print("✅ Token de Usuario Extendido obtenido.")

    # PASO B: Usar Token Largo de Usuario -> Obtener Token de Página (Que hereda la duración)
    print("\n2. Obteniendo Token de Página Definitivo...")
    url_page = f"https://graph.facebook.com/v19.0/{PAGE_ID}"
    params_page = {
        'fields': 'access_token',
        'access_token': long_user_token
    }
    
    resp_page = requests.get(url_page, params=params_page)
    data_page = resp_page.json()
    
    if 'access_token' in data_page:
        final_token = data_page['access_token']
        print("\n🎉 ¡ÉXITO! ESTE TOKEN DURA 60 DÍAS O MÁS:")
        print("-" * 60)
        print(final_token)
        print("-" * 60)
        print("👉 Copia esto a tu .env (FACEBOOK_ACCESS_TOKEN) y olvídate de renovar por meses.")
    else:
        print("❌ Error en Paso 2:", data_page)

if __name__ == "__main__":
    obtener_token_largo()