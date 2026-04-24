import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  groupPollsQueryOptions,
  voteInPoll,
  createPoll,
} from "@/services/group-collaboration.service";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Loader2,
  CheckCircle2,
  Circle,
  BarChart3,
  Calendar,
  X,
} from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface GroupPollsProps {
  tripId: string;
}

export default function GroupPolls({ tripId }: GroupPollsProps) {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const { data: polls = [], isLoading } = useQuery({
    ...groupPollsQueryOptions(tripId),
    refetchInterval: isCreateOpen ? false : 15000,
    refetchOnWindowFocus: !isCreateOpen,
  });

  const voteMutation = useMutation({
    mutationFn: ({ pollId, optionId }: { pollId: string; optionId: string }) =>
      voteInPoll(pollId, optionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group-polls", tripId] });
      queryClient.invalidateQueries({ queryKey: ["group-activity", tripId] });
      toast.success("Vote recorded!");
    },
    onError: () => toast.error("Failed to record vote."),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Polls
        </h2>
        <CreatePollDialog
          tripId={tripId}
          open={isCreateOpen}
          onOpenChange={setIsCreateOpen}
        />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : polls.length === 0 ? (
        <Card className="p-8 text-center border-dashed border-2 bg-muted/20">
          <p className="text-muted-foreground">No active polls yet.</p>
          <p className="text-xs text-muted-foreground mt-1">Start a poll to decide on attractions or hotels!</p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {polls.map((poll) => (
            <Card key={poll.id} className="p-5 space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <h3 className="font-semibold text-lg">{poll.title}</h3>
                  {poll.description && (
                    <p className="text-sm text-muted-foreground italic">
                      {poll.description}
                    </p>
                  )}
                </div>
                {!poll.is_active && <Badge variant="secondary">Closed</Badge>}
              </div>

              <div className="space-y-2">
                {poll.options.map((option) => {
                  const percentage =
                    poll.total_votes > 0
                      ? Math.round((option.vote_count / poll.total_votes) * 100)
                      : 0;
                  const isVoted = poll.my_vote_option_id === option.id;

                  return (
                    <div key={option.id} className="group flex flex-col gap-1">
                      <button
                        onClick={() =>
                          poll.is_active &&
                          voteMutation.mutate({ pollId: poll.id, optionId: option.id })
                        }
                        disabled={!poll.is_active || voteMutation.isPending}
                        className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all hover:border-primary/50 text-left relative overflow-hidden group/btn cursor-pointer ${
                          isVoted ? "border-primary bg-primary/5 ring-1 ring-primary" : "bg-card"
                        }`}
                      >
                        <div className="flex items-center gap-3 relative z-10">
                          {isVoted ? (
                            <CheckCircle2 className="h-5 w-5 text-primary" />
                          ) : (
                            <Circle className="h-5 w-5 text-muted-foreground group-hover/btn:text-primary/50" />
                          )}
                          <span className="font-medium text-sm">{option.text}</span>
                        </div>
                        <span className="text-xs font-bold text-muted-foreground relative z-10">
                          {option.vote_count} vote{option.vote_count !== 1 ? "s" : ""}
                        </span>

                        {/* Progress Bar background */}
                        <div
                          className={`absolute inset-0 transition-all duration-500 opacity-20 ${
                            isVoted ? "bg-primary" : "bg-muted-foreground"
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </button>
                      <div className="flex justify-end px-1">
                         <span className="text-[10px] text-muted-foreground">{percentage}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
                <div className="flex items-center gap-1">
                  <Calendar size={12} />
                  <span>Started {new Date(poll.created_at).toLocaleDateString()}</span>
                </div>
                <div className="font-medium">Total: {poll.total_votes} votes</div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function CreatePollDialog({
  tripId,
  open,
  onOpenChange,
}: {
  tripId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [options, setOptions] = useState(["", ""]);
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => createPoll(tripId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group-polls", tripId] });
      queryClient.invalidateQueries({ queryKey: ["group-activity", tripId] });
      toast.success("Poll created!");
      onOpenChange(false);
      resetForm();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to create poll.");
    },
  });

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setOptions(["", ""]);
  };

  const handleAddOption = () => setOptions([...options, ""]);
  const handleRemoveOption = (index: number) => {
    if (options.length > 2) {
      setOptions(options.filter((_, i) => i !== index));
    }
  };

  const handleCreate = () => {
    const validOptions = options.filter((o) => o.trim() !== "");
    if (!title.trim() || validOptions.length < 2) {
      toast.error("Please provide a title and at least 2 options.");
      return;
    }
    createMutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      options: validOptions.map((text) => ({ text })),
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger
        render={
          <Button type="button" size="sm" className="gap-2 rounded-full">
            <Plus size={16} /> New Poll
          </Button>
        }
      />
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create a New Poll</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Question/Title</Label>
            <Input
              id="title"
              placeholder="e.g., Which hotel should we book?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Details (Optional)</Label>
            <Textarea
              id="description"
              placeholder="Add more context..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Options</Label>
            <div className="space-y-2">
              {options.map((opt, i) => (
                <div key={i} className="flex gap-2">
                  <Input
                    placeholder={`Option ${i + 1}`}
                    value={opt}
                    onChange={(e) => {
                      const newOpts = [...options];
                      newOpts[i] = e.target.value;
                      setOptions(newOpts);
                    }}
                  />
                  {options.length > 2 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRemoveOption(i)}
                      className="shrink-0"
                    >
                      <X size={16} />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddOption}
                className="w-full mt-1 border-dashed"
              >
                Add Option
              </Button>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button
            type="button"
            onClick={handleCreate}
            disabled={createMutation.isPending}
            className="w-full"
          >
            {createMutation.isPending ? (
              <Loader2 className="animate-spin h-4 w-4 mr-2" />
            ) : null}
            Create Poll
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
