import { motion } from "framer-motion";

type LaneProps = {
  express: boolean;
  blocked: boolean;
  caption: string;
};

export function Lane({ express, blocked, caption }: LaneProps) {
  const className = blocked ? "lane lane--blocked" : express ? "lane lane--express" : "lane";
  return (
    <section className={className} aria-label="Carril de despacho">
      <div className="lane__meta">
        <span>{express ? "Carril express · prioridad de muelle" : "Carril estándar · ventana regular"}</span>
        <span>{caption}</span>
      </div>
      <div className="lane__track">
        <div className="crate" aria-hidden="true">
          <span>FX</span>
        </div>
        <motion.div
          className="barrier"
          initial={false}
          animate={blocked ? { y: 0, opacity: 1 } : { y: -78, opacity: 0 }}
          transition={{ type: "spring", stiffness: 280, damping: 22 }}
        >
          <strong>Límite excedido</strong>
        </motion.div>
      </div>
    </section>
  );
}
