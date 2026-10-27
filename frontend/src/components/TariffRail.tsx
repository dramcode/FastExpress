import type { TariffBoard } from "../types";

type TariffRailProps = {
  board: TariffBoard | null;
  failed: boolean;
};

export function TariffRail({ board, failed }: TariffRailProps) {
  return (
    <aside className="rail" aria-label="Tarifario">
      <p className="rail__kicker">Tarifario vivo</p>
      <h2>Reglas de muelle</h2>
      {failed && <p className="rail__error">El tarifario no respondió.</p>}
      {!board && !failed && <p className="rail__wait">Leyendo tarifario…</p>}
      {board && (
        <>
          <p className="rail__base">
            Base <strong>{board.base_fee}</strong> {board.currency}
          </p>
          <ul>
            {board.weight_bands.map((band) => (
              <li key={band.min_kg}>
                <span>
                  {band.min_kg}–{band.max_kg} kg
                </span>
                <strong>
                  {band.rate_per_kg} /kg
                </strong>
              </li>
            ))}
          </ul>
          <p className="rail__cap">Tope {board.max_weight_kg} kg. Por encima, el muelle rechaza la guía.</p>
          <ul className="rail__pills">
            {board.client_types.map((item) => (
              <li key={item.code}>
                {item.label} · {percent(item.discount_rate)}
              </li>
            ))}
            {board.shipping_types.map((item) => (
              <li key={item.code}>
                {item.label} · {percent(item.surcharge_rate)} recargo
              </li>
            ))}
          </ul>
        </>
      )}
    </aside>
  );
}

function percent(rate: string): string {
  return `${Math.round(Number(rate) * 100)}%`;
}
