# Google Stitch UI Design Prompts — BongoVromon (Smart Travel Itinerary Planner for Bangladesh)

> **App Context:** A travel planning **desktop website** for Bangladesh called "BongoVromon". Tech stack is React + TailwindCSS + ShadCN. The design should be **minimalist** — clean whitespace, flat/subtle elements, muted teal-and-amber color palette with soft whites, and minimal visual clutter. Use Inter or similar clean sans-serif font. All screens are full **desktop website** layouts (not mobile app screens).

---

## Prompt 1 — Community Data Contribution Page (Member-1)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" where users contribute location data for attractions, hotels, guesthouses, homestays, and restaurants. Keep the UI clean with generous whitespace, flat design elements, and no visual clutter.

**Page layout:**
- Top: sticky navbar with logo ("BongoVromon"), search bar, and user avatar dropdown.
- Hero section: a banner with the heading "Share a Hidden Gem" and a subheading encouraging community contributions.
- Main content: a clean multi-step form card with the following steps:
  - Step 1 — Category selector (attraction, hotel, guesthouse, homestay, restaurant) shown as icon cards.
  - Step 2 — Details form with fields: name, location (with a small inline map pin picker), price range slider, amenities (tag chips), and a rich text area for tips.
  - Step 3 — Media upload section: a drag-and-drop photo upload area (powered by Cloudinary) with image thumbnails preview, plus a URL embed field for YouTube/Facebook/TikTok travel vlogger reels with a live preview card.
  - Step 4 — Tag selector for "Hidden Gem" or "Trending" with toggle badges, and a submit button.
- Sidebar: a live preview card showing how the listing will appear on the platform.
- Color palette: muted deep teal primary, warm amber accents, soft white background. Minimalist style — flat cards with thin borders instead of heavy shadows, generous whitespace, clean typography, and simple step-transition indicators.

---

## Prompt 2 — Group Trip Creation Page (Member-1)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" where users create and manage group trips. Keep the UI clean, flat, and uncluttered with generous whitespace.

**Page layout:**
- Top: sticky navbar with logo, navigation links (Explore, My Trips, Groups), and user avatar.
- Main content area split into two columns:
  - Left column — "Create a Group Trip" form card with fields: trip name, destination (autocomplete dropdown with Bangladeshi locations), start date and end date (date range picker), visibility toggle (Public/Private with icon badges), description text area, and a "Generate Invite Link" button that shows a copyable shareable link with a copy-to-clipboard icon.
  - Right column — "Who Else Is Going?" discovery panel: a list of user avatar cards showing other travelers planning to visit the same destination during overlapping dates, each card showing name, travel dates, mutual interests as small tag chips, and a "Send Meetup Request" button.
- Bottom section: a horizontal scrollable list of the user's existing group trips as cards with trip name, destination thumbnail, member count badge, and date range.
- Color palette: muted deep teal, warm amber highlights on CTAs, soft white card backgrounds. Minimalist flat cards with thin borders, no glassmorphism or heavy shadows, clean hover states with subtle underlines or color shifts.

---

## Prompt 3 — AI Itinerary Generation Page (Member-2)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" where users generate AI-powered personalized travel itineraries. Clean, flat, uncluttered layout with generous whitespace.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Left panel (1/3 width) — Input form card with:
  - Destination search field with autocomplete and a small map thumbnail.
  - Travel duration selector (number of days stepper).
  - Budget input with a slider and numeric field (in BDT taka).
  - Travel style selector as selectable pill chips: Budget, Comfort, Luxury, Adventure, Cultural, Family.
  - Interests multi-select as icon tag chips: Nature, History, Food, Photography, Hiking, Beach, River, Tea Gardens.
  - Group type selector: Solo, Couple, Family, Friends.
  - A prominent "Generate Itinerary" CTA button with a sparkle/AI icon.
- Right panel (2/3 width) — Generated itinerary results area:
  - A day-by-day accordion/timeline view. Each day expands to show hour-by-hour activity cards.
  - Each activity card shows: time slot, activity name and description, a small photo thumbnail, estimated cost badge (in taka), and a "local cultural insight" tip shown as a subtle info callout.
  - Activities tagged as "Hidden Gem" or "Underrated" have a special gold star badge.
  - A floating summary bar at the bottom showing total estimated cost, total days, and a "Save Itinerary" button.
