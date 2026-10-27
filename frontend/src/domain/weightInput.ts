export type WeightCheck =
  | { ok: true; value: string }
  | { ok: false; pending: boolean; message: string };

export function checkWeight(raw: string): WeightCheck {
  const trimmed = raw.trim();
  if (!trimmed) {
    return { ok: false, pending: false, message: "Ingrese el peso para cotizar." };
  }
  if (trimmed.endsWith(".") || trimmed.endsWith(",")) {
    return { ok: false, pending: true, message: "" };
  }
  const normalized = trimmed.replace(",", ".");
  if (!/^-?\d+(\.\d+)?$/.test(normalized)) {
    return { ok: false, pending: false, message: "El peso debe ser un número decimal." };
  }
  const fraction = normalized.split(".")[1] ?? "";
  if (fraction.length > 2) {
    return {
      ok: false,
      pending: false,
      message: "El peso admite como máximo dos decimales.",
    };
  }
  return { ok: true, value: normalized };
}
