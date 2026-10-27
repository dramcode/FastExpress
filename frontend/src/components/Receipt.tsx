import { motion } from "framer-motion";

import type { ApiEnvelope, QuoteData, Ticket } from "../types";

type ReceiptProps = {
  quote: QuoteData | null;
  error: ApiEnvelope<QuoteData> | null;
  phase: "loading" | "ready" | "rejected" | "invalid" | "offline" | "idle";
  onFix: () => void;
  tickets: Ticket[];
};

export function Receipt({ quote, error, phase, onFix, tickets }: ReceiptProps) {
  const rejected = phase === "rejected" || phase === "invalid" || phase === "offline";
  return (
    <aside className="slip-column" aria-live="polite">
      <article className={rejected ? "slip slip--stop" : "slip"} key={quote?.total ?? error?.code ?? phase}>
        <p className="slip__kicker">Guía de cotización</p>
        <h2>{rejected ? "Rechazada" : "Pre-guía"}</h2>
        <p className="slip__message">
          {phase === "loading" && "Calculando en muelle…"}
          {phase === "offline" && "No hay conexión con el servicio. Inicie la API en el puerto 8000."}
          {phase !== "loading" && phase !== "offline" && (error?.message || (quote ? "Cotización calculada correctamente." : "Esperando peso."))}
        </p>
        {quote && phase === "ready" && (
          <motion.dl initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }}>
            <Row label="Peso" value={`${quote.weight_kg} kg`} />
            <Row label="Tarifa por kg" value={`${quote.rate_per_kg} USD`} />
            <Row label="Base" value={quote.base_fee} />
            <Row label="Cargo por peso" value={quote.weight_charge} />
            <Row label="Subtotal" value={quote.subtotal} />
            <Row label="Recargo" value={quote.surcharge_amount} />
            <Row label="Descuento" value={quote.discount_amount} />
            <div className="slip__total">
              <span>Monto</span>
              <strong>
                {quote.total} <small>{quote.currency}</small>
              </strong>
            </div>
          </motion.dl>
        )}
        <button type="button" className="fix" onClick={onFix} disabled={phase !== "ready"}>
          Fijar guía
        </button>
      </article>
      <ul className="stack">
        {tickets.map((ticket) => (
          <li key={ticket.folio}>
            <span>{ticket.folio}</span>
            <strong>
              {ticket.total} {ticket.currency}
            </strong>
          </li>
        ))}
      </ul>
    </aside>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
