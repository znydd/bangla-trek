import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { communityEntryQueryOptions, updateEntry } from "@/services/community.service";
import { EntryForm } from "@/components/community/EntryForm";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import type { UpdateEntryPayload } from "@/types/community";

export const Route = createFileRoute(
  "/_authenticated/community/$entryId_/edit"
)({
  component: EditCommunityEntryPage,
});

function EditCommunityEntryPage() {
  const { entryId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const { data: entry, isLoading, error } = useQuery(
    communityEntryQueryOptions(entryId)
  );

  const mutation = useMutation({
    mutationFn: (payload: UpdateEntryPayload) => updateEntry(entryId, payload),
    onSuccess: () => {
      toast.success("Entry updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["community-entries", entryId] });
      navigate({ to: "/community/$entryId", params: { entryId } });
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to update entry");
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-3xl space-y-8">
        <Skeleton className="h-10 w-1/2 mb-4" />
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    );
  }

  if (error || !entry) {
    return (
      <div className="container mx-auto py-20 px-4 text-center">
        <h2 className="text-2xl font-bold mb-2">Entry Not Found</h2>
        <p className="text-muted-foreground">The community entry you are looking for does not exist or has been removed.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Edit Community Entry</h1>
        <p className="text-muted-foreground mt-1">
          Update your travel entry details.
        </p>
      </div>
      
      <div className="bg-card border border-border/50 rounded-xl p-6">
        <EntryForm 
          mode="edit" 
          defaultValues={entry} 
          onSubmit={async (data) => {
            mutation.mutate(data);
          }} 
        />
      </div>
    </div>
  );
}
