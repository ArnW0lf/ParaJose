import requests

# 1. PEGA AQUÍ EL TOKEN QUE TIENES AHORA MISMO EN EL EXPLORADOR
# (El que dice "Token del usuario" en el menú, no importa)
USER_TOKEN ="EAAK8zoOGmhcBPZBfRk3xuPU7ZBO2N19hjPkkSi9KybeYdYurBoFUteZAUWfc1JuADUCeb6Qq2fcajrLNparHvm7MuYf5V7Gg4pigA2GbNWckiYz7PFnLFdsB2gclZBuIZCpTTwvrT1OmALtZBIF03myAOlZBPrzO8RJQQpqfdroYmN1ozaH0n1Rr1IrbG7ZAEcMGZBDif5tlUEcTbzn6Xuj3HF1OAUEgz79b5Y0pWZA5kyiTkv9kdQVH50prfIvDIiZCcpEJFHF1KMwaZCtw3IQS"

# 2. PEGA AQUÍ EL ID DE TU PÁGINA (Ya lo tienes en tu .env)
PAGE_ID = "818138381393500" 

print("--- CANJEANDO TOKEN DE USUARIO POR TOKEN DE PÁGINA ---")

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}"
params = {
    'fields': 'access_token',
    'access_token': USER_TOKEN
}

try:
    response = requests.get(url, params=params)
    data = response.json()

    if 'access_token' in data:
        page_token = data['access_token']
        print("\n✅ ¡ÉXITO! AQUÍ ESTÁ TU TOKEN DE PÁGINA:")
        print("-" * 60)
        print(page_token)
        print("-" * 60)
        print("\n👉 Copia este token nuevo y ponlo en tu archivo .env en FACEBOOK_ACCESS_TOKEN")
    else:
        print("\n❌ Error al canjear:")
        print(data)

except Exception as e:
    print(f"Error de conexión: {e}")