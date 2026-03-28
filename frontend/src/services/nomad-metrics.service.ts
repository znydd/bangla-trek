import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { NomadMetricSummary, NomadMetricSubmit } from "@/types/nomad-metrics";

const BASE = "/api/v1/nomad-metrics";

export const nomadMetricsQueryOptions = (entryId: string) =>
  queryOptions<NomadMetricSummary>({
    queryKey: ["nomad-metrics", entryId],
    queryFn: async () => {
      const res = await api.get<NomadMetricSummary>(`${BASE}/${entryId}`);
      return res.data;
    },
  });

export const submitNomadMetric = async (payload: NomadMetricSubmit) => {
  const res = await api.post(BASE, payload);
  return res.data;
};
