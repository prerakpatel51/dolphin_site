"use client";

import NextLink from "next/link";
import { useParams as useNextParams, usePathname, useRouter, useSearchParams as useNextSearchParams } from "next/navigation";
import { useEffect } from "react";

export function Link({ to, href, children, ...props }) {
  return (
    <NextLink href={href || to || "/"} {...props}>
      {children}
    </NextLink>
  );
}

export function NavLink({ to, href, className, children, ...props }) {
  const pathname = usePathname() || "/";
  const target = href || to || "/";
  const isActive = target === "/" ? pathname === "/" : pathname.startsWith(target);
  const resolvedClassName = typeof className === "function" ? className({ isActive }) : className;

  return (
    <NextLink href={target} className={resolvedClassName} {...props}>
      {children}
    </NextLink>
  );
}

export function useNavigate() {
  const router = useRouter();
  return (to, options = {}) => {
    if (options.replace) router.replace(to);
    else router.push(to);
  };
}

export function useParams() {
  return useNextParams();
}

export function useSearchParams() {
  const params = useNextSearchParams();
  return [params];
}

export function useLocation() {
  const pathname = usePathname() || "/";
  const params = useNextSearchParams();
  const search = params.toString();
  return {
    pathname,
    search: search ? `?${search}` : "",
  };
}

export function Navigate({ to, replace }) {
  const nav = useNavigate();
  useEffect(() => {
    nav(to, { replace });
  }, [nav, replace, to]);
  return null;
}
