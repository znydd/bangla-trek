"""
Pre-saved emergency phrases in English, Bengali, and Romanized Bengali.
These are static data served directly from the backend without needing a database table.
"""

EMERGENCY_PHRASES = [
    {
        "category": "Medical",
        "phrases": [
            {
                "id": "med-1",
                "english": "I need a doctor",
                "bengali": "আমার ডাক্তার দরকার",
                "romanized": "Amar daktar dorkar",
            },
            {
                "id": "med-2",
                "english": "Please call an ambulance",
                "bengali": "অ্যাম্বুলেন্স ডাকুন",
                "romanized": "Ambulance dakun",
            },
            {
                "id": "med-3",
                "english": "I am allergic to this medicine",
                "bengali": "আমার এই ওষুধে অ্যালার্জি আছে",
                "romanized": "Amar ei oshudhe allergy achhe",
            },
            {
                "id": "med-4",
                "english": "Where is the nearest hospital?",
                "bengali": "নিকটতম হাসপাতাল কোথায়?",
                "romanized": "Nikottomo hashpatal kothay?",
            },
            {
                "id": "med-5",
                "english": "I need medicine for fever",
                "bengali": "আমার জ্বরের ওষুধ দরকার",
                "romanized": "Amar jworer oshudh dorkar",
            },
            {
                "id": "med-6",
                "english": "I have a stomach ache",
                "bengali": "আমার পেটে ব্যথা",
                "romanized": "Amar pete byatha",
            },
        ],
    },
    {
        "category": "Police & Safety",
        "phrases": [
            {
                "id": "pol-1",
                "english": "Please help me, I am in danger",
                "bengali": "আমাকে সাহায্য করুন, আমি বিপদে আছি",
                "romanized": "Amake sahajjo korun, ami bipode achhi",
            },
            {
                "id": "pol-2",
                "english": "I want to report a theft",
                "bengali": "আমি চুরির রিপোর্ট করতে চাই",
                "romanized": "Ami churir report korte chai",
            },
            {
                "id": "pol-3",
                "english": "Where is the nearest police station?",
                "bengali": "নিকটতম থানা কোথায়?",
                "romanized": "Nikottomo thana kothay?",
            },
            {
                "id": "pol-4",
                "english": "My passport has been stolen",
                "bengali": "আমার পাসপোর্ট চুরি হয়ে গেছে",
                "romanized": "Amar passport churi hoye gechhe",
            },
            {
                "id": "pol-5",
                "english": "I need to contact the tourist police",
                "bengali": "আমাকে ট্যুরিস্ট পুলিশে যোগাযোগ করতে হবে",
                "romanized": "Amake tourist police-e jogajog korte hobe",
            },
            {
                "id": "pol-6",
                "english": "Someone is following me",
                "bengali": "কেউ আমাকে অনুসরণ করছে",
                "romanized": "Keu amake onusoron korchhe",
            },
        ],
    },
    {
        "category": "Lost & Directions",
        "phrases": [
            {
                "id": "lost-1",
                "english": "I am lost, can you help me?",
                "bengali": "আমি পথ হারিয়ে ফেলেছি, আমাকে সাহায্য করবেন?",
                "romanized": "Ami poth hariye felechhi, amake sahajjo korben?",
            },
            {
                "id": "lost-2",
                "english": "Can you show me on the map?",
                "bengali": "আমাকে মানচিত্রে দেখাতে পারবেন?",
                "romanized": "Amake manchhitre dekhate parben?",
            },
            {
                "id": "lost-3",
                "english": "I need to go to this address",
                "bengali": "আমাকে এই ঠিকানায় যেতে হবে",
                "romanized": "Amake ei thikanay jete hobe",
            },
            {
                "id": "lost-4",
                "english": "Where can I find a taxi?",
                "bengali": "ট্যাক্সি কোথায় পাব?",
                "romanized": "Taxi kothay pabo?",
            },
        ],
    },
    {
        "category": "Communication",
        "phrases": [
            {
                "id": "com-1",
                "english": "I do not speak Bengali",
                "bengali": "আমি বাংলা বলতে পারি না",
                "romanized": "Ami Bangla bolte pari na",
            },
            {
                "id": "com-2",
                "english": "Do you speak English?",
                "bengali": "আপনি কি ইংরেজি বলতে পারেন?",
                "romanized": "Apni ki English bolte paren?",
            },
            {
                "id": "com-3",
                "english": "Can I use your phone to make a call?",
                "bengali": "আমি কি আপনার ফোন ব্যবহার করতে পারি?",
                "romanized": "Ami ki apnar phone bybohar korte pari?",
            },
            {
                "id": "com-4",
                "english": "Please speak slowly",
                "bengali": "দয়া করে ধীরে বলুন",
                "romanized": "Doya kore dhire bolun",
            },
        ],
    },
    {
        "category": "Money & Documents",
        "phrases": [
            {
                "id": "doc-1",
                "english": "Where is the nearest ATM?",
                "bengali": "নিকটতম এটিএম কোথায়?",
                "romanized": "Nikottomo ATM kothay?",
            },
            {
                "id": "doc-2",
                "english": "I have lost my wallet",
                "bengali": "আমার মানিব্যাগ হারিয়ে গেছে",
                "romanized": "Amar manibag hariye gechhe",
            },
            {
                "id": "doc-3",
                "english": "Where is the nearest embassy?",
                "bengali": "নিকটতম দূতাবাস কোথায়?",
                "romanized": "Nikottomo dutabas kothay?",
            },
            {
                "id": "doc-4",
                "english": "I need to exchange money",
                "bengali": "আমার টাকা বিনিময় করতে হবে",
                "romanized": "Amar taka binimoy korte hobe",
            },
        ],
    },
]
