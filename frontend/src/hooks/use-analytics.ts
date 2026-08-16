import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export interface AnalyticsSummary {
  documents_count: number;
  embeddings_count: number;
  total_queries: number;
  avg_response_time_ms: number | null;
  avg_retrieval_time_ms: number | null;
  retrieval_accuracy: number | null;
  token_usage: { prompt_tokens: number; completion_tokens: number };
  estimated_cost_usd: number;
  daily_queries: { date: string; count: number }[];
}

export function useAnalyticsSummary(days = 14) {
  return useQuery({
    queryKey: ["analytics-summary", days],
    queryFn: async () => {
      const { data } = await apiClient.get<AnalyticsSummary>("/analytics/summary", { params: { days } });
      return data;
    },
  });
}
