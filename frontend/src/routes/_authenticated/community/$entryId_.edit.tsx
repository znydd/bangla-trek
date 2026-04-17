import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  communityEntryQueryOptions,
  deletePhoto,
  updateEntry,
  uploadPhotos,
} from "@/services/community.service";
import { EntryForm } from "@/components/community/EntryForm";
import { Skeleton } from "@/components/ui/skeleton";
import type { CreateEntryPayload } from "@/types/community";

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

  const { mutateAsync, isPending } = useMutation({
    mutationFn: async ({
      data,
      photos,
      deletedPhotoIds,
    }: {
      data: CreateEntryPayload;
      photos: File[];
      deletedPhotoIds: string[];
    }) => {
      const updated = await updateEntry(entryId, data);
      await Promise.all(deletedPhotoIds.map((photoId) => deletePhoto(entryId, photoId)));
      if (photos.length > 0) {
        await uploadPhotos(entryId, photos);
      }
      return updated;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["community-entries"] });
      queryClient.invalidateQueries({ queryKey: ["community-entries", entryId] });
      navigate({ to: "/community/$entryId", params: { entryId } });
    },
  });

  const handleSubmit = async (
    data: CreateEntryPayload,
    photos: File[],
    deletedPhotoIds: string[],
  ) => {
    await mutateAsync({ data, photos, deletedPhotoIds });
  };

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
          onSubmit={handleSubmit}
          isLoading={isPending}
        />
      </div>
    </div>
  );
}
