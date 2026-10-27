export type FieldError = {
  field: string;
  message: string;
};

export type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  code: string;
  data: T | null;
  errors: FieldError[];
};

export type QuoteData = {
  weight_kg: string;
  rate_per_kg: string;
  base_fee: string;
  weight_charge: string;
  subtotal: string;
  client_type: string;
  discount_rate: string;
  shipping_type: string;
  surcharge_rate: string;
  surcharge_amount: string;
  gross_amount: string;
  discount_amount: string;
  total: string;
  currency: string;
};

export type TariffBoard = {
  currency: string;
  base_fee: string;
  max_weight_kg: string;
  min_weight_kg: string;
  weight_bands: { min_kg: string; max_kg: string; rate_per_kg: string }[];
  client_types: { code: string; label: string; discount_rate: string }[];
  shipping_types: { code: string; label: string; surcharge_rate: string }[];
};

export type Ticket = QuoteData & { folio: string };
