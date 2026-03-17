Proposed Project Title: Smart Travel Itinerary Planner for
Bangladesh

● Language: TypeScript, Python
● Framework: React (Vite), FastAPI
● Styling: TailwindCSS, ShadCN
● Database: PostgreSQL
● ORM: Raw SQL
● Deployment: Vercel, Railway


Functional requirements:
Module 1: AI-Powered Itinerary, Viral Discovery & Community Data
1. [Member-1] Travelers and locals can contribute data for attractions, hotels,
guesthouses, homestays, and restaurants (name, location, price range,
amenities, photos, tips) through our platform. To reduce server costs while
keeping the platform highly visual, users embed URLs for famous travel vloggers'
reels (YouTube/Facebook/TikTok) directly into location pages, alongside
uploading their own photos via the Cloudinary API. The system categorizes these
entries with "Hidden Gem" or "Trending" tags to highlight viral and underrated
spots.
2. [Member-2] Users input destination, travel duration, budget, and preferences
(travel style, interests, group type). The system uses the LLM API to analyze
community-contributed data and generate personalized hour-by-hour itineraries
with activity descriptions, estimated costs, and local cultural insights, specifically
prioritizing underrated locations that match the user's criteria.
3. [Member-3] Each location page features a "Nomad Metrics" section where the
community rates vital infrastructural data critical for remote Bangladesh travel.
The system displays an interactive map using the Mapping API(Bari Koi API) that
visualizes these user-generated scores, including network connectivity by
specific carrier (e.g., GP 3G vs. Robi No Signal), solo-female safety ratings, and
digital payment (bKash) availability.
4. [Member-4] Users interact with an AI chatbot to refine itineraries using natural
language (e.g., "Add more nature spots," "Make it under 5000 taka"). To assist
with planning, the system sends seasonal intelligence and monsoon warnings via
the Messaging API, suggesting optimal visit months based on historical weather
patterns and community feedback.
Module 2: Social Travel & Accommodation
1. [Member-1] Users can create public or private group trips, invite others via
shareable links, and see who else is planning to visit the same destination during
overlapping dates to coordinate potential meetups and shared experiences.
2. [Member-2] The system recommends hotels, guesthouses, and homestays from
community-contributed data, filtering by budget range, location proximity to
planned attractions, amenities, and user ratings. The LLM API suggests
accommodations strategically positioned to minimize daily travel distances with
cost-benefit comparisons.
3. [Member-3] The system shows an interactive social map using the Mapping API
displaying where other users are currently traveling or planning to travel. This
enables spontaneous meetups and travel buddy matching based on shared
interests and travel styles.
4. [Member-4] Group members can collaboratively plan itineraries with real-time
updates, vote on attractions, hotels, and restaurants using a polling system. The
system sends real-time collaboration alerts and polling results to the group via
the Messaging API.
Module 3: Smart Route Optimization, Budget Management, Reviews, Emergency
& Export Features
1. [Member-1] After trips, users submit detailed reviews with star ratings, upload
photos via Cloudinary API, log actual costs and time spent at attractions and
hotels, and share travel tips that future travelers can filter by travel style (budget,
luxury, adventure, family).
2. [Member-2] Because standard mapping APIs frequently fail in rural Bangladesh,
users can manually write community "Transit Blueprints" (e.g., "Take a bus to
point A, hire a local CNG to point B, walk 20 mins"). The LLM API parses these
natural-language blueprints to override automated routing when planning trips to
off-grid underrated places.
3. [Member-3] The system uses the Mapping API to calculate optimal daily routes
with automatic geographic clustering of attractions, showing estimated travel
times by different modes (walking, cycling, driving) to minimize backtracking. It
falls back to community "Transit Blueprints" when standard API paths are
unavailable.
4. [Member-4] Users receive email notifications via the Messaging API when their
travel dates overlap with friends/connections in the same location, when
someone joins their group trip, and for daily itinerary reminders.
5. [Member-1] Users can view transportation cost estimates between locations with
manual input options for local transport fares (CNG, bus, train). The system
crowdsources this pricing data from community contributions to maintain
accurate, up-to-date fare estimates with external links to transportation booking
websites (Shohoz, rail e-ticketing).
6. [Member-2] Users can access emergency resources including a database of
hospitals, police stations, tourist police with showing nearest locations, and
pre-saved emergency phrases in Bengali/English. The LLM API helps translate
custom emergency requests into local dialects if needed.
7. [Member-3] The system provides a live budget tracker where users set trip
budgets, log expenses in real-time by category (accommodation, food, transport,
attractions), view visual spending breakdowns with charts, and receive alerts
when approaching 80% and 100% of budget limits.
8. [Member-4] Users export itineraries as PDF documents and download complete
itineraries with offline maps. The system ensures that all critical data including
the community Transit Blueprints, Nomad network metrics, and emergency
contacts is explicitly embedded into this offline export so it is fully accessible
without the internet during travel in remote areas.