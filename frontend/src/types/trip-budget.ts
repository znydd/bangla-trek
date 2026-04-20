export type ExpenseCategory =
  | "accommodation"
  | "food"
  | "transport"
  | "attractions"
  | "shopping"
  | "other";

export type GroupTripBudget = {
  id: string;
  trip_id: string;
  created_by_user_id: string;
  total_budget: number;
  currency: string;
  alert_80_sent: boolean;
  alert_100_sent: boolean;
  created_at: string;
  updated_at: string;
};

export type GroupTripBudgetUpsert = {
  total_budget: number;
  currency?: string;
};

export type GroupTripExpense = {
  id: string;
  trip_id: string;
  user_id: string;
  amount: number;
  currency: string;
  category: ExpenseCategory | string;
  note: string | null;
  spent_at: string;
  created_at: string;
  updated_at: string;
  user_name?: string | null;
  user_picture_url?: string | null;
};

export type GroupTripExpenseCreate = {
  amount: number;
  currency?: string;
  category: ExpenseCategory;
  note?: string | null;
  spent_at?: string;
};

export type GroupTripExpenseUpdate = Partial<GroupTripExpenseCreate>;

export type BudgetCategoryTotal = { category: string; total: number };

export type BudgetSummary = {
  trip_id: string;
  currency: string;
  budget_total: number;
  spent_total: number;
  remaining: number;
  percent_used: number;
  totals_by_category: BudgetCategoryTotal[];
  crossed_80: boolean;
  crossed_100: boolean;
};

