import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  TransitBlueprint,
  TransitBlueprintListResponse,
  TransitBlueprintSearchParams,
  TransitBlueprintListItem,
  CreateTransitBlueprintPayload,
  ParsePreviewPayload,
  ParsePreviewResponse,
} from "@/types/transit-blueprint";

const BASE = "/api/v1/transit-blueprints";
const LIST_BASE = `${BASE}/`;

// --- Query options ---

export const transitBlueprintsQueryOptions = (
  params: TransitBlueprintSearchParams = {},
) =>
  queryOptions<TransitBlueprintListResponse>({
    queryKey: ["transit-blueprints", params],
    queryFn: async () => {
      const res = await api.get<TransitBlueprintListResponse>(LIST_BASE, { params });
      return res.data;
    },
  });

export const transitBlueprintQueryOptions = (blueprintId: string) =>
  queryOptions<TransitBlueprint>({
    queryKey: ["transit-blueprints", blueprintId],
    queryFn: async () => {
      const res = await api.get<TransitBlueprint>(`${BASE}/${blueprintId}`);
      return res.data;
    },
  });

export const routeBlueprintsQueryOptions = (
  origin: string,
  destination: string,
) =>
  queryOptions<TransitBlueprintListItem[]>({
    queryKey: ["transit-blueprints", "route", origin, destination],
    queryFn: async () => {
      const res = await api.get<TransitBlueprintListItem[]>(`${BASE}/route`, {
        params: { origin, destination },
      });
      return res.data;
    },
    enabled: !!origin && !!destination,
  });

// --- Mutations ---

export const createTransitBlueprint = async (
  payload: CreateTransitBlueprintPayload,
) => {
  const res = await api.post<TransitBlueprint>(LIST_BASE, payload);
  return res.data;
};

export const parsePreview = async (payload: ParsePreviewPayload) => {
  const res = await api.post<ParsePreviewResponse>(
    `${BASE}/parse-preview`,
    payload,
  );
  return res.data;
};

export const deleteTransitBlueprint = async (id: string) => {
  await api.delete(`${BASE}/${id}`);
};
