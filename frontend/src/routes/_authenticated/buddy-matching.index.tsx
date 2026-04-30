import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  discoverBuddiesQueryOptions,
  incomingRequestsQueryOptions,
  myMatchesQueryOptions,
  connectWithUser,
  matchAction,
  deleteMatch,
} from "@/services/buddy-matching.service";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import type { BuddyMatch, BuddyMatchSuggestion } from "@/types/buddy-match";
import {
  Users,
  MapPin,
  Heart,
  UserPlus,
  UserCheck,
  UserX,
  Sparkles,
  Search,
  Compass,
} from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/_authenticated/buddy-matching/")({
  component: BuddyMatchingPage,
});

function BuddyMatchingPage() {
  const [activeTab, setActiveTab] = useState("discover");
  const [destinationFilter, setDestinationFilter] = useState("");
  const [interestFilter, setInterestFilter] = useState("");

  const queryClient = useQueryClient();

  // Queries
  const discoverQuery = useQuery(
    discoverBuddiesQueryOptions({
      destination: destinationFilter || undefined,
      interest: interestFilter || undefined,
      limit: 20,
    })
  );

  const myMatchesQuery = useQuery(
    myMatchesQueryOptions({ per_page: 100 })
  );
  const incomingRequestsQuery = useQuery(incomingRequestsQueryOptions());

  // Mutations
  const connectMutation = useMutation({
    mutationFn: connectWithUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["buddy-matching"] });
      setActiveTab("pending");
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ matchId, action }: { matchId: string; action: "accept" | "reject" | "block" }) =>
      matchAction(matchId, { action }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["buddy-matching"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMatch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["buddy-matching"] });
    },
  });

  const handleAccept = (matchId: string) => {
    actionMutation.mutate({ matchId, action: "accept" });
  };

  const handleReject = (matchId: string) => {
    actionMutation.mutate({ matchId, action: "reject" });
  };

  const handleDelete = (matchId: string) => {
    deleteMutation.mutate(matchId);
  };

  const handleConnect = (userId: string) => {
    connectMutation.mutate(userId);
  };

  // Group matches by status
  const allMatches = myMatchesQuery.data?.items ?? [];
  const suggestedMatches =
    allMatches.filter((m) => m.status === "suggested");
  const pendingMatches =
    allMatches.filter((m) => m.status === "pending");
  const acceptedMatches =
    allMatches.filter((m) => m.status === "accepted");
  const incomingPendingMatches =
    incomingRequestsQuery.data?.items.filter((m) => m.status === "pending") ?? [];

  const existingStatusByUserId = new Map(
    allMatches.map((m) => [m.matched_user_id, m.status] as const)
  );
  const visibleDiscoverSuggestions = (discoverQuery.data ?? []).filter((s) => {
    const currentStatus = existingStatusByUserId.get(s.matched_user_id);
    return !currentStatus || currentStatus === "suggested" || currentStatus === "rejected";
  });

  return (
    <div className="w-full max-w-[1400px] mx-auto py-8 px-4 md:px-6 xl:px-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <Users className="h-7 w-7 text-primary" />
            <h1 className="text-4xl font-bold tracking-tight">Buddy Matching</h1>
          </div>
          <p className="text-lg text-muted-foreground mt-1">
            Find travel companions based on shared interests and destinations.
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 lg:max-w-xl text-lg h-14">
          <TabsTrigger value="discover">
            <Compass size={16} />
            Discover
          </TabsTrigger>
          <TabsTrigger value="suggested">
            <Sparkles size={16} />
            Suggested
            {suggestedMatches.length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {suggestedMatches.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="pending">
            <UserPlus size={16} />
            Pending
            {pendingMatches.length + incomingPendingMatches.length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {pendingMatches.length + incomingPendingMatches.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="connected">
            <UserCheck size={16} />
            Connected
          </TabsTrigger>
        </TabsList>

        {/* Discover Tab */}
        <TabsContent value="discover" className="space-y-6 min-h-[56vh]">
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Filter by destination..."
                value={destinationFilter}
                onChange={(e) => setDestinationFilter(e.target.value)}
                className="pl-10 h-12 text-lg"
              />
            </div>
            <div className="relative flex-1">
              <Heart className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Filter by interest..."
                value={interestFilter}
                onChange={(e) => setInterestFilter(e.target.value)}
                className="pl-10 h-12 text-lg"
              />
            </div>
          </div>

          {/* Results */}
          {discoverQuery.isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-48 rounded-xl" />
              ))}
            </div>
          ) : visibleDiscoverSuggestions.length > 0 ? (
            <div className="space-y-4">
              {visibleDiscoverSuggestions.map((suggestion) => (
                <SuggestionCard
                  key={suggestion.matched_user_id}
                  suggestion={suggestion}
                  onConnect={() => handleConnect(suggestion.matched_user_id)}
                  isLoading={connectMutation.isPending}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 space-y-4">
              <Search className="h-16 w-16 mx-auto text-muted-foreground/30" />
              <div>
                <h2 className="text-xl font-semibold">No matches found</h2>
                <p className="text-muted-foreground mt-1">
                  Try adjusting your filters or create an itinerary to get
                  better matches.
                </p>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Suggested Tab */}
        <TabsContent value="suggested" className="space-y-4 min-h-[56vh]">
          {suggestedMatches.length > 0 ? (
            <div className="space-y-4">
              {suggestedMatches.map((match) => (
                <MatchCard
                  key={match.id}
                  match={match}
                  onConnect={() => handleConnect(match.matched_user_id)}
                  onReject={() => handleReject(match.id)}
                  isLoading={connectMutation.isPending || actionMutation.isPending}
                />
              ))}
            </div>
          ) : (
            <EmptyState message="No suggested matches yet. Go to Discover to find buddies!" />
          )}
        </TabsContent>

        {/* Pending Tab */}
        <TabsContent value="pending" className="space-y-4 min-h-[56vh]">
          {pendingMatches.length > 0 || incomingPendingMatches.length > 0 ? (
            <div className="space-y-6">
              {incomingPendingMatches.length > 0 ? (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold">Incoming requests</h3>
                  <div className="space-y-4">
                    {incomingPendingMatches.map((match) => (
                      <MatchCard
                        key={match.id}
                        match={match}
                        onAccept={() => handleAccept(match.id)}
                        onReject={() => handleReject(match.id)}
                        showActions={true}
                        isLoading={actionMutation.isPending}
                      />
                    ))}
                  </div>
                </div>
              ) : null}

              {pendingMatches.length > 0 ? (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold">Outgoing requests</h3>
                  <div className="space-y-4">
                    {pendingMatches.map((match) => (
                      <MatchCard
                        key={match.id}
                        match={match}
                        onDelete={() => handleDelete(match.id)}
                        isConnected={true}
                        isLoading={deleteMutation.isPending}
                        removeLabel="Cancel request"
                      />
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          ) : (
            <EmptyState message="No pending connection requests." />
          )}
        </TabsContent>

        {/* Connected Tab */}
        <TabsContent value="connected" className="space-y-4 min-h-[56vh]">
          {acceptedMatches.length > 0 ? (
            <div className="space-y-4">
              {acceptedMatches.map((match) => (
                <MatchCard
                  key={match.id}
                  match={match}
                  onDelete={() => handleDelete(match.id)}
                  isConnected={true}
                  isLoading={deleteMutation.isPending}
                />
              ))}
            </div>
          ) : (
            <EmptyState message="No connected buddies yet. Accept some suggestions to build your network!" />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Sub-components

function SuggestionCard({
  suggestion,
  onConnect,
  isLoading,
}: {
  suggestion: BuddyMatchSuggestion;
  onConnect: () => void;
  isLoading?: boolean;
}) {
  return (
    <Card className="w-full max-w-6xl mx-auto min-h-[26rem] flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar className="h-12 w-12">
              <AvatarImage src={suggestion.matched_user_picture_url || ""} />
              <AvatarFallback>
                {suggestion.matched_user_name.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold text-2xl">{suggestion.matched_user_name}</h3>
              <div className="flex items-center gap-1 text-lg text-muted-foreground">
                <Sparkles className="h-3 w-3" />
                <span>{Math.round(suggestion.match_score * 100)}% match</span>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 content-start">
        {/* Common Interests */}
        {suggestion.common_interests.length > 0 && (
          <div className="md:col-span-2">
            <p className="text-base text-muted-foreground mb-2">Common interests</p>
            <div className="flex flex-wrap gap-1">
              {suggestion.common_interests.slice(0, 3).map((interest) => (
                <Badge key={interest} variant="secondary" className="text-base px-3 py-1">
                  {interest}
                </Badge>
              ))}
              {suggestion.common_interests.length > 3 && (
                <Badge variant="outline" className="text-base px-3 py-1">
                  +{suggestion.common_interests.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Common Destinations */}
        {suggestion.common_destinations.length > 0 && (
          <div>
            <p className="text-base text-muted-foreground mb-2">
              Common destinations
            </p>
            <div className="flex flex-wrap gap-1">
              {suggestion.common_destinations.map((dest) => (
                <Badge key={dest} variant="outline" className="text-base px-3 py-1">
                  <MapPin className="h-3 w-3 mr-1" />
                  {dest}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Source */}
        <div className="flex items-center gap-2 text-base text-muted-foreground pt-2 md:justify-end">
          <Badge variant="outline" className="text-base capitalize px-3 py-1">
            {suggestion.match_source.replace("_", " ")}
          </Badge>
        </div>

        <Button onClick={onConnect} className="w-full text-lg h-12 md:col-span-3" disabled={isLoading}>
          <UserPlus className="h-4 w-4 mr-2" />
          {isLoading ? "Sending..." : "Connect"}
        </Button>
      </CardContent>
    </Card>
  );
}

function MatchCard({
  match,
  onConnect,
  onAccept,
  onReject,
  onDelete,
  showActions = false,
  isConnected = false,
  isLoading = false,
  removeLabel = "Remove Connection",
}: {
  match: BuddyMatch;
  onConnect?: () => void;
  onAccept?: () => void;
  onReject?: () => void;
  onDelete?: () => void;
  showActions?: boolean;
  isConnected?: boolean;
  isLoading?: boolean;
  removeLabel?: string;
}) {
  return (
    <Card className="w-full max-w-6xl mx-auto min-h-[26rem] flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar className="h-12 w-12">
              <AvatarImage src={match.matched_user_picture_url || ""} />
              <AvatarFallback>{match.matched_user_name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold text-2xl">{match.matched_user_name}</h3>
              <div className="flex items-center gap-1 text-lg text-muted-foreground">
                <Sparkles className="h-3 w-3" />
                <span>{Math.round(match.match_score * 100)}% match</span>
              </div>
            </div>
          </div>
          <Badge
            variant={
              match.status === "accepted"
                ? "default"
                : match.status === "pending"
                ? "secondary"
                : "outline"
            }
            className="capitalize text-base px-3 py-1"
          >
            {match.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 content-start">
        {/* Common Interests */}
        {match.common_interests.length > 0 && (
          <div className="md:col-span-2">
            <p className="text-base text-muted-foreground mb-2">Common interests</p>
            <div className="flex flex-wrap gap-1">
              {match.common_interests.slice(0, 3).map((interest) => (
                <Badge key={interest} variant="secondary" className="text-base px-3 py-1">
                  <Heart className="h-3 w-3 mr-1" />
                  {interest}
                </Badge>
              ))}
              {match.common_interests.length > 3 && (
                <Badge variant="outline" className="text-base px-3 py-1">
                  +{match.common_interests.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Common Destinations */}
        {match.common_destinations.length > 0 && (
          <div>
            <p className="text-base text-muted-foreground mb-2">
              Common destinations
            </p>
            <div className="flex flex-wrap gap-1">
              {match.common_destinations.map((dest) => (
                <Badge key={dest} variant="outline" className="text-base px-3 py-1">
                  <MapPin className="h-3 w-3 mr-1" />
                  {dest}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="flex gap-2 pt-2 mt-auto md:col-span-3">
            <Button
              onClick={onAccept}
              variant="default"
              size="sm"
              className="flex-1 text-lg h-12"
              disabled={isLoading}
            >
              <UserCheck className="h-4 w-4 mr-1" />
              Accept
            </Button>
            <Button
              onClick={onReject}
              variant="outline"
              size="sm"
              className="flex-1 text-lg h-12"
              disabled={isLoading}
            >
              <UserX className="h-4 w-4 mr-1" />
              Reject
            </Button>
          </div>
        )}

        {isConnected && (
          <Button onClick={onDelete} variant="outline" size="sm" className="w-full text-lg h-12 mt-auto md:col-span-3" disabled={isLoading}>
            <UserX className="h-4 w-4 mr-2" />
            {removeLabel}
          </Button>
        )}

        {match.status === "suggested" && (
          <div className="flex gap-2 pt-2 mt-auto md:col-span-3">
            <Button
              onClick={onConnect}
              variant="default"
              size="sm"
              className="flex-1 text-lg h-12"
              disabled={isLoading}
            >
              <UserPlus className="h-4 w-4 mr-1" />
              Connect
            </Button>
            <Button
              onClick={onReject}
              variant="outline"
              size="sm"
              className="flex-1 text-lg h-12"
              disabled={isLoading}
            >
              <UserX className="h-4 w-4 mr-1" />
              Dismiss
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-16 space-y-4">
      <Users className="h-16 w-16 mx-auto text-muted-foreground/30" />
      <p className="text-muted-foreground">{message}</p>
    </div>
  );
}
