import { Phone } from "lucide-react";

const EMERGENCY_NUMBERS = [
  { label: "National Emergency", number: "999", color: "bg-red-600" },
  { label: "Tourist Police", number: "01769-690730", color: "bg-emerald-600" },
  { label: "Fire Service", number: "199", color: "bg-orange-600" },
  { label: "Ambulance", number: "199", color: "bg-blue-600" },
];

export function EmergencyContactsBar() {
  return (
    <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-destructive mb-3 flex items-center gap-2">
        <Phone size={14} />
        Emergency Numbers
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {EMERGENCY_NUMBERS.map((item) => (
          <a
            key={item.label}
            href={`tel:${item.number}`}
            className={`${item.color} text-white rounded-lg p-3 text-center transition-all hover:opacity-90 hover:shadow-md`}
          >
            <div className="text-xs font-medium opacity-90">{item.label}</div>
            <div className="text-lg font-bold">{item.number}</div>
          </a>
        ))}
      </div>
    </div>
  );
}