- Use a simple loading skeleton animation while the AI generates results. Color palette: muted teal, amber, white. Minimalist card-based layout with thin timeline connectors between activities, no heavy shadows or decorative elements.

---

## Prompt 4 — Accommodation Recommendations Page (Member-2)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" that recommends hotels, guesthouses, and homestays from community data. Clean flat design with generous whitespace.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Filter bar below navbar: horizontal scrollable filter chips for — type (Hotel, Guesthouse, Homestay), budget range slider, amenities multi-select (WiFi, AC, Hot Water, Parking, Restaurant), minimum star rating selector, and a "Sort by" dropdown (Price Low-High, Rating, Distance to Attractions).
- Main content in a two-column layout:
  - Left column (60%) — accommodation listing cards in a vertical list. Each card shows: a large cover photo, property name, type badge (Hotel/Guesthouse/Homestay), star rating with review count, price per night in BDT, top 3 amenity icons, distance to nearest planned attraction (e.g., "1.2 km from Sajek Valley viewpoint"), and a "View Details" button.
  - Right column (40%) — an embedded interactive map showing pins for all listed accommodations. Clicking a pin highlights the corresponding card on the left. Planned attractions are shown as different colored pins.
- Below the listing: an "AI Recommendation" highlight section — a special card with a subtle gradient border and sparkle icon, showing the LLM's top pick with a short explanation of why it was chosen (strategic positioning, cost-benefit analysis). Include comparison badges like "Saves 45 min daily travel" or "Best value in area".
- Color palette: muted teal, amber, white. Minimalist flat cards with thin borders, no heavy shadows, clean typography with generous spacing.

---

## Prompt 5 — Nomad Metrics & Interactive Map Page (Member-3)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" showing a location's "Nomad Metrics" with an interactive community-rated map. Clean, flat, data-focused layout with no visual clutter.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Hero section: a full-width header with the location name (e.g., "Sajek Valley"), a large cover photo, and breadcrumb navigation (Home > Rangamati > Sajek Valley).
- Main content two-column layout:
  - Left column (55%) — "Nomad Metrics" dashboard cards in a grid:
    - **Network Connectivity card:** a table/grid showing mobile carriers (Grameenphone, Robi, Banglalink, Teletalk) as rows, with signal strength indicators (No Signal, 2G, 3G, 4G) as colored badge cells. Community vote count shown per cell. A small rating bar for each.
    - **Solo-Female Safety card:** a circular gauge/donut chart showing the safety score (e.g., 4.2/5) with total ratings count, plus top 3 safety tips from the community as a mini list.
    - **Digital Payment Availability card:** icon badges for bKash, Nagad, Rocket with availability status (Available, Limited, Unavailable) as colored chips and percentage bars based on community reports.
    - **General Infrastructure card:** small rating bars for electricity reliability, clean water access, and road quality.
  - Right column (45%) — a large interactive map (Bari Koi API style) of the area with:
    - Color-coded overlay zones showing network coverage, safety heatmap layer, and bKash availability markers.
    - A layer toggle control panel (top-right of map) to switch between: Network, Safety, Payments views.
    - Clickable pins for points of interest with mini info popups.
- Bottom section: a "Rate This Location" collapsible panel where users can submit their own ratings for each metric category using slider inputs and optional comment fields.
- Color palette: muted deep teal, amber, white. Minimalist data visualization — flat charts, thin grid lines, clean metric cards with thin borders and generous whitespace.

---

## Prompt 6 — Live Budget Tracker Page (Member-3)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" featuring a live trip budget tracker with expense logging and visual spending breakdowns. Flat, clean, uncluttered layout.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Header section: trip name (e.g., "Sylhet Adventure — 5 Day Trip"), overall budget progress bar showing spent vs. remaining (e.g., "৳12,400 / ৳20,000") with a percentage indicator. The progress bar changes color: green (<60%), amber (60-80%), orange (80-100%), red (>100%).
- Main content in two-column layout:
  - Left column (55%) — Expense log section:
    - "Add Expense" button that opens an inline form or modal with: amount (BDT), category dropdown (Accommodation, Food, Transport, Attractions, Shopping, Other), description field, date picker (defaults to today), and optional photo receipt upload.
    - Below the form: a scrollable list of logged expenses grouped by day, each entry showing category icon, description, amount, and a small delete/edit icon. Daily subtotals shown as section headers.
  - Right column (45%) — Visual spending dashboard:
    - A donut/pie chart showing spending breakdown by category with color-coded legend.
    - A horizontal stacked bar chart comparing budget allocation vs actual spending per category.
    - A daily spending trend line chart showing spending over the trip duration.
