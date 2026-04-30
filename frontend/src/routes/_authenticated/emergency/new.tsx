import { createFileRoute } from "@tanstack/react-router";
import { FacilityForm } from "@/components/emergency/FacilityForm";

export const Route = createFileRoute("/_authenticated/emergency/new")({
  component: NewEmergencyFacilityPage,
});

function NewEmergencyFacilityPage() {
  return (
    <div className="container mx-auto py-8 px-4 flex justify-center">
      <div className="w-full max-w-2xl">
        <FacilityForm />
      </div>
    </div>
  );
}
