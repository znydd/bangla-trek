export type CommunicationPlatform = "WhatsApp" | "Telegram" | "Messenger";

export interface PublicTrip {
  id: string;
  title: string;
  origin: string;
  destination: string;
  startAt: string;
  endAt: string;
  meetingPoint: string;
  transport: string;
  estimatedCost: string;
  description: string;
  itinerary: string;
  requirements: string[];
  organizerName: string;
  organizerEmail: string;
  communicationPlatform: CommunicationPlatform;
  communicationNote: string;
  memberCount: number;
  maxMembers: number;
  participantEmails: string[];
  ownedByViewer?: boolean;
}

export const syntheticTrips: PublicTrip[] = [
  {
    id: "sajek-weekend",
    title: "Cloudy Sajek weekend",
    origin: "Dhaka",
    destination: "Sajek Valley",
    startAt: "2026-08-28T22:30",
    endAt: "2026-08-31T06:00",
    meetingPoint: "Arambagh bus counter, Dhaka",
    transport: "Night bus to Khagrachari, then reserved chander gari",
    estimatedCost: "৳5,500–6,500 per person",
    description:
      "A relaxed weekend for sunrise, short walks and local food. We will travel overnight so both full days remain free in Sajek.",
    itinerary:
      "Friday night departure from Dhaka. Saturday: Khagrachari breakfast, Sajek check-in and sunset. Sunday: sunrise, Konglak walk and free time. Return Sunday evening.",
    requirements: ["Carry a photo ID", "Comfortable with shared rooms", "Pay the transport advance after confirmation"],
    organizerName: "Nafisa Rahman",
    organizerEmail: "nafisa@example.com",
    communicationPlatform: "WhatsApp",
    communicationNote: "The confirmed travelers receive the WhatsApp group invite by email.",
    memberCount: 5,
    maxMembers: 8,
    participantEmails: ["arif@example.com", "maliha@example.com", "rayhan@example.com", "tania@example.com"],
  },
  {
    id: "debota-khum-adventure",
    title: "Debotakhum river journey",
    origin: "Chattogram",
    destination: "Debotakhum",
    startAt: "2026-09-11T05:30",
    endAt: "2026-09-13T22:00",
    meetingPoint: "BRTC bus counter, Chattogram",
    transport: "Local bus, reserved jeep, boat and a short trek",
    estimatedCost: "৳4,200–5,200 per person",
    description:
      "A small-group adventure to Debotakhum with an early start, local guide and a night in Rowangchhari.",
    itinerary:
      "Travel to Bandarban and Rowangchhari on day one. Visit Debotakhum with a local guide on day two. Return through Bandarban on day three.",
    requirements: ["Able to walk on wet terrain", "Carry cash", "Follow the local guide's safety decisions"],
    organizerName: "Tahmid Hasan",
    organizerEmail: "tahmid@example.com",
    communicationPlatform: "Telegram",
    communicationNote: "A private Telegram group is shared after your place is confirmed.",
    memberCount: 3,
    maxMembers: 6,
    participantEmails: ["nabila@example.com", "sami@example.com"],
    ownedByViewer: true,
  },
  {
    id: "tanguar-haor",
    title: "Full-moon haor boat trip",
    origin: "Sylhet",
    destination: "Tanguar Haor",
    startAt: "2026-09-25T06:00",
    endAt: "2026-09-26T20:00",
    meetingPoint: "Ambarkhana Point, Sylhet",
    transport: "Reserved microbus to Tahirpur and an overnight boat",
    estimatedCost: "৳3,800–4,500 per person",
    description: "An overnight boat journey focused on open water, village stops and a quiet full-moon evening.",
    itinerary: "Morning departure for Tahirpur, board before lunch, overnight on the haor, return to Sylhet the following evening.",
    requirements: ["Bring a light blanket", "Shared sleeping deck", "No loud music near villages"],
    organizerName: "Sadman Kabir",
    organizerEmail: "sadman@example.com",
    communicationPlatform: "Messenger",
    communicationNote: "The organizer will email the Messenger group link after confirmation.",
    memberCount: 9,
    maxMembers: 14,
    participantEmails: [],
  },
  {
    id: "srimangal-cycling",
    title: "Tea garden cycling escape",
    origin: "Dhaka",
    destination: "Sreemangal",
    startAt: "2026-10-09T06:30",
    endAt: "2026-10-10T22:30",
    meetingPoint: "Kamalapur Railway Station",
    transport: "Intercity train and rented bicycles",
    estimatedCost: "৳3,000–4,000 per person",
    description: "A beginner-friendly cycling weekend through tea gardens with plenty of rest stops.",
    itinerary: "Train to Sreemangal, afternoon tea garden ride, morning cycle to Baikka Beel, return by evening train.",
    requirements: ["Know basic cycling", "Bring a refillable bottle", "Helmet rental included"],
    organizerName: "Raisa Ahmed",
    organizerEmail: "raisa@example.com",
    communicationPlatform: "WhatsApp",
    communicationNote: "Coordination happens in WhatsApp once the organizer confirms everyone.",
    memberCount: 4,
    maxMembers: 10,
    participantEmails: [],
  },
  {
    id: "kuakata-sunrise",
    title: "Kuakata sunrise and sunset",
    origin: "Barishal",
    destination: "Kuakata",
    startAt: "2026-10-23T07:00",
    endAt: "2026-10-24T19:00",
    meetingPoint: "Nathullabad bus terminal",
    transport: "Direct local bus and shared auto-rickshaw",
    estimatedCost: "৳2,800–3,600 per person",
    description: "A simple beach weekend with both sunrise and sunset, local food and no packed schedule.",
    itinerary: "Saturday arrival and sunset; Sunday sunrise, beach exploration and evening return to Barishal.",
    requirements: ["Shared twin rooms", "Bring sun protection", "Respect the agreed departure time"],
    organizerName: "Fahim Chowdhury",
    organizerEmail: "fahim@example.com",
    communicationPlatform: "Messenger",
    communicationNote: "The Messenger group invitation will arrive with your confirmation email.",
    memberCount: 2,
    maxMembers: 6,
    participantEmails: [],
  },
  {
    id: "ratargul-kayak",
    title: "Ratargul morning paddle",
    origin: "Sylhet",
    destination: "Ratargul Swamp Forest",
    startAt: "2026-11-07T06:00",
    endAt: "2026-11-07T16:00",
    meetingPoint: "Shahjalal Uposhohor, Sylhet",
    transport: "Reserved CNG and local wooden boats",
    estimatedCost: "৳1,400–1,900 per person",
    description: "A one-day early morning visit for calm water, photography and lunch near the forest.",
    itinerary: "Meet at 6:00 AM, reach Ratargul before crowds, two-hour boat session, local lunch and return by 4:00 PM.",
    requirements: ["Arrive on time", "Use a life jacket", "Keep electronics waterproof"],
    organizerName: "Ishrat Jahan",
    organizerEmail: "ishrat@example.com",
    communicationPlatform: "Telegram",
    communicationNote: "Confirmed travelers are invited to Telegram by email.",
    memberCount: 5,
    maxMembers: 7,
    participantEmails: [],
  },
];
