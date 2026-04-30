import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { EntryForm } from "@/components/community/EntryForm";
import { createEntry, uploadPhotos } from "@/services/community.service";
import type { CreateEntryPayload } from "@/types/community";

export const Route = createFileRoute("/_authenticated/community/new")({
  component: NewCommunityEntryPage,
});

function NewCommunityEntryPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn: async ({
      data,
      photos,
    }: {
      data: CreateEntryPayload;
      photos: File[];
    }) => {
      const entry = await createEntry(data);
      if (photos.length > 0) {
        await uploadPhotos(entry.id, photos);
      }
      return entry;
    },
    onSuccess: (entry) => {
      queryClient.invalidateQueries({ queryKey: ["community-entries"] });
      navigate({ to: "/community/$entryId", params: { entryId: entry.id } });
    },
  });

  const handleSubmit = async (data: CreateEntryPayload, photos: File[]) => {
    await mutateAsync({ data, photos });
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <div className="mb-8">
        <p className="text-muted-foreground mt-1">
          Share your travel experiences and recommendations with the community.
        </p>
      </div>

      <div className="bg-card border border-border/50 rounded-xl p-6">
        <EntryForm mode="create" onSubmit={handleSubmit} isLoading={isPending} />
      </div>
    </div>
  );
}