import httpx

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "chuny@gmail.com"
PASSWORD = "1234x5678"   # pon tu password real
PAQUETE_ID = 2        # id del paquete que quieres testear

def main():
    with httpx.Client() as client:
        # 1. Login
        login_res = client.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        print("Login status:", login_res.status_code)
        print("Login response:", login_res.json())

        token = login_res.json().get("access_token")
        if not token:
            print("❌ No se pudo obtener token")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check favorito
        fav_res = client.get(f"{BASE_URL}/favoritos/check/{PAQUETE_ID}", headers=headers)
        print("Check favorito status:", fav_res.status_code)
        print("Check favorito response:", fav_res.json())

if __name__ == "__main__":
    main()
