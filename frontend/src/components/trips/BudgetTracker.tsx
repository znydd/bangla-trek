import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ExpenseCategory, GroupTripExpenseCreate } from "@/types/trip-budget";
import {
  createGroupTripExpense,
  deleteGroupTripExpense,
  groupTripBudgetQueryOptions,
  groupTripBudgetSummaryQueryOptions,
  groupTripExpensesQueryOptions,
  upsertGroupTripBudget,
} from "@/services/trip-budget.service";
import { cn } from "@/lib/utils";
import { PiggyBank, Trash2 } from "lucide-react";

const CATEGORIES: Array<{ value: ExpenseCategory; label: string }> = [
  { value: "accommodation", label: "Accommodation" },
  { value: "food", label: "Food" },
  { value: "transport", label: "Transport" },
  { value: "attractions", label: "Attractions" },
  { value: "shopping", label: "Shopping" },
  { value: "other", label: "Other" },
];

function formatMoney(amount: number, currency: string) {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${currency} ${amount.toFixed(0)}`;
  }
}

function clamp01(x: number) {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

function DonutChart({
  totals,
  currency,
}: {
  totals: Array<{ category: string; total: number }>;
  currency: string;
}) {
  const total = totals.reduce((s, t) => s + (Number(t.total) || 0), 0);
  const segments = useMemo(() => {
    const colors = [
      "#10b981",
      "#3b82f6",
      "#f59e0b",
      "#ef4444",
      "#8b5cf6",
      "#14b8a6",
    ];
    const safe = totals.filter((t) => t.total > 0);
    let acc = 0;
    return safe.map((t, idx) => {
      const frac = total > 0 ? t.total / total : 0;
      const start = acc;
      acc += frac;
      return {
        ...t,
        frac,
        start,
        color: colors[idx % colors.length],
      };
    });
  }, [totals, total]);

  const r = 46;
  const c = 2 * Math.PI * r;
  return (
    <div className="flex items-center gap-6">
      <div className="relative h-28 w-28">
        <svg viewBox="0 0 120 120" className="h-28 w-28 -rotate-90">
          <circle cx="60" cy="60" r={r} fill="none" stroke="hsl(var(--muted))" strokeWidth="14" />
          {segments.map((s) => {
            const dash = c * s.frac;
            const offset = c * (1 - s.start);
            return (
              <circle
                key={s.category}
                cx="60"
                cy="60"
                r={r}
                fill="none"
                stroke={s.color}
                strokeWidth="14"
                strokeDasharray={`${dash} ${c - dash}`}
                strokeDashoffset={offset}
                strokeLinecap="butt"
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center text-center">
          <div>
            <div className="text-xs text-muted-foreground">Spent</div>
            <div className="text-sm font-semibold">{formatMoney(total, currency)}</div>
          </div>
        </div>
      </div>
      <div className="flex-1">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {segments.length ? (
            segments.map((s) => (
              <div key={s.category} className="flex items-center justify-between gap-2 rounded-lg border p-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: s.color }} />
                  <span className="text-sm font-medium truncate capitalize">{s.category}</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {formatMoney(s.total, currency)}
                </span>
              </div>
            ))
          ) : (
            <div className="text-sm text-muted-foreground">No expenses yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

export function BudgetTracker({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();

  const budgetQuery = useQuery(groupTripBudgetQueryOptions(tripId));
  const expensesQuery = useQuery(groupTripExpensesQueryOptions(tripId));
  const summaryQuery = useQuery({
    ...groupTripBudgetSummaryQueryOptions(tripId),
    enabled: Boolean(budgetQuery.data),
    refetchInterval: 5_000,
  });

  const [budgetAmount, setBudgetAmount] = useState("");
  const [budgetCurrency, setBudgetCurrency] = useState("BDT");

  const [expenseForm, setExpenseForm] = useState<GroupTripExpenseCreate>({
    amount: 0,
    category: "food",
    currency: "BDT",
    note: "",
  });

  useEffect(() => {
    if (!budgetQuery.data) return;
    setBudgetAmount(String(budgetQuery.data.total_budget ?? ""));
    setBudgetCurrency(budgetQuery.data.currency ?? "BDT");
    setExpenseForm((f) => ({ ...f, currency: budgetQuery.data?.currency ?? f.currency }));
  }, [budgetQuery.data]);

  const budgetMutation = useMutation({
    mutationFn: (payload: { total_budget: number; currency: string }) =>
      upsertGroupTripBudget(tripId, payload),
    onSuccess: () => {
      toast.success("Budget saved.");
      queryClient.invalidateQueries({ queryKey: ["group-trips", tripId, "budget"] });
      queryClient.invalidateQueries({ queryKey: ["group-trips", tripId, "budget", "summary"] });
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to save budget.");
    },
  });

  const createExpenseMutation = useMutation({
    mutationFn: (payload: GroupTripExpenseCreate) => createGroupTripExpense(tripId, payload),
    onSuccess: async () => {
      setExpenseForm((f) => ({ ...f, amount: 0, note: "" }));
      await queryClient.invalidateQueries({ queryKey: ["group-trips", tripId, "expenses"] });
      const res = await queryClient.fetchQuery(groupTripBudgetSummaryQueryOptions(tripId));
      if (res.crossed_100) toast.error("Budget exceeded (100%).");
      else if (res.crossed_80) toast.warning("Approaching budget limit (80%).");
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to add expense.");
    },
  });

  const deleteExpenseMutation = useMutation({
    mutationFn: ({ expenseId }: { expenseId: string }) => deleteGroupTripExpense(tripId, expenseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group-trips", tripId, "expenses"] });
      queryClient.invalidateQueries({ queryKey: ["group-trips", tripId, "budget", "summary"] });
    },
  });

  const summary = summaryQuery.data;
  const percent = clamp01(summary?.percent_used ?? 0);
  const percentLabel = `${Math.round(percent * 100)}%`;

  const progressTone =
    percent >= 1 ? "bg-red-500" : percent >= 0.8 ? "bg-amber-500" : "bg-green-600";

  return (
    <Card className="p-6 space-y-6">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <PiggyBank className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Live Budget Tracker</h2>
        </div>
        {budgetQuery.data ? (
          <Badge variant="secondary">Budget set</Badge>
        ) : (
          <Badge variant="outline">Set a budget to start</Badge>
        )}
      </div>

      {/* Budget form */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div className="space-y-2">
          <Label>Total budget</Label>
          <Input
            inputMode="decimal"
            placeholder="e.g. 25000"
            value={budgetAmount}
            onChange={(e) => setBudgetAmount(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label>Currency</Label>
          <Input
            placeholder="BDT"
            value={budgetCurrency}
            onChange={(e) => setBudgetCurrency(e.target.value.toUpperCase())}
          />
        </div>
        <Button
          onClick={() => {
            const amt = Number(budgetAmount);
            if (!Number.isFinite(amt) || amt <= 0) {
              toast.error("Enter a valid budget amount.");
              return;
            }
            budgetMutation.mutate({ total_budget: amt, currency: budgetCurrency || "BDT" });
          }}
          disabled={budgetMutation.isPending}
        >
          {budgetMutation.isPending ? "Saving..." : "Save budget"}
        </Button>
      </div>

      {/* Summary */}
      {budgetQuery.data && summary ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border p-4">
              <div className="text-xs text-muted-foreground">Budget</div>
              <div className="text-xl font-semibold">
                {formatMoney(summary.budget_total, summary.currency)}
              </div>
            </div>
            <div className="rounded-xl border p-4">
              <div className="text-xs text-muted-foreground">Spent</div>
              <div className="text-xl font-semibold">
                {formatMoney(summary.spent_total, summary.currency)}
              </div>
            </div>
            <div className="rounded-xl border p-4">
              <div className="text-xs text-muted-foreground">Remaining</div>
              <div className="text-xl font-semibold">
                {formatMoney(summary.remaining, summary.currency)}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Budget usage</span>
              <span className="font-medium">{percentLabel}</span>
            </div>
            <div className="h-3 w-full rounded-full bg-muted overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", progressTone)}
                style={{ width: `${Math.min(100, Math.round(percent * 100))}%` }}
              />
            </div>
            <div className="text-xs text-muted-foreground">
              Alerts trigger at 80% and 100% usage.
            </div>
          </div>

          <DonutChart totals={summary.totals_by_category} currency={summary.currency} />
        </div>
      ) : budgetQuery.data ? (
        <div className="text-sm text-muted-foreground">Loading summary…</div>
      ) : null}

      {/* Add expense */}
      <div className="rounded-xl border p-4 space-y-4">
        <div className="text-sm font-semibold">Log an expense</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
          <div className="space-y-2">
            <Label>Amount</Label>
            <Input
              inputMode="decimal"
              value={expenseForm.amount ? String(expenseForm.amount) : ""}
              onChange={(e) =>
                setExpenseForm((f) => ({ ...f, amount: Number(e.target.value) || 0 }))
              }
              placeholder="e.g. 1200"
              disabled={!budgetQuery.data}
            />
          </div>
          <div className="space-y-2">
            <Label>Category</Label>
            <Select
              value={expenseForm.category}
              onValueChange={(v) =>
                setExpenseForm((f) => ({ ...f, category: v as ExpenseCategory }))
              }
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c.value} value={c.value}>
                      {c.label}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2 md:col-span-2">
            <Label>Note (optional)</Label>
            <Input
              value={expenseForm.note ?? ""}
              onChange={(e) => setExpenseForm((f) => ({ ...f, note: e.target.value }))}
              placeholder="e.g. Dinner at Panshi"
              disabled={!budgetQuery.data}
            />
          </div>
          <Button
            onClick={() => {
              if (!budgetQuery.data) {
                toast.error("Set a budget first.");
                return;
              }
              if (!Number.isFinite(expenseForm.amount) || expenseForm.amount <= 0) {
                toast.error("Enter a valid expense amount.");
                return;
              }
              createExpenseMutation.mutate({
                amount: expenseForm.amount,
                category: expenseForm.category,
                currency: budgetQuery.data.currency,
                note: expenseForm.note?.trim() ? expenseForm.note.trim() : null,
              });
            }}
            disabled={!budgetQuery.data || createExpenseMutation.isPending}
            className="md:col-span-4"
          >
            {createExpenseMutation.isPending ? "Adding..." : "Add expense"}
          </Button>
        </div>
      </div>

      {/* Expenses list */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">Recent expenses</div>
          <div className="text-xs text-muted-foreground">
            {expensesQuery.data?.length ?? 0} entries
          </div>
        </div>
        {expensesQuery.isLoading ? (
          <div className="text-sm text-muted-foreground">Loading…</div>
        ) : expensesQuery.data && expensesQuery.data.length ? (
          <div className="space-y-2">
            {expensesQuery.data.slice(0, 20).map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between gap-3 rounded-xl border p-3"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium">
                      {formatMoney(e.amount, e.currency)}
                    </span>
                    <Badge variant="outline" className="capitalize">
                      {e.category}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(e.spent_at).toLocaleString()}
                    </span>
                  </div>
                  {e.note ? (
                    <div className="text-sm text-muted-foreground truncate">{e.note}</div>
                  ) : null}
                  {e.user_name ? (
                    <div className="text-xs text-muted-foreground">
                      by {e.user_name}
                    </div>
                  ) : null}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteExpenseMutation.mutate({ expenseId: e.id })}
                  disabled={deleteExpenseMutation.isPending}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            No expenses yet. Add your first one above.
          </div>
        )}
      </div>
    </Card>
  );
}

