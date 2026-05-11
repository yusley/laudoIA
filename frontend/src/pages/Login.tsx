import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api/auth";
import { Input } from "../components/Input";
import { loginSchema, registerSchema } from "../schemas/auth";
import type { User } from "../types";
import { me } from "../api/auth";

type Props = {
  setUser: (user: User) => void;
};

type LoginForm = { email: string; password: string };
type RegisterForm = { name: string; email: string; password: string };

export function Login({ setUser }: Props) {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
  const registerForm = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  function getApiErrorMessage(error: unknown, fallback: string) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail;
      if (typeof detail === "string" && detail.trim()) {
        return detail;
      }
    }
    if (error instanceof Error && error.message) {
      return error.message;
    }
    return fallback;
  }

  async function handleLogin(values: LoginForm) {
    try {
      setError("");
      const token = await login(values.email, values.password);
      localStorage.setItem("laudoia_token", token.access_token);
      const user = await me();
      setUser(user);
      navigate("/");
    } catch (error) {
      setError(getApiErrorMessage(error, "Nao foi possivel entrar. Verifique suas credenciais."));
    }
  }

  async function handleRegister(values: RegisterForm) {
    try {
      setError("");
      await register(values.name, values.email, values.password);
      await handleLogin({ email: values.email, password: values.password });
    } catch (error) {
      setError(getApiErrorMessage(error, "Nao foi possivel criar sua conta."));
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="grid max-w-5xl gap-6 md:grid-cols-[1.2fr_0.9fr]">
        <div className="rounded-[32px] border border-black/10 bg-ink p-10 text-sand shadow-panel">
          <p className="mb-3 text-sm uppercase tracking-[0.25em] text-brass">Engenharia pericial assistida</p>
          <h1 className="font-display text-5xl leading-tight">Laudos trabalhistas com base documental, quesitos e IA.</h1>
          <p className="mt-5 max-w-xl text-sm text-sand/75">
            Cadastre processos, organize FISPQ, prova emprestada, fotos e gere um laudo técnico estruturado pronto para revisão e exportação.
          </p>
        </div>

        <div className="rounded-[32px] border border-black/10 bg-white/85 p-8 shadow-panel">
          <div className="mb-6 flex gap-2 rounded-full bg-stone-100 p-1">
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`flex-1 rounded-full px-4 py-2 ${mode === "login" ? "bg-ember text-white" : ""}`}
            >
              Entrar
            </button>
            <button
              type="button"
              onClick={() => setMode("register")}
              className={`flex-1 rounded-full px-4 py-2 ${mode === "register" ? "bg-ember text-white" : ""}`}
            >
              Criar conta
            </button>
          </div>

          {mode === "login" ? (
            <form className="space-y-4" onSubmit={loginForm.handleSubmit(handleLogin)}>
              <Input placeholder="E-mail" {...loginForm.register("email")} />
              {loginForm.formState.errors.email && (
                <p className="text-sm text-red-600">{loginForm.formState.errors.email.message}</p>
              )}
              <Input type="password" placeholder="Senha" {...loginForm.register("password")} />
              {loginForm.formState.errors.password && (
                <p className="text-sm text-red-600">{loginForm.formState.errors.password.message}</p>
              )}
              {error && <p className="text-sm text-red-600">{error}</p>}
              <button
                type="submit"
                disabled={loginForm.formState.isSubmitting}
                className="w-full rounded-2xl bg-ink px-4 py-3 text-sand"
              >
                {loginForm.formState.isSubmitting ? "Entrando..." : "Entrar"}
              </button>
            </form>
          ) : (
            <form className="space-y-4" onSubmit={registerForm.handleSubmit(handleRegister)}>
              <Input placeholder="Nome" {...registerForm.register("name")} />
              {registerForm.formState.errors.name && (
                <p className="text-sm text-red-600">{registerForm.formState.errors.name.message}</p>
              )}
              <Input placeholder="E-mail" {...registerForm.register("email")} />
              {registerForm.formState.errors.email && (
                <p className="text-sm text-red-600">{registerForm.formState.errors.email.message}</p>
              )}
              <Input type="password" placeholder="Senha" {...registerForm.register("password")} />
              {registerForm.formState.errors.password && (
                <p className="text-sm text-red-600">{registerForm.formState.errors.password.message}</p>
              )}
              {error && <p className="text-sm text-red-600">{error}</p>}
              <button
                type="submit"
                disabled={registerForm.formState.isSubmitting}
                className="w-full rounded-2xl bg-ember px-4 py-3 text-white"
              >
                {registerForm.formState.isSubmitting ? "Criando..." : "Criar conta"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
