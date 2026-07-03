// Server component (no "use client" here)
import "../globals.css";
import { UserProvider } from "../context/UserContext";
import ClientLayoutWrapper from "./ClientLayoutWrapper";

export const metadata = {
  title: "Recommender Systems App",
  description: "Personalized news recommendation app",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <UserProvider>
          {/* This wrapper will now decide whether to show the Nav */}
          <ClientLayoutWrapper>{children}</ClientLayoutWrapper>
        </UserProvider>
      </body>
    </html>
  );
}
