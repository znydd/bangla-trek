import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { EntryForm } from "@/components/community/EntryForm";

export const Route = createFileRoute("/_authenticated/community/new")({
  component: NewCommunityEntryPage,
});

function NewCommunityEntryPage() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Create Community Entry</h1>
        <p className="text-muted-foreground mt-1">
          Share your travel experiences and recommendations with the community.
        </p>
      </div>
      
      <div className="bg-card border border-border/50 rounded-xl p-6">
        <EntryForm mode="create" />
      </div>
    </div>
  );
}
