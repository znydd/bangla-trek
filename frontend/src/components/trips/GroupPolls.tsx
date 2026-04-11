import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tripPollsQueryOptions, createPoll, votePoll } from "@/services/poll.service";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2, Plus, BarChart2 } from "lucide-react";
import { toast } from "sonner";
import { Poll } from "@/types/poll";

export function GroupPolls({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const { data: polls, isLoading } = useQuery(tripPollsQueryOptions(tripId));
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({ title: "", category: "general", options: ["", ""] });

  const createMutation = useMutation({
    mutationFn: () =>
      createPoll(tripId, {
        title: form.title,
        category: form.category,
        options: form.options.filter((o) => o.trim()).map((o) => ({ title: o })),
      }),
    onSuccess: () => {
      toast.success("Poll created!");
      setIsCreating(false);
      setForm({ title: "", category: "general", options: ["", ""] });
      queryClient.invalidateQueries({ queryKey: ["polls", tripId] });
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Failed to create poll"),
  });

  const voteMutation = useMutation({
    mutationFn: ({ pollId, optionId }: { pollId: string; optionId: string }) =>
      votePoll(tripId, pollId, optionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["polls", tripId] });
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Failed to vote"),
  });

  if (isLoading) return <div className="space-y-4"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <BarChart2 size={20} /> Group Polls
        </h2>
        {!isCreating && (
          <Button onClick={() => setIsCreating(true)} size="sm">
            <Plus size={16} className="mr-1" /> New Poll
          </Button>
        )}
      </div>

      {isCreating && (
        <Card className="p-4 space-y-4 border-primary">
          <h3 className="font-medium">Create a New Poll</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Question / Title</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Which hotel?" />
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <select 
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={form.category} 
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                <option value="general">General</option>
                <option value="attractions">Attractions</option>
                <option value="hotels">Hotels</option>
                <option value="restaurants">Restaurants</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Options</Label>
            {form.options.map((opt, i) => (
              <Input
                key={i}
                value={opt}
                onChange={(e) => {
                  const newOpts = [...form.options];
                  newOpts[i] = e.target.value;
                  setForm({ ...form, options: newOpts });
                }}
                placeholder={`Option ${i + 1}`}
              />
            ))}
            <Button variant="ghost" size="sm" onClick={() => setForm({ ...form, options: [...form.options, ""] })}>
              + Add Option
            </Button>
          </div>
          <div className="flex gap-2">
            <Button disabled={createMutation.isPending || !form.title || form.options.filter(o => o.trim()).length < 2} onClick={() => createMutation.mutate()}>
              {createMutation.isPending ? "Creating..." : "Create Poll"}
            </Button>
            <Button variant="outline" onClick={() => setIsCreating(false)}>Cancel</Button>
          </div>
        </Card>
      )}

      <div className="space-y-4">
        {polls?.map((poll) => (
          <PollCard key={poll.id} poll={poll} onVote={(optId) => voteMutation.mutate({ pollId: poll.id, optionId: optId })} />
        ))}
        {polls?.length === 0 && !isCreating && (
          <p className="text-muted-foreground text-sm text-center py-8">No polls yet. Start one to get the group's opinion!</p>
        )}
      </div>
    </div>
  );
}

function PollCard({ poll, onVote }: { poll: Poll; onVote: (optionId: string) => void }) {
  const total = poll.total_votes || 1; // prevent div by zero
  
  return (
    <Card className="p-4 space-y-3">
      <div>
        <div className="flex justify-between items-start">
          <h3 className="font-semibold text-lg">{poll.title}</h3>
          <Badge variant="outline">{poll.total_votes} votes</Badge>
        </div>
        <p className="text-xs text-muted-foreground mt-1">Asked by {poll.creator_name}</p>
      </div>

      <div className="space-y-2">
        {poll.options.map((opt) => {
          const percent = Math.round((opt.vote_count / total) * 100) || 0;
          return (
            <div key={opt.id} className="relative group cursor-pointer" onClick={() => onVote(opt.id)}>
              <div className="absolute inset-0 bg-secondary/30 rounded-md overflow-hidden">
                <div className="h-full bg-primary/20 transition-all duration-500" style={{ width: `${percent}%` }} />
              </div>
              <div className="relative p-3 flex justify-between items-center rounded-md border border-transparent group-hover:border-primary/30 transition-colors">
                <span className="font-medium flex items-center gap-2">
                  {opt.has_voted && <div className="h-2 w-2 bg-primary rounded-full" />}
                  {opt.title}
                </span>
                <span className="text-sm text-muted-foreground">{opt.vote_count} ({percent}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