- Alert banners: a yellow warning banner appears at 80% budget ("You've used 80% of your budget!") and a red danger banner at 100% ("Budget exceeded!") with suggestions to adjust remaining plans.
- Bottom section: a summary card showing per-day average spending, projected total, and remaining budget.
- Color palette: muted teal, amber, white. Minimal chart colors (teal, amber, coral, soft blue). Flat cards with thin borders, simple clean charts, no decorative elements.

---

## Prompt 7 — AI Chatbot for Itinerary Refinement Page (Member-4)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" featuring an AI chatbot interface for refining travel itineraries with natural language. Clean, flat chat UI with generous whitespace.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Main content in a two-panel layout:
  - Left panel (40%) — Current itinerary summary view:
    - A compact vertical timeline showing the current itinerary with day headers and activity cards (time, name, cost badge). Items that the AI modifies get a subtle highlight/glow animation. A "Save Changes" floating button at the bottom.
  - Right panel (60%) — Chat interface:
    - Chat header: "BongoVromon AI Assistant" with a bot avatar and a green "online" status dot.
    - Chat message area with alternating message bubbles:
      - User messages in a teal bubble (right-aligned).
      - AI responses in a light gray/white bubble (left-aligned) with the bot avatar. AI responses can contain rich content: formatted text, mini itinerary cards, cost comparison tables, and inline suggestion chips.
    - Quick suggestion chips above the input field: "Add more nature spots", "Make it under 5000 taka", "Add a food tour", "Show hidden gems", "Extend by 1 day".
    - Input area at bottom: a text input field with a send button and a microphone icon.
- Top banner (collapsible): a seasonal intelligence alert bar — e.g., a weather warning "⚠️ Monsoon season in Sylhet (June-Sept): Heavy rainfall expected. Consider visiting Oct-Feb for best conditions." in an amber/yellow alert card with a dismiss button.
- Color palette: muted deep teal, warm amber, soft white. Minimalist chat bubbles with subtle rounded corners and thin borders, no heavy shadows. Simple fade-in for new messages.

---

## Prompt 8 — Collaborative Group Planning & Polling Page (Member-4)

Design a minimalist desktop website page for a Bangladesh travel platform called "BongoVromon" where group members collaboratively plan itineraries with real-time updates and vote on options. Clean, flat, uncluttered collaborative workspace.

**Page layout:**
- Top: sticky navbar with logo and navigation.
- Sub-header: group trip info bar showing trip name, destination, dates, and member avatars (stacked circular avatars with a "+3 more" overflow badge). An "Invite Members" button with a link-copy icon.
- Main content in a three-column layout:
  - Left column (25%) — Group members panel:
    - List of member cards with avatar, name, online/offline status dot, and role badge (Organizer, Member). Each member has a colored cursor/presence indicator to show where they are editing.
  - Center column (50%) — Shared itinerary editor:
    - A day-by-day itinerary timeline that all members can edit. Each activity card shows: activity name, time, added-by avatar, and a small vote count badge.
    - Inline "Add Activity" button between cards to suggest new items.
    - Real-time edit indicators: colored borders or highlights showing which member is currently editing which activity (collaborative cursor style).
    - Activity cards that are being voted on have a special "Under Vote" badge with a timer countdown.
  - Right column (25%) — Activity & polling panel:
    - **Active Polls section:** poll cards with the question (e.g., "Where should we eat dinner on Day 2?"), options as selectable cards with photos and quick info (name, rating, price), vote count bars for each option, and a "Vote" button. Shows which members voted via small avatars.
    - **Create Poll button:** opens a form to create a new poll with question, add options (searchable from platform locations), and set voting deadline.
    - **Activity Feed section:** a scrollable feed of recent changes — "Rima added Ratargul Swamp Forest to Day 3", "Karim voted for Hotel Greenland", "New poll: Day 2 dinner spot?" — with timestamps and member avatars.
- A notification toast area (top-right) for real-time alerts: "Karim just updated Day 2 activities", "Poll results are in!".
- Color palette: muted deep teal, warm amber, white. Use subtle colored presence indicators (green, blue, purple, orange) for different members. Minimalist flat cards with thin borders, simple real-time update indicators, no heavy decorative elements.
