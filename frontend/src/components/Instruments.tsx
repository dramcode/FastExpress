import { motion } from "framer-motion";

type Option = { code: string; label: string };

type InstrumentsProps = {
  weight: string;
  onWeight: (value: string) => void;
  client: string;
  onClient: (value: string) => void;
  shipping: string;
  onShipping: (value: string) => void;
  clients: Option[];
  shippings: Option[];
  hint: string | null;
};

const FALLBACK_CLIENTS: Option[] = [
  { code: "NUEVO", label: "Nuevo" },
  { code: "FRECUENTE", label: "Frecuente" },
  { code: "VIP", label: "VIP" },
];

const FALLBACK_SHIPPING: Option[] = [
  { code: "ESTANDAR", label: "Estándar" },
  { code: "EXPRESS", label: "Express" },
];

export function Instruments({
  weight,
  onWeight,
  client,
  onClient,
  shipping,
  onShipping,
  clients,
  shippings,
  hint,
}: InstrumentsProps) {
  const numeric = Number(weight.replace(",", "."));
  const slider = Number.isFinite(numeric) ? Math.min(Math.max(numeric, 0), 25) : 0;
  const ratio = slider / 25;
  const hot = Number.isFinite(numeric) && numeric > 20;
  const clientOptions = clients.length > 0 ? clients : FALLBACK_CLIENTS;
  const shippingOptions = shippings.length > 0 ? shippings : FALLBACK_SHIPPING;

  function step(delta: number) {
    const current = Number.isFinite(numeric) ? numeric : 0;
    const next = Math.min(25, Math.max(0, current + delta));
    onWeight(next.toFixed(2));
  }

  return (
    <section className="instruments" aria-label="Controles de cotización">
      <article className="plate plate--scale">
        <header>
          <span>Báscula</span>
          <span>0–25 kg</span>
        </header>
        <div className="scale">
          <svg className="gauge" viewBox="0 0 140 78" aria-hidden="true">
            <path className="gauge__track" pathLength={100} d="M14 70 A52 52 0 0 1 126 70" />
            <path
              className={hot ? "gauge__value gauge__value--hot" : "gauge__value"}
              pathLength={100}
              strokeDasharray={`${ratio * 100} 100`}
              d="M14 70 A52 52 0 0 1 126 70"
            />
          </svg>
          <label className="scale__readout">
            <input
              aria-label="Peso en kilogramos"
              inputMode="decimal"
              value={weight}
              onChange={(event) => onWeight(event.target.value)}
            />
            <small>kg</small>
          </label>
        </div>
        <div className="scale__row">
          <button type="button" onClick={() => step(-0.5)} aria-label="Restar medio kilo">
            −0.50
          </button>
          <input
            className="scale__slider"
            type="range"
            min={0}
            max={25}
            step={0.01}
            value={slider}
            aria-label="Deslizar peso"
            onChange={(event) => onWeight(Number(event.target.value).toFixed(2))}
          />
          <button type="button" onClick={() => step(0.5)} aria-label="Sumar medio kilo">
            +0.50
          </button>
        </div>
        {hint && <p className="plate__hint">{hint}</p>}
      </article>

      <article className="plate">
        <header>
          <span>Sello de cliente</span>
          <span>Descuento</span>
        </header>
        <div className="seals">
          {clientOptions.map((option) => (
            <motion.button
              key={option.code}
              type="button"
              className={client === option.code ? `seal seal--${option.code.toLowerCase()} is-on` : `seal seal--${option.code.toLowerCase()}`}
              whileTap={{ scale: 0.94, rotate: -3 }}
              onClick={() => onClient(option.code)}
              aria-pressed={client === option.code}
            >
              {option.label}
            </motion.button>
          ))}
        </div>
      </article>

      <article className="plate">
        <header>
          <span>Carril</span>
          <span>Recargo</span>
        </header>
        <div className="lever" role="group" aria-label="Tipo de envío">
          {shippingOptions.map((option) => (
            <button
              key={option.code}
              type="button"
              className={shipping === option.code ? "lever__side is-on" : "lever__side"}
              onClick={() => onShipping(option.code)}
              aria-pressed={shipping === option.code}
            >
              <strong>{option.label}</strong>
              <span>{option.code === "EXPRESS" ? "+25% sobre subtotal" : "Sin recargo"}</span>
            </button>
          ))}
        </div>
      </article>
    </section>
  );
}
