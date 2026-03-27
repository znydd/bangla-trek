import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { communityEntryQueryOptions } from "@/services/community.service";
import { EntryDetail } from "@/components/community/EntryDetail";
import { Skeleton } from "@/components/ui/skeleton";

export const Route = createFileRoute("/_authenticated/community/$entryId")({
  component: CommunityDetailPage,
});

function CommunityDetailPage() {
  const { entryId } = Route.useParams();
  const { data: entry, isLoading, error } = useQuery(
    communityEntryQueryOptions(entryId)
  );

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 space-y-8">
        <Skeleton className="h-10 w-1/3 mb-4" />
        <Skeleton className="h-64 w-full rounded-xl mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-4">
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-5/6" />
            <Skeleton className="h-6 w-4/6" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full rounded-xl" />
          </div>
        </div>
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
    <div className="container mx-auto py-8 px-4">
      <EntryDetail entry={entry} />
    </div>
  );
}
