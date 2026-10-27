"""Drive the running FastExpress dock and save desktop screenshots."""

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "docs" / "evidence"
APP = "http://localhost:5173"
COVERAGE = OUT / "coverage-html" / "index.html"


def shot(page, name: str) -> None:
    page.screenshot(path=str(OUT / name), full_page=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(APP, wait_until="networkidle")
        page.get_by_text("Cotización calculada correctamente.").wait_for()
        page.get_by_text("10.00").first.wait_for()
        shot(page, "01-estandar-nuevo.png")

        page.get_by_role("button", name="Frecuente").click()
        page.get_by_role("button", name="Express", exact=False).click()
        page.get_by_text("11.25").wait_for()
        page.get_by_role("button", name="Fijar guía").click()
        page.get_by_text("Carril express").wait_for()
        shot(page, "02-frecuente-express.png")

        page.get_by_role("button", name="Nuevo").click()
        page.get_by_role("button", name="Estándar", exact=False).click()
        page.get_by_label("Peso en kilogramos").fill("5.00")
        page.get_by_text("15.00").first.wait_for()
        shot(page, "03-frontera-5-00.png")

        page.get_by_label("Peso en kilogramos").fill("5.01")
        page.get_by_text("25.04").first.wait_for()
        shot(page, "04-frontera-5-01.png")

        page.get_by_label("Peso en kilogramos").fill("22.00")
        page.locator(".slip__message").get_by_text("Límite excedido").wait_for()
        page.get_by_role("heading", name="Rechazada").wait_for()
        shot(page, "05-limite-excedido.png")

        page.get_by_label("Peso en kilogramos").fill("abc")
        page.get_by_text("El peso debe ser un número decimal.").first.wait_for()
        shot(page, "06-peso-invalido.png")

        page.goto(COVERAGE.as_uri(), wait_until="domcontentloaded")
        page.get_by_text("100%").first.wait_for()
        shot(page, "07-cobertura.png")
        browser.close()


if __name__ == "__main__":
    main()
