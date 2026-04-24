import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { NomadMetricSummary, NomadMetricSubmit } from "@/types/nomad-metrics";

const BASE = "/api/v1/nomad-metrics";
const SUBMIT_BASE = `${BASE}/`;

export const nomadMetricsQueryOptions = (entryId: string) =>
  queryOptions<NomadMetricSummary>({
    queryKey: ["nomad-metrics", entryId],
    queryFn: async () => {
      const res = await api.get<NomadMetricSummary>(`${BASE}/${entryId}`);
      return res.data;
    },
  });

export const submitNomadMetric = async (payload: NomadMetricSubmit) => {
  const res = await api.post(SUBMIT_BASE, payload);
  return res.data;
};
