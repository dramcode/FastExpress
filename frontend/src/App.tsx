import { useEffect, useMemo, useRef, useState } from "react";

import { fetchHealth, fetchTariffs, requestQuote } from "./api";
import { Instruments } from "./components/Instruments";
import { Lane } from "./components/Lane";
import { Receipt } from "./components/Receipt";
import { TariffRail } from "./components/TariffRail";
import { checkWeight } from "./domain/weightInput";
import type { ApiEnvelope, QuoteData, TariffBoard, Ticket } from "./types";

type Phase = "loading" | "ready" | "rejected" | "invalid" | "offline" | "idle";

export function App() {
  const [weight, setWeight] = useState("2.50");
  const [clientType, setClientType] = useState("NUEVO");
  const [shippingType, setShippingType] = useState("ESTANDAR");
  const [board, setBoard] = useState<TariffBoard | null>(null);
  const [boardFailed, setBoardFailed] = useState(false);
  const [online, setOnline] = useState(true);
  const [quote, setQuote] = useState<QuoteData | null>(null);
  const [error, setError] = useState<ApiEnvelope<QuoteData> | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [clock, setClock] = useState(() => formatClock(new Date()));
  const requestId = useRef(0);

  useEffect(() => {
    const timer = window.setInterval(() => setClock(formatClock(new Date())), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((up) => {
        if (active) {
          setOnline(up);
        }
      })
      .catch(() => {
        if (active) {
          setOnline(false);
        }
      });
    fetchTariffs()
      .then((tariffs) => {
        if (active) {
          setBoard(tariffs);
        }
      })
      .catch(() => {
        if (active) {
          setBoardFailed(true);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      const checked = checkWeight(weight);
      if (!checked.ok) {
        if (checked.pending) {
          return;
        }
        setQuote(null);
        setError({
          success: false,
          message: checked.message,
          code: "INVALID_WEIGHT",
          data: null,
          errors: [{ field: "weight_kg", message: checked.message }],
        });
        setPhase("invalid");
        return;
      }
      const current = ++requestId.current;
      setPhase("loading");
      requestQuote({
        weight_kg: checked.value,
        client_type: clientType,
        shipping_type: shippingType,
      })
        .then((body) => {
          if (current !== requestId.current) {
            return;
          }
          if (body.success && body.data) {
            setQuote(body.data);
            setError(null);
            setPhase("ready");
            setOnline(true);
            return;
          }
          setQuote(null);
          setError(body);
          setPhase("rejected");
        })
        .catch(() => {
          if (current !== requestId.current) {
            return;
          }
          setOnline(false);
          setQuote(null);
          setError(null);
          setPhase("offline");
        });
    }, 280);
    return () => window.clearTimeout(handle);
  }, [weight, clientType, shippingType]);

  const hint = useMemo(() => {
    if (phase === "invalid" || phase === "rejected") {
      return error?.errors.find((item) => item.field === "weight_kg")?.message ?? error?.message ?? null;
    }
    return null;
  }, [error, phase]);

  function fixTicket() {
    if (!quote || phase !== "ready") {
      return;
    }
    const folio = `FX-${Date.now().toString(36).toUpperCase()}`;
    setTickets((current) => [{ ...quote, folio }, ...current].slice(0, 3));
  }

  return (
    <main className="dock">
      <header className="mast">
        <div>
          <p className="mast__mark">FastExpress</p>
          <p className="mast__sub">Muelle 04 · cotización de envíos</p>
        </div>
        <p className={online ? "lamp lamp--on" : "lamp"}>{online ? "API en línea" : "API fuera de línea"}</p>
        <p className="mast__clock">
          <span>Turno noche</span>
          <strong>{clock}</strong>
        </p>
      </header>

      <section className="stage">
        <TariffRail board={board} failed={boardFailed} />
        <Lane
          express={shippingType === "EXPRESS"}
          blocked={error?.code === "WEIGHT_LIMIT_EXCEEDED"}
          caption={quote ? `${quote.weight_kg} kg · ${quote.client_type}` : `${weight || "—"} kg`}
        />
        <Receipt quote={quote} error={error} phase={phase} onFix={fixTicket} tickets={tickets} />
      </section>

      <Instruments
        weight={weight}
        onWeight={setWeight}
        client={clientType}
        onClient={setClientType}
        shipping={shippingType}
        onShipping={setShippingType}
        clients={board?.client_types ?? []}
        shippings={board?.shipping_types ?? []}
        hint={hint}
      />
    </main>
  );
}

function formatClock(date: Date): string {
  return date.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
}
