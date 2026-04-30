import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  BudgetSummary,
  GroupTripBudget,
  GroupTripBudgetUpsert,
  GroupTripExpense,
  GroupTripExpenseCreate,
  GroupTripExpenseUpdate,
} from "@/types/trip-budget";

const BASE = "/api/v1/group-trips";

export const groupTripBudgetQueryOptions = (tripId: string) =>
  queryOptions<GroupTripBudget | null>({
    queryKey: ["group-trips", tripId, "budget"],
    queryFn: async () => {
      const res = await api.get<GroupTripBudget | null>(`${BASE}/${tripId}/budget`);
      return res.data;
    },
  });

export const groupTripBudgetSummaryQueryOptions = (tripId: string) =>
  queryOptions<BudgetSummary>({
    queryKey: ["group-trips", tripId, "budget", "summary"],
    queryFn: async () => {
      const res = await api.get<BudgetSummary>(`${BASE}/${tripId}/budget/summary`);
      return res.data;
    },
    retry: false,
  });

export const groupTripExpensesQueryOptions = (tripId: string) =>
  queryOptions<GroupTripExpense[]>({
    queryKey: ["group-trips", tripId, "expenses"],
    queryFn: async () => {
      const res = await api.get<GroupTripExpense[]>(`${BASE}/${tripId}/expenses`);
      return res.data;
    },
  });

export const upsertGroupTripBudget = async (tripId: string, payload: GroupTripBudgetUpsert) => {
  const res = await api.put<GroupTripBudget>(`${BASE}/${tripId}/budget`, payload);
  return res.data;
};

export const createGroupTripExpense = async (tripId: string, payload: GroupTripExpenseCreate) => {
  const res = await api.post<GroupTripExpense>(`${BASE}/${tripId}/expenses`, payload);
  return res.data;
};

export const updateGroupTripExpense = async (
  tripId: string,
  expenseId: string,
  payload: GroupTripExpenseUpdate
) => {
  const res = await api.put<GroupTripExpense>(`${BASE}/${tripId}/expenses/${expenseId}`, payload);
  return res.data;
};

export const deleteGroupTripExpense = async (tripId: string, expenseId: string) => {
  const res = await api.delete(`${BASE}/${tripId}/expenses/${expenseId}`);
  return res.data;
};

