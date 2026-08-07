import { LogIn, Compass, X } from "lucide-react";
import { loginWithGoogle } from "@/services/auth.service";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface LoginModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** What the user was trying to do — shown in the modal */
  action?: string;
}

export function LoginModal({ open, onOpenChange, action }: LoginModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton={false} className="max-w-sm gap-0 overflow-hidden p-0">
        {/* Header gradient */}
        <div className="relative bg-gradient-to-br from-emerald-600 to-teal-700 px-6 pb-8 pt-6 text-white">
          <button
            type="button"
            onClick={() => onOpenChange(false)}
            className="absolute right-4 top-4 rounded-full p-1.5 text-white/70 transition hover:bg-white/15 hover:text-white"
            aria-label="Close"
          >
            <X size={18} />
          </button>

          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
            <Compass size={26} className="text-white" strokeWidth={2.5} />
          </div>

          <DialogHeader>
            <DialogTitle className="text-left text-xl font-bold text-white">
              Sign in to continue
            </DialogTitle>
            <DialogDescription className="mt-1 text-left text-sm text-white/75">
              {action
                ? `To ${action}, you need to be signed in with Google.`
                : "Sign in with your Google account to access all Bangla Trek features."}
            </DialogDescription>
          </DialogHeader>
        </div>

        {/* Body */}
        <div className="flex flex-col gap-3 p-6">
          <Button
            type="button"
            onClick={loginWithGoogle}
            className="flex h-11 w-full items-center gap-3 rounded-xl bg-emerald-600 text-sm font-semibold text-white hover:bg-emerald-700"
          >
            <LogIn size={17} />
            Continue with Google
          </Button>

          <p className="text-center text-[11px] leading-5 text-muted-foreground">
            Your Google account is used only for authentication.
            <br />
            We never post on your behalf.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
