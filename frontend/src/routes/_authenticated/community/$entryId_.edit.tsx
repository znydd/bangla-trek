import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { communityEntryQueryOptions } from "@/services/community.service";
import { EntryForm } from "@/components/community/EntryForm";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth"; // assuming there's a useAuth or similar, wait let me check auth method later 
// Actually we can just get current user from API or skip auth check in UI, let backend handle or check author_name?
// wait, we can just fetch entry and render.

export const Route = createFileRoute(
  "/_authenticated/community/$entryId_/edit"
)({
  component: EditCommunityEntryPage,
});

function EditCommunityEntryPage() {
  const { entryId } = Route.useParams();
  const { data: entry, isLoading, error } = useQuery(
    communityEntryQueryOptions(entryId)
  );

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
        <EntryForm mode="edit" defaultValues={entry} />
      </div>
    </div>
  );
}
