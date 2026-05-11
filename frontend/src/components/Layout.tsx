import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import type { User } from "../types";

type Props = {
  user: User;
};

export function Layout({ user }: Props) {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("laudoia_token");
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-transparent text-ink">
      <header className="border-b border-black/10 bg-sand/70 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="font-display text-2xl font-semibold tracking-tight">
            LaudoIA Pericial
          </Link>
          <nav className="flex items-center gap-5 text-sm">
            <NavLink to="/" className="hover:text-ember">
              Dashboard
            </NavLink>
            <NavLink to="/processos" className="hover:text-ember">
              Processos
            </NavLink>
            <span className="rounded-full bg-white/70 px-3 py-1 text-xs">{user.name}</span>
            <button onClick={logout} className="rounded-full border border-ink px-3 py-1 hover:bg-ink hover:text-sand">
              Sair
            </button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
