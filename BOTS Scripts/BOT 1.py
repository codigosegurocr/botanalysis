from playwright.sync_api import sync_playwright

def ejecutar_login(page):
    # Ir a la página de login
    page.goto("http://localhost:5032/", wait_until="domcontentloaded")

    # Esperar elementos
    page.wait_for_selector("#username")
    page.wait_for_selector("#password")
    page.wait_for_selector("#submit-button")

    # Llenar formulario
    page.fill("#username", "usuarioEjemplo")
    page.fill("#password", "contraseñaEjemplo")
    page.click("#submit-button")

    # Esperar un poco antes de terminar la iteración
    page.wait_for_timeout(1000)  # 1 segundo

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    num_repeticiones = 1
    for i in range(num_repeticiones):
        print(f"--- Iteración {i+1} ---")
        ejecutar_login(page)

    browser.close()
