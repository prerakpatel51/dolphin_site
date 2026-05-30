"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "../src/lib/auth.jsx";
import { queryClient } from "../src/lib/queryClient.js";

export default function Providers({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
