# FastExpress — cotización de envíos

Módulo que calcula el monto de un envío en USD a partir del peso, el tipo de cliente y el tipo de envío.

## Cómo correrlo

1. Backend, desde `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --port 8000
```

2. Frontend, desde `frontend`:

```powershell
npm install
npm test
npm run dev
```

3. Abrir `http://localhost:5173`. La interfaz habla con `/api/v1` por el proxy de Vite.

## Cálculo

El peso completo usa la tarifa de su banda, no un tramo marginal.

| Paso | Regla |
| --- | --- |
| Base | 5.00 USD |
| 0.01 kg a 5.00 kg | 2.00 USD por kg |
| 5.01 kg a 20.00 kg | 4.00 USD por kg |
| Más de 20.00 kg | Rechazo: límite excedido |
| Nuevo / Frecuente / VIP | 0% / 10% / 20% después del recargo |
| Estándar / Express | 0% / +25% sobre el subtotal |

Cada importe se redondea al centavo, half-up. `Monto` es el total calculado; no es un campo de entrada.

## Pruebas

- Caja blanca: `backend/tests/whitebox` cubre los 7 caminos del algoritmo.
- Caja negra: `backend/tests/blackbox` cubre particiones, BVA y la tabla de decisión.
- Contrato HTTP: `backend/tests/api`.
- Entrada del cliente: `frontend` con `npm test`.

El informe de calidad está en `docs/Informe_Calidad_FastExpress.pdf`.
