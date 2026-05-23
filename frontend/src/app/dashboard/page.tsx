"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe, UserProfile } from "@/lib/api";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    const token = getCookie("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    getMe(token)
      .then(setUser)
      .catch(() => router.replace("/login"));
  }, [router]);

  function handleLogout() {
    document.cookie = "access_token=; path=/; max-age=0";
    document.cookie = "refresh_token=; path=/; max-age=0";
    router.replace("/login");
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
        Carregando...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <span className="font-bold text-gray-900">Hospitality Research</span>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-gray-900 transition"
        >
          Sair
        </button>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          Bem-vindo, {user.name}!
        </h1>
        <p className="text-gray-500 text-sm mb-8">Seu painel de pesquisa em hospitalidade</p>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-3">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Seu perfil</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">E-mail</span>
              <p className="font-medium text-gray-900">{user.email}</p>
            </div>
            <div>
              <span className="text-gray-500">Instituição</span>
              <p className="font-medium text-gray-900">{user.institution ?? "—"}</p>
            </div>
            <div>
              <span className="text-gray-500">Área de pesquisa</span>
              <p className="font-medium text-gray-900">{user.research_area ?? "—"}</p>
            </div>
            <div>
              <span className="text-gray-500">Membro desde</span>
              <p className="font-medium text-gray-900">
                {new Date(user.created_at).toLocaleDateString("pt-BR")}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
