"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "../context/UserContext";

export default function HomePage() {
  const router = useRouter();
  const { user } = useUser();

  useEffect(() => {
    if (user) {
      router.push("/recommendations"); // already logged in
    } else {
      router.push("/login");           // not logged in
    }
  }, [user, router]);

  return null; // nothing to render
}