import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { BlueprintForm } from "@/components/transit-blueprints/BlueprintForm";
import { createTransitBlueprint } from "@/services/transit-blueprint.service";
import type { CreateTransitBlueprintPayload } from "@/types/transit-blueprint";

export const Route = createFileRoute(
  "/_authenticated/transit-blueprints/new",
)({
  component: NewTransitBlueprintPage,
});

function NewTransitBlueprintPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn: async (data: CreateTransitBlueprintPayload) => {
      return createTransitBlueprint(data);
    },
    onSuccess: (blueprint) => {
      queryClient.invalidateQueries({ queryKey: ["transit-blueprints"] });
      navigate({
        to: "/transit-blueprints/$blueprintId",
        params: { blueprintId: blueprint.id },
      });
    },
  });

  const handleSubmit = async (data: CreateTransitBlueprintPayload) => {
    await mutateAsync(data);
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">
          Add Transit Blueprint
        </h1>
        <p className="text-muted-foreground mt-1">
          Share step-by-step transit directions for hard-to-reach destinations.
          Our AI will parse your description into structured steps.
        </p>
      </div>

      <div className="bg-card border border-border/50 rounded-xl p-6">
        <BlueprintForm onSubmit={handleSubmit} isLoading={isPending} />
      </div>
    </div>
  );
}
