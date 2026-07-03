"use client"; // Must be first line

import { usePathname } from "next/navigation";
import Nav from "../components/Nav";

export default function ClientLayoutWrapper({ children }) {
  const pathname = usePathname();

  // Pages where Nav should NOT appear
  const noNavPages = ["/", "/login", "/register"];

  const showNav = !noNavPages.includes(pathname);

  return (
    <>
      {showNav && <Nav />}
      <main>{children}</main>
    </>
  );
}