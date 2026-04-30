import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transitBlueprintQueryOptions, deleteTransitBlueprint } from "@/services/transit-blueprint.service";
import { BlueprintDetail } from "@/components/transit-blueprints/BlueprintDetail";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Loader2 } from "lucide-react";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/_authenticated/transit-blueprints/$blueprintId",
)({
  component: TransitBlueprintDetailPage,
});

function TransitBlueprintDetailPage() {
  const { blueprintId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: blueprint,
    isLoading,
    error,
  } = useQuery(transitBlueprintQueryOptions(blueprintId));

  const { mutateAsync: doDelete, isPending: isDeleting } = useMutation({
    mutationFn: () => deleteTransitBlueprint(blueprintId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transit-blueprints"] });
      navigate({ to: "/transit-blueprints" });
    },
  });

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this transit blueprint?")) {
      await doDelete();
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 space-y-8">
        <Skeleton className="h-10 w-1/3 mb-4" />
        <Skeleton className="h-6 w-2/3 mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !blueprint) {
    return (
      <div className="container mx-auto py-20 px-4 text-center">
        <h2 className="text-2xl font-bold mb-2">Blueprint Not Found</h2>
        <p className="text-muted-foreground">
          The transit blueprint you are looking for does not exist or has been
          removed.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          size="sm"
          render={<Link to="/transit-blueprints" />}
          className="gap-2"
        >
          <ArrowLeft size={16} />
          All Blueprints
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleDelete}
          disabled={isDeleting}
          className="text-destructive hover:text-destructive gap-2"
        >
          {isDeleting ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Trash2 size={14} />
          )}
          Delete
        </Button>
      </div>

      <BlueprintDetail blueprint={blueprint} />
    </div>
  );
}
