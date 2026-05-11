import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import type { User } from "../types";

type Props = {
  user: User | null;
  loading: boolean;
  children: ReactNode;
};

export function ProtectedRoute({ user, loading, children }: Props) {
  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-lg">Carregando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
