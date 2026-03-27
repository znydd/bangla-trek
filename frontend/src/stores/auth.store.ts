import { create } from "zustand";
import type { User } from "@/types/user";

// Stores user info for synchronous access (e.g. Navbar).
// Tokens are NEVER stored here — httpOnly cookies handle that.
interface AuthState {
  user: User | null;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
