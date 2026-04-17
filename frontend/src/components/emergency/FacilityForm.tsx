import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createFacility } from "@/services/emergency.service";
import type { EmergencyFacilityCreate, FacilityType } from "@/types/emergency";
import { Loader2, Plus, MapPin } from "lucide-react";

export function FacilityForm() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [locating, setLocating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EmergencyFacilityCreate>({
    defaultValues: {
      name: "",
      facility_type: "hospital" as FacilityType,
      address: "",
      district: "",
      latitude: 0,
      longitude: 0,
      phone_number: "",
      notes: "",
    },
  });

  const facilityType = watch("facility_type");

  const mutation = useMutation({
    mutationFn: createFacility,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emergency-facilities"] });
      queryClient.invalidateQueries({ queryKey: ["emergency-nearest"] });
      navigate({ to: "/emergency" });
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.detail || "Failed to create facility");
    },
  });

  const onSubmit = (data: EmergencyFacilityCreate) => {
    mutation.mutate(data);
  };

  const handleLocateMe = () => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setValue("latitude", position.coords.latitude);
        setValue("longitude", position.coords.longitude);
        setLocating(false);
      },
      () => {
        setLocating(false);
      },
    );
  };

  return (
    <Card className="max-w-2xl border-primary/20">
      <CardHeader>
        <CardTitle>Add Emergency Facility</CardTitle>
        <CardDescription>
          Contribute a new emergency facility (hospital, police station, or tourist police) to the community database.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {errorMsg && (
            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
              {errorMsg}
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Name */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Facility Name *</label>
                <Input
                  placeholder="e.g. Dhaka Medical College"
                  {...register("name", { required: "Name is required" })}
                />
                {errors.name && (
                  <p className="text-xs text-destructive">{errors.name.message}</p>
                )}
              </div>

              {/* Type */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Facility Type *</label>
                <Select
                  value={facilityType}
                  onValueChange={(val: FacilityType) =>
                    setValue("facility_type", val)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hospital">Hospital</SelectItem>
                    <SelectItem value="police_station">Police Station</SelectItem>
                    <SelectItem value="tourist_police">Tourist Police</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Address */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Address *</label>
              <Input
                placeholder="e.g. Secretariat Road, Dhaka 1000"
                {...register("address", { required: "Address is required" })}
              />
              {errors.address && (
                <p className="text-xs text-destructive">{errors.address.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* District */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">District *</label>
                <Input
                  placeholder="e.g. Dhaka"
                  {...register("district", { required: "District is required" })}
                />
                {errors.district && (
                  <p className="text-xs text-destructive">{errors.district.message}</p>
                )}
              </div>

              {/* Phone */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Phone Number</label>
                <Input
                  placeholder="e.g. 02-55165088"
                  {...register("phone_number")}
                />
              </div>
            </div>

            {/* Coordinates */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">GPS Coordinates *</label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleLocateMe}
                  disabled={locating}
                  className="h-7 text-xs gap-1.5"
                >
                  {locating ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <MapPin size={12} />
                  )}
                  Use current location
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Input
                    type="number"
                    step="any"
                    placeholder="Latitude"
                    {...register("latitude", {
                      required: "Latitude is required",
                      valueAsNumber: true,
                    })}
                  />
                  {errors.latitude && (
                    <p className="text-xs text-destructive mt-1">
                      {errors.latitude.message}
                    </p>
                  )}
                </div>
                <div>
                  <Input
                    type="number"
                    step="any"
                    placeholder="Longitude"
                    {...register("longitude", {
                      required: "Longitude is required",
                      valueAsNumber: true,
                    })}
                  />
                  {errors.longitude && (
                    <p className="text-xs text-destructive mt-1">
                      {errors.longitude.message}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Notes (optional)</label>
              <Textarea
                placeholder="e.g. 24/7 emergency department available."
                {...register("notes")}
                rows={3}
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/emergency" })}
              disabled={mutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending} className="gap-2">
              {mutation.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Plus size={16} />
              )}
              Add Facility
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
